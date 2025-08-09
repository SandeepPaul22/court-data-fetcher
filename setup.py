"""
Setup configuration for Court Data Fetcher
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="court-data-fetcher",
    version="1.0.0",
    author="Court Data Fetcher Team",
    description="A web application for fetching Indian court case data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/court-data-fetcher",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "court-data-fetcher=app:main",
        ],
    },
)
