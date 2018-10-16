"""
Helper functions used throughout the framework
"""
import string

from bashfuscator.common.random import RandomGen

randGen = RandomGen()

def escapeQuotes(inCmd):
    return inCmd.replace("'", "'\"'\"'")

def getArrayIndexSyntax(arrayVarName, arrayLen, offset, length):
    if randGen.probibility(50):
        offset = -arrayLen + offset

    arrayExpandSymbol = randGen.randSelect(["@", "*"])

    return "${{{0}[{1}]: {2}:{3}}}".format(arrayVarName, arrayExpandSymbol, offset, length)

def getStringIndexSyntax(stringVarName, stringLen, offset, length):
    syntaxChoice = randGen.randChoice(4)

    if syntaxChoice == 0:
        pass

    elif syntaxChoice == 1:
        offset = -stringLen + offset

    elif syntaxChoice == 2:
        offset = -stringLen + offset
        length = offset + 1
    
    else:
        length = -stringLen + offset + 1

    return "${{{0}: {1}:{2}}}".format(stringVarName, offset, length)

def strToArrayElements(inCmd):
    specialChars = string.punctuation + " "
    arrayElementsStr = ""
 
    for char in inCmd:
        if char in specialChars:
            char = "\\" + char

        arrayElementsStr += char + " "

    return arrayElementsStr[:-1]
