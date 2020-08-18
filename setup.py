from pathlib import Path
from setuptools import setup
from setuptools import find_packages

version = "0.0.5"
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
        "certifi>=2020.4.5.1,<2021",
        "chardet>=3.0.4,<4",
        "idna>=2.9,<3",
        "numpy>=1.18.4,<2",
        "pandas>=1.0.3,<2",
        "pyarrow>=0.17.0,<1",
        "python-dateutil>=2.8.1,<3",
        "pytz>=2020.1,<2021",
        "requests>=2.23.0,<3",
        "six>=1.14.0,<2",
        "urllib3>=1.25.9,<2",
        "xmltodict>=0.12.0,<1",
    ],
)
