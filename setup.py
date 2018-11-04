"""
Get dependencies, install bashfuscator to PATH and enable auto-completion
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import call, Popen, PIPE
from sys import exit
import os


def findArgcompletePath(command):
    proc = Popen("which " + command, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    command1Path, __ = proc.communicate()

    proc = Popen("which " + command + "3", stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    command2Path, __ = proc.communicate()

    if command1Path:
        finalCommandPath = command1Path
    elif command2Path:
        finalCommandPath = command2Path
    else:
        print("ERROR: python3-argcomplete is not installed, install it with your package manager to activate autocompletion")
        exit(1)

    return finalCommandPath[:-1]


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

    if "bashfuscator" not in bashrcContent:
        print("\nRegistering bashfuscator in .bashrc for auto-completion ...")

        proc = call(findArgcompletePath("activate-global-python-argcomplete") + " --user", shell=True)

        argcompleteComment = "# Enables autocompletion of options for bashfuscator"
        with open(bashrcFile, "a") as f:
            f.write("\n\n{0}\n".format(argcompleteComment))
            f.write('eval "$({0})"\n'.format(findArgcompletePath("register-python-argcomplete") + " bashfuscator"))

        print("Auto-completion has been installed.")
        proc = call("source " + bashrcFile, executable="/bin/bash", shell=True)

else:
    print("ERROR: could not find your .bashrc file, autocompletion will not enabled")
