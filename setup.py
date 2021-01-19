# from setuptools import find_packages, setup
from setuptools import setup, find_packages, Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="azcam-focus",
    version="21.1.3",
    description="azcam extension for focus control",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="Michael Lesser",
    author_email="mlesser@arizona.edu",
    keywords="python parameters",
    packages=find_packages(),
    zip_safe=False,
    install_requires=["azcam"],
)
