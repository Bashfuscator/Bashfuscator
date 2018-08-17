"""

This file contains base classes that other classes inherit from thoughout the framework

"""
import re

from bashfuscator.common.messages import printError
from bashfuscator.common.random import RandomGen


class Mutator(object):
    """
    Base class that all mutators inherit from
    """
    def __init__(self, name, mutatorType, notes, author, credits):
        self.name = name
        self.mutatorType = mutatorType
        self.longName = self.mutatorType + "/" + self.name.replace(" ", "_").lower()
        self.notes = notes
        self.author = author
        self.credits = credits
        self.randGen = RandomGen()


class Stub(object):
    """
    This class is in charge of generating a valid deobfuscation stub,
    taking care of properly escaping quotes in the user's input, 
    generating random variable names, and so on. 

    :param name: name of the Stub
    :param binariesUsed: list of strings containing all the binaries
    used in the stub
    :param sizeRating: rating from 1 to 5 of how much the Stub 
    increases the size of the overall payload
    :param timeRating: rating from 1 to 5 of how much the Stub 
    increases the execution time of the overall payload
    :param escapeQuotes: True if the stub requires any quotes in the 
    original command to be escaped, False otherwise
    :param stub: string containing the actual stub
    """
    def __init__(self, name, binariesUsed, sizeRating, timeRating, escapeQuotes, stub):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.binariesUsed = binariesUsed
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.escapeQuotes = escapeQuotes
        self.stub = stub
        self.randGen = RandomGen()

    def genStub(self, sizePref, userCmd):
        cmplxCmd = type(userCmd) == list

        if self.escapeQuotes:
            if cmplxCmd:
                for idx, cmd in enumerate(userCmd):
                    userCmd[idx] = cmd.replace("'", "'\"'\"'")
            else:
                userCmd = userCmd.replace("'", "'\"'\"'")
        
        genStub = self.stub
        for var in re.findall(r"VAR\d+", genStub):
            genStub = genStub.replace(var, self.randGen.randGenVar(sizePref))

        if cmplxCmd:
            cmdMatches = re.findall(r"CMD\d+", genStub)
            if cmdMatches is not None:
                for idx, cmd in enumerate(cmdMatches):
                    genStub = genStub.replace(cmd, userCmd[idx])
            else:
                printError("Stub '{0}' is improperly formatted: no 'CMD' string found".format(self.stub.name))
        
        else:
            genStub = genStub.replace("CMD", userCmd)

        return genStub
