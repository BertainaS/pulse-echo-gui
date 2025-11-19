#!/usr/bin/env python3
"""
Setup script for PulseEchoGui package.

A standalone GUI package for simulating nuclear magnetic resonance (NMR)
and electron spin resonance (ESR) spin echo pulse sequences.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="pulseechogui",
    version="1.0.0",
    author="Sylvain Bertaina",
    author_email="sylvain.bertaina@cnrs.fr",
    description="GUI applications for NMR/ESR spin echo pulse sequence simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sylvainbertaina/PulseSeq",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "joblib>=1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "isort>=5.10",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pulseechogui-basic=pulseechogui.gui:launch_basic_gui",
            "pulseechogui-basic-single=pulseechogui.gui:launch_basic_gui_single",
            "pulseechogui-shaped=pulseechogui.gui:launch_shaped_pulse_gui",
            "pulseechogui-validate=pulseechogui:validate_installation",
        ],
    },
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/sylvainbertaina/PulseSeq/issues",
        "Source": "https://github.com/sylvainbertaina/PulseSeq",
    },
    keywords=[
        "nmr", "esr", "spin echo", "pulse sequences", "quantum simulation",
        "magnetic resonance", "shaped pulses", "gui", "tkinter",
        "quantum mechanics", "density matrix", "physics simulation"
    ],
    zip_safe=False,
)
