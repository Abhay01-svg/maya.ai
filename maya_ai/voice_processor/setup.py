"""
Setup script for Maya AI Voice Processor
Compiles C-based wake word detector for maximum performance
"""

from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'wake_word_detector',
        ['wake_word_detector.c'],
        include_dirs=[pybind11.get_include()],
        extra_compile_args=['-O3', '-ffast-math', '-march=native'],
        language='c'
    ),
]

setup(
    name='maya_voice_processor',
    version='1.0.0',
    description='High-performance voice processing for Maya AI',
    ext_modules=ext_modules,
    zip_safe=False,
)
