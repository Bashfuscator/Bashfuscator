"""
Helper functions to print output to the terminal.
"""
import sys

from bashfuscator.common.colors import blue, yellow, red, bold


QUIET_OUTPUT = False


def activateQuietMode():
    """Activate quiet mode, only print errors."""
    global QUIET_OUTPUT
    QUIET_OUTPUT = True


def printInfo(msg):
    """Format and print informational messages to the terminal."""
    if not QUIET_OUTPUT:
        print(f'[{blue("+")}] {msg}')


def printWarning(msg):
    """Format and print warning messages to the terminal."""
    if not QUIET_OUTPUT:
        print(yellow(f"[!] {msg}"))


def printError(msg):
    """Format and print error messages to the terminal."""
    print(bold(red(f"[ERROR] {msg}")))
    sys.exit(1)


def printExitMsg(msg):
    """Format and print exit messages to the terminal."""
    if not QUIET_OUTPUT:
        print(bold(red(msg)))

    sys.exit(1)
