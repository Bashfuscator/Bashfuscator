"""
Base class for Command Obfuscators used by the framework
"""
import re

from bashfuscator.common.messages import printError
from bashfuscator.core.mutators.mutator import Mutator


class CommandObfuscator(Mutator):
    """
    Base class for all Command Obfuscators. If an obfuscator takes the
    original input, mutates it, and requires a deobfuscation stub to
    execute, then it is a Command Obfuscator.

    :param name: name of the CommandObfuscator
    :type name: str
    :param description: short description of what the CommandObfuscator
        does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how much the
        CommandObfuscator increases the size of the overall payload
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the
        CommandObfuscator increases the execution time of the overall
        payload
    :type timeRating: int
    :param reversible: True if the obfuscator cancels itself out when
        run twice in a row on a command/script, False otherwise
    :type reversible: bool
    :param fileWrite: True if the Command Obfuscator requires
        creating/writing to files, False otherwise
    :type fileWrite: bool
    :param notes: see :class:`bashfuscator.common.objects.Mutator`
    :type notes: str
    :param author: see :class:`bashfuscator.common.objects.Mutator`
    :type author: str
    :param credits: see :class:`bashfuscator.common.objects.Mutator`
    :type credits: str
    """

    def __init__(self, name, description, sizeRating, timeRating, notes=None, author=None, credits=None, evalWrap=True, unreadableOutput=False, reversible=False):
        super().__init__(name, "command", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

        self.reversible = reversible
        self.stubs = []
        self.deobStub = None


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

    def __init__(self, name, sizeRating, timeRating, binariesUsed, fileWrite, escapeQuotes, stub):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.binariesUsed = binariesUsed
        self.fileWrite = fileWrite
        self.escapeQuotes = escapeQuotes
        self.stub = stub

        self.mangler = None
        self.randGen = None

    def genStub(self, userCmd):
        """
        Generate a valid deobfuscation stub and wrap an obfuscated
        command in it.

        :param userCmd: command that need to be wrapped in a
            deobfuscation stub
        :type userCmd: str
        """
        if self.escapeQuotes:
            userCmd = userCmd.replace("'", "'\"'\"'")

        genStub = self.stub
        for var in re.findall(r"VAR\d+", genStub):
            genStub = genStub.replace(var, self.randGen.randGenVar())

        genStub = self.mangler.getMangledLine(genStub)

        if "CMD" not in genStub:
            printError(f"Stub '{self.name}' is improperly formatted: no 'CMD' string found")

        else:
            genStub = genStub.replace("CMD", userCmd)

        return genStub
