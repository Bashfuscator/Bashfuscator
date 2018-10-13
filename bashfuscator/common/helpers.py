"""
Helper functions used throughout the framework
"""

import string

def escapeQuotes(inCmd):
    return inCmd.replace("'", "'\"'\"'")

def strToArrayElements(inCmd):
    specialChars = string.punctuation + " "
    arrayElementsStr = ""
    
    for char in inCmd:
        if char in specialChars:
            char = "\\" + char

        arrayElementsStr += char + " "

    return arrayElementsStr[:-1]
