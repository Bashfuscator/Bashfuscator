"""
Get dependencies, install bashfuscator to PATH and enable auto-completion
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import Popen, PIPE
import os


with open("README.md") as f:
    longDescription = f.read()

setup(
    name="bashfuscator",
    version="0.0.1",
    description="Configurable and extendable Bash obfuscation framework",
    license="MIT",
    long_description=longDescription,
    author="Andrew LeFevre",
    packages=find_packages(),
    scripts=["bashfuscator/bin/bashfuscator"],
    install_requires=[
        "argcomplete",
        "pyperclip",
		"plotly",
    ],
    extras_require={
        "dev": [
            "pytest",
        ]
    }
)

# activate autocompletion for bashfuscator
bashrcFile = os.environ["HOME"] + os.sep + ".bashrc"

if os.path.exists(bashrcFile):
    with open(bashrcFile, "r") as f:
        bashrcContent = f.read()

    if '_python_argcomplete "bashfuscator"' not in bashrcContent:
        print("\nRegistering bashfuscator in .bashrc for auto-completion ...")
        proc = Popen("activate-global-python-argcomplete3 --user", shell=True)
        proc.wait()

        # this will write the configuration needed in .bashrc file
        proc = Popen("register-python-argcomplete3 bashfuscator", stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        autoCompleteData, __ = proc.communicate()

        with open(bashrcFile, "a") as f:
            f.write("\n{0}\n".format(autoCompleteData))

        print("Auto-completion has been installed.")
        proc = Popen(". ~/.bashrc", shell=True)
        proc.wait()

else:
    print("ERROR: could not find your .bashrc file, autocompletion will not enabled")
