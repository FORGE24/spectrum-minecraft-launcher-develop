from setuptools import setup, Extension

module = Extension(
    "spectrum_plugin",
    sources=["spectrum_plugin.c"],
    include_dirs=["."],  # 包含 spectrum_sdk.h
)

setup(
    name="spectrum_plugin",
    version="1.0",
    description="Spectrum Plugin C Extension",
    ext_modules=[module],
)
