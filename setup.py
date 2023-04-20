"""Install packages as defined in this file into the Python environment."""
from setuptools import setup, find_packages

# The version of this tool is based on the following steps:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = {}

setup(
    name="DTGUILib",
    author="Dion Timmer",
    author_email="diontimmernl@gmail.com",
    url="diontimmer.com",
    description="Shortcuts for hijacking libraries to support PySimpleGUI",
    version=VERSION.get("__version__", "0.0.1"),
    py_modules=["DTGUILib"],
    packages=find_packages(where=".", exclude=["tests"]),
    install_requires=[
        "setuptools>=45.0",
        "PySimpleGUI",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Programming Language :: Python",
    ],
)