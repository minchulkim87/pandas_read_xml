from pathlib import Path
from setuptools import setup
from setuptools import find_packages

version = "0.2.0"
description = "A tool to read XML files as pandas dataframes."

source_root = Path(".")

with (source_root / "README.md").open(encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pandas_read_xml",
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Min Chul Kim",
    author_email="minchulkim87@gmail.com",
    url="https://github.com/minchulkim87/pandas_read_xml",
    py_modules=["pandas_read_xml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyarrow",
        "pandas",
        "xmltodict",
        "requests",
        "zipfile36",
        "distlib",
        "urllib3>=1.26.3",
    ],
)
