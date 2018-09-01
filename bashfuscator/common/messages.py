"""
Helper functions to print output to the terminal.
"""
from sys import exit

from bashfuscator.common.colors import blue, yellow, red, bold


QUIET_OUTPUT = False


def activateQuietMode():
    """Activate quiet mode, only print errors."""
    global QUIET_OUTPUT
    QUIET_OUTPUT = True


def printInfo(msg):
    """Format and print informational messages to the terminal."""
    if not QUIET_OUTPUT:
        print("[{0}] {1}".format(blue("+"), msg))


def printWarning(msg):
    """Format and print warning messages to the terminal."""
    if not QUIET_OUTPUT:
        print(yellow("[!] {0}".format(msg)))


def printError(msg):
    """Format and print error messages to the terminal."""
    print(bold(red("[ERROR] {0}".format(msg))))
    exit(1)
