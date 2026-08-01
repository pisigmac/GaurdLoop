from setuptools import setup, find_packages

setup(
    name="guardloop-sdk",
    version="1.0.0",
    description="GuardLoop Python SDK — Agent Trust & Orchestration Layer",
    author="GuardLoop",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
