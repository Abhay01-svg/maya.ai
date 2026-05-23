from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string
import os
from download_sd import generate

app = Flask(__name__)

OUT_DIR = os.path.abspath("outputs")
os.makedirs(OUT_DIR, exist_ok=True)

INDEX_HTML = '''
<!doctype html>
<title>SD Verify UI</title>
<h1>Stable Diffusion Verify</h1>
<form method=post action="/generate">
  <label>Prompt: <input name=prompt size=80 required></label><br><br>
  <label>Width: <input name=width value=256></label>
    <label>Height: <input name=height value=512></label><br><br>
    <label>Steps: <input name=steps value=50></label>
    <label>Guidance: <input name=guidance value=7.5 step=0.1></label><br><br>
    <label>Seed (optional): <input name=seed></label>
    <label>Upscale: <input type=checkbox name=upscale></label>
    <label>High quality (generate at 2x then downscale): <input type=checkbox name=high_quality></label><br><br>
  <button type=submit>Generate</button>
</form>
{% if img_url %}
  <h2>Result</h2>
  <img src="{{ img_url }}" style="max-width:90%;height:auto;"/>
  <p><a href="{{ img_url }}" target="_blank">Open image</a></p>
{% endif %}
<p>Note: CPU inference may be slow on this machine.</p>
'''


@app.route('/')
def index():
    return render_template_string(INDEX_HTML, img_url=None)


@app.route('/generate', methods=['POST'])
def do_generate():
    prompt = request.form.get('prompt')
    width = int(request.form.get('width') or 512)
    height = int(request.form.get('height') or 512)
    steps = int(request.form.get('steps') or 50)
    guidance = float(request.form.get('guidance') or 7.5)
    seed = request.form.get('seed')
    seed = int(seed) if seed else None
    upscale = True if request.form.get('upscale') else False
    high_quality = True if request.form.get('high_quality') else False

    safe_name = "sd_out.png"
    out_path = os.path.join(OUT_DIR, safe_name)

    # Call the existing generate() function from download_sd.py
    try:
        generate(prompt=prompt, out_path=out_path, steps=steps, guidance=guidance, height=height, width=width, seed=seed, upscale=upscale, high_quality=high_quality)
    except Exception as e:
        return f"Generation failed: {e}", 500

    img_url = url_for('static_output', filename=safe_name)
    return render_template_string(INDEX_HTML, img_url=img_url)


@app.route('/outputs/<path:filename>')
def static_output(filename):
    return send_from_directory(OUT_DIR, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
