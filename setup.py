# -*- coding: utf-8 -*-
"""
Financial AI Skills - Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="financial-ai-skills",
    version="1.0.0",
    author="Financial AI Contributors (Yu Zhaopeng)",
    author_email="",
    description="AI Agent Skills for Financial Institutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuzhaopeng-up/financial-ai-skills",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dateutil>=2.8.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "requests>=2.25.0",
    ],
)
