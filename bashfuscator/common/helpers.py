"""
Helper functions used throughout the framework
"""

import string

def escapeQuotes(inCmd):
    return inCmd.replace("'", "'\"'\"'")

def strToArrayElements(inCmd):
    # escape all Ascii unprintable chars, as well as all special chars and space chars
    escapeChars = string.punctuation + "".join(chr(i) for i in range(1, 33)) + chr(127)
    arrayElementsStr = "* *"

    for char in inCmd:
        if char in escapeChars:
            char = "\\" + char

        arrayElementsStr += char + "% %"

    return arrayElementsStr[:-3] + "* *"
