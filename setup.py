"""

Install bashfuscator to PATH and enable auto-completion. Auto-completion activation code
borrowed from https://github.com/0x00-0x00/Shellpop

"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import Popen, PIPE
import os


def applyChanges():
    proc = Popen("source ~/.bashrc", stdout=PIPE, stderr=PIPE, shell=True)
    __, __ = proc.communicate()
    return None


def activateTabComplete():
    proc = Popen("activate-global-python-argcomplete3", stdout=PIPE, stderr=PIPE, shell=True)
    __, __ = proc.communicate()
    return True if proc.poll() is 0 else False


def autoComplete():
    proc = Popen("register-python-argcomplete3 bashfuscator", stdout=PIPE, stderr=PIPE, shell=True)
    stdout, __ = proc.communicate()
    return stdout


class CustomInstall(install):
    def run(self):
        install.run(self)
        bashrc_file = os.environ["HOME"] + os.sep + ".bashrc"
        if not os.path.exists(bashrc_file):
            return None
        with open(bashrc_file, "r") as f:
            bashrc_content = f.read()
        if "bashfuscator" not in bashrc_content:
            print("Registering bashfuscator in .bashrc for auto-completion ...")
            activateTabComplete() # this will enable auto-complete feature.

            # This will write the configuration needed in .bashrc file
            with open(bashrc_file, "a") as f:
                f.write("\n{0}\n".format(autoComplete()))
            print("Auto-completion has been installed.")
            applyChanges()


with open("README.md") as f:
    longDescription = f.read()

setup(
    name="bashfuscator",
    version="0.0.1",
    description="Configurable and extendable bash obfuscator",
    license="MIT",
    long_description=longDescription,
    author="Andrew LeFevre",
    packages=find_packages(),
    scripts=["bashfuscator/bin/bashfuscator"],
    install_requires=[
        "argcomplete",
        "pyperclip"
    ],
    cmdclass={"install":CustomInstall}
)
