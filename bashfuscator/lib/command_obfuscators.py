"""
Command Obfuscators used by the framework.
"""
import re

from bashfuscator.common.helpers import escapeQuotes
from bashfuscator.common.messages import printError
from bashfuscator.common.objects import Mutator


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

    def __init__(self, name, description, sizeRating, timeRating, reversible, fileWrite=False, notes=None, author=None, credits=None, evalWrap=True):
        super().__init__(name, "command", description, notes, author, credits, evalWrap)

        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.reversible = reversible
        self.fileWrite = fileWrite
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

    def __init__(self, name, binariesUsed, sizeRating, timeRating, escapeQuotes, stub):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.binariesUsed = binariesUsed
        self.sizeRating = sizeRating
        self.timeRating = timeRating
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
            userCmd = escapeQuotes(userCmd)

        genStub = self.stub
        for var in re.findall(r"VAR\d+", genStub):
            genStub = genStub.replace(var, self.randGen.randGenVar())

        genStub = self.mangler.getMangledLine(genStub)

        if "CMD" not in genStub:
            printError("Stub '{0}' is improperly formatted: no 'CMD' string found".format(self.name))

        else:
            genStub = genStub.replace("CMD", userCmd)

        return genStub


class CaseSwap(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Case Swapper",
            description="Flips the case of all alpha chars",
            sizeRating=1,
            timeRating=1,
            reversible=True,
            author="capnspacehook"
        )

        self.stubs = [
            Stub(
                name="bash case swap expansion",
                binariesUsed=[],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub='''? ?VAR1='CMD'* *END* *:printf:^ ^%s^ ^"${VAR1~~}"* *END* *'''
            )
        ]

    def mutate(self, userCmd):
        obCmd = userCmd.swapcase()

        return self.deobStub.genStub(obCmd)


class Reverse(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Reverse",
            description="Reverses a command",
            sizeRating=1,
            timeRating=1,
            reversible=True,
            author="capnspacehook"
        )

        self.stubs = [
            Stub(
                name="printf rev",
                binariesUsed=["rev"],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""* *:printf:^ ^%s^ ^'CMD'* *|* *:rev:* *END* *"""
            ),
            Stub(
                name="herestring rev",
                binariesUsed=["rev"],
                sizeRating=3,
                timeRating=1,
                escapeQuotes=True,
                stub="""* *:rev:^ ^<<<? ?'CMD'* *END* *"""
            )
        ]

    def mutate(self, userCmd):
        obCmd = userCmd[::-1]
        
        return self.deobStub.genStub(obCmd)
