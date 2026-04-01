from setuptools import setup, find_packages

setup(
    name="stem-voice-clone",
    version="0.1.0",
    description="Multi-stem singing voice cloning toolkit",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={"console_scripts": ["stem-voice-clone=src.cli:main"]},
)
