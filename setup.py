#!/usr/bin/env python
"""Setup script for Plex Renamer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plex-renamer",
    version="1.1.0",
    author="Plex Renamer Contributors",
    description="Professional tool for organizing TV shows in Plex-perfect format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/plex-renamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "rich>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "plex-renamer=plex_renamer:main",
        ],
    },
)
