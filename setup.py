from setuptools import setup, find_packages

with open("README.md") as f:
    longDescription = f.read()

setup(
    name="bashfuscator",
    description="Bash obfuscator",
    license="MIT",
    long_description=longDescription,
    author="Andrew LeFevre",
    packages=find_packages(),
    scripts=["bashfuscator/bin/bashfuscator"],
    install_requires=[
        "argcomplete",
        "pyperclip"
    ],
)