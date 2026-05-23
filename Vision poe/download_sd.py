import argparse
import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import shutil
import subprocess
import sys

"""download_sd.py
Simple script to load Stable Diffusion 1.5 and generate images.
Supports CUDA when available and an optional upscaling path (uses diffusers upscaler
if present, otherwise falls back to PIL Lanczos resize).
"""

MODEL_ID = "runwayml/stable-diffusion-v1-5"


def get_device_and_dtype():
	if torch.cuda.is_available():
		return "cuda", torch.float16
	return "cpu", torch.float32


def load_sd_pipeline(device, torch_dtype):
	print(f"Loading Stable Diffusion {MODEL_ID} on {device} (dtype={torch_dtype})...")
	pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch_dtype)
	pipe.to(device)
	pipe.enable_attention_slicing()
	if device == "cuda":
		try:
			pipe.enable_xformers_memory_efficient_attention()
		except Exception:
			pass
	return pipe


def try_load_upscaler(device, torch_dtype):
	try:
		from diffusers import StableDiffusionUpscalePipeline

		print("Attempting to load stabilityai/stable-diffusion-x4-upscaler...")
		upscaler = StableDiffusionUpscalePipeline.from_pretrained(
			"stabilityai/stable-diffusion-x4-upscaler", torch_dtype=torch_dtype
		)
		upscaler.to(device)
		return upscaler
	except Exception:
		return None


def generate(prompt: str, out_path: str, steps: int, guidance: float, height: int, width: int, seed: int, upscale: bool, high_quality: bool=False):
	# If a C++ backend binary is available, prefer calling it for low-latency runs.
	sd_cpp = os.environ.get('SD_CPP_BIN')
	if sd_cpp and shutil.which(sd_cpp):
		cmd = [sd_cpp, '--prompt', prompt, '--out', out_path, '--width', str(width), '--height', str(height), '--steps', str(steps), '--guidance', str(guidance)]
		if seed is not None:
			cmd += ['--seed', str(seed)]
		if upscale:
			cmd += ['--upscale']
		print(f"Using C++ backend: {' '.join(cmd)}")
		try:
			subprocess.check_call(cmd)
			print(f"Saved -> {out_path} (via C++ backend)")
			return
		except subprocess.CalledProcessError as e:
			print(f"C++ backend failed (exit {e.returncode}), falling back to Python pipeline.")
		except FileNotFoundError:
			print("C++ backend binary not found, falling back to Python pipeline.")

	device, torch_dtype = get_device_and_dtype()
	pipe = load_sd_pipeline(device, torch_dtype)

	upscaler = None
	if upscale:
		upscaler = try_load_upscaler(device, torch_dtype)
		if upscaler is None:
			print("Upscaler model not available locally — will use image resize fallback.")

	# Prefer DPMSolverMultistep scheduler for improved quality/speed when available
	try:
		pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
	except Exception:
		pass

	generator = None
	if seed is not None:
		try:
			gen_device = torch.device(device)
			generator = torch.Generator(device=gen_device).manual_seed(seed)
		except Exception:
			generator = torch.Generator().manual_seed(seed)

	gen_width, gen_height = (width * 2, height * 2) if high_quality else (width, height)
	print(f"Generating image for prompt: '{prompt}' (gen_size={gen_width}x{gen_height})...")
	result = pipe(
		prompt,
		height=gen_height,
		width=gen_width,
		guidance_scale=guidance,
		num_inference_steps=steps,
		generator=generator,
	)
	image = result.images[0]

	# If we rendered at higher resolution for quality, downscale back to target
	if high_quality and (gen_width != width or gen_height != height):
		try:
			image = image.resize((width, height), resample=Image.LANCZOS)
			print(f"Downscaled from {gen_width}x{gen_height} to {width}x{height}")
		except Exception:
			print("Downscale failed — keeping original generated size.")

	if upscale:
		if upscaler is not None:
			try:
				print("Running neural upscaler (x4)...")
				up_res = upscaler(prompt=prompt, image=image, num_inference_steps=20)
				image = up_res.images[0]
			except Exception:
				print("Neural upscaler failed — falling back to PIL resize.")
				image = image.resize((width * 2, height * 2), resample=Image.LANCZOS)
		else:
			image = image.resize((width * 2, height * 2), resample=Image.LANCZOS)

	os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
	image.save(out_path)
	print(f"Saved -> {out_path}")


def main():
	parser = argparse.ArgumentParser(description="Generate images with Stable Diffusion 1.5")
	parser.add_argument("--prompt", "-p", required=True, help="Text prompt (put in quotes)")
	parser.add_argument("--out", "-o", default="output.png", help="Output filename")
	parser.add_argument("--steps", type=int, default=30, help="Inference steps")
	parser.add_argument("--guidance", type=float, default=7.5, help="Guidance scale")
	parser.add_argument("--width", type=int, default=512, help="Image width (must be divisible by 8)")
	parser.add_argument("--height", type=int, default=512, help="Image height (must be divisible by 8)")
	parser.add_argument("--seed", type=int, default=None, help="Random seed (int)")
	parser.add_argument("--upscale", action="store_true", help="Attempt neural upscaling (requires upscaler model) or fallback to PIL resize")
	parser.add_argument("--high-quality", dest='high_quality', action="store_true", help="Generate at 2x resolution then downscale for higher detail")

	args = parser.parse_args()

	generate(
		prompt=args.prompt,
		out_path=args.out,
		steps=args.steps,
		guidance=args.guidance,
		height=args.height,
		width=args.width,
		seed=args.seed,
		upscale=args.upscale,
		high_quality=args.high_quality,
	)


if __name__ == "__main__":
	main()
