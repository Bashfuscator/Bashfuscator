# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2016 Cuckoo Foundation.
"""
Provides helper functions for pretty-printing with colors. This file is
borrowed from the Cuckoo Sandbox Project:
https://github.com/cuckoosandbox/cuckoo
"""
import os
import sys


def color(text, colorCode):
    """
    Colorize input text, on supported terminals.

    :param text: text to color
    :param color_code: color to colorize text
    :return: colorized text
    """
    # $TERM under Windows:
    # cmd.exe -> "" (what would you expect..?)
    # cygwin -> "cygwin" (should support colors, but doesn't work somehow)
    # mintty -> "xterm" (supports colors)
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return f"\x1b[{colorCode}m{text}\x1b[0m"


def black(text):
    """Returns black text on supported terminals."""
    return color(text, 30)


def red(text):
    """Returns red text on supported terminals."""
    return color(text, 31)


def green(text):
    """Returns green text on supported terminals."""
    return color(text, 32)


def yellow(text):
    """Returns yellow text on supported terminals."""
    return color(text, 33)


def blue(text):
    """Returns blue text on supported terminals."""
    return color(text, 34)


def magenta(text):
    """Returns magenta text on supported terminals."""
    return color(text, 35)


def cyan(text):
    """Returns cyan text on supported terminals."""
    return color(text, 36)


def white(text):
    """Returns white text on supported terminals."""
    return color(text, 37)


def bold(text):
    """Returns bold text on supported terminals."""
    return color(text, 1)
