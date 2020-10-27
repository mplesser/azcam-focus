from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="azcam-focus",
    version="20.1",
    description="azcam plugin for focus control",
    long_description=long_description,
    author="Michael Lesser",
    author_email="mlesser@arizona.edu",
    keywords="python parameters",
    packages=find_packages(),
    zip_safe=False,
    install_requires=["azcam"],
)
