"""
Command Obfuscators used by the framework.
"""
from bashfuscator.common.helpers import strToArrayElements
from bashfuscator.common.objects import Mutator, Stub


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
        self.originalCmd = ""
        self.payload = ""


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
                stub='''VAR1='CMD';printf %s "${VAR1~~}"'''
            )
        ]

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = self.originalCmd.swapcase()
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload


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
                stub="""printf %s 'CMD'|rev"""
            ),
            Stub(
                name="herestring rev",
                binariesUsed=["rev"],
                sizeRating=3,
                timeRating=1,
                escapeQuotes=True,
                stub="""rev <<<'CMD'"""
            )
        ]

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = self.originalCmd[::-1]
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload
