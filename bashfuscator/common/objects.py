"""
Base classes used throughout the framework.
"""
import re

from bashfuscator.common.helpers import escapeQuotes
from bashfuscator.common.messages import printError
from bashfuscator.common.random import RandomGen
from bashfuscator.core.mangler import Mangler


class Mutator(object):
    """
    Base class that all Mutators inherit from. Automatically generates
    a longName attribute that is used to choose Mutators on the
    command line, and stores a
    :class:`bashfuscator.common.random.RandomGen` object.

    :param name: Name of the Mutator
    :type name: str
    :param mutatorType: child Mutator's type
    :type mutatorType: lowercase str
    :param notes: any additional information useful to know when using
        the Mutator
    :type notes: str
    :param author: creator of the Mutator
    :type author: str
    :param credits: whom or where inpiration for or the complete method
        of mutation was found at. Should be the name/handle of the
        person who inspired you, and/or a link to where you got the
        idea from. See
        :class:`bashfuscator.lib.token_obfuscators.AnsiCQuote` for an
        example
    :type credits: str
    """

    def __init__(self, name, mutatorType, description, notes, author, credits, evalWrap):
        self.name = name
        self.mutatorType = mutatorType
        self.description = description
        self.longName = self.mutatorType + "/" + self.name.replace(" ", "_").lower()
        self.notes = notes
        self.author = author
        self.credits = credits
        self.evalWrap = evalWrap

        self._originalCmd = ""
        self._obfuscatedCmd = ""

        self.randGen = RandomGen()
        self.mangler = Mangler()


class Stub(object):
    """
    This class is in charge of generating a valid deobfuscation stub,
    taking care of properly escaping quotes in the user's input,
    generating random variable names, and so on.

    :param name: name of the Stub
    :param binariesUsed: all the binaries
        used in the stub
    :type binariesUsed: list of strs
    :param sizeRating: rating from 1 to 5 of how much the Stub
        increases the size of the overall payload
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the Stub
        increases the execution time of the overall payload
    :type timeRating: int
    :param escapeQuotes: True if the stub requires any quotes in the
        original command to be escaped, False otherwise
    :type escapeQuotes: int
    :param stub: string containing the actual stub
    :type stub: str
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
        """
        Generate a valid deobfuscation stub and wrap an obfuscated
        command in it.

        :param sizePref: sizePref user option
        :type sizePref: int
        :param userCmd: command(s) that need to be wrapped in a
            deobfuscation stub
        :type userCmd: str or list of strs
        """
        cmplxCmd = type(userCmd) == list

        if self.escapeQuotes:
            if cmplxCmd:
                for idx, cmd in enumerate(userCmd):
                    userCmd[idx] = escapeQuotes(cmd)
            else:
                userCmd = escapeQuotes(userCmd)

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
