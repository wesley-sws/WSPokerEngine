from setuptools import setup, find_packages

setup(
    name="wspokerengine",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    author="Wesley Sze",
    description="A comprehensive Texas Hold'em poker engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)