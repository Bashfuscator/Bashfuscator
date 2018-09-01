"""
Command Obfuscators used by the framework.
"""
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

    def __init__(self, name, description, sizeRating, timeRating, reversible, fileWrite=False, notes=None, author=None, credits=None):
        super().__init__(name, "command", notes, author, credits)

        self.description = description
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
                binariesUsed=["bash"],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub='''VAR1='CMD';printf -- "${VAR1~~}"'''
            ),
            Stub(
                name="python swapcase",
                binariesUsed=["python"],
                sizeRating=2,
                timeRating=1,
                escapeQuotes=True,
                stub="""python -c 'print('"'''"'CMD'"'''"'.swapcase())'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = self.originalCmd.swapcase()
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload


class ForCode(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="ForCode",
            description="Shuffle command and reassemble it in a for loop",
            sizeRating=3,
            timeRating=2,
            reversible=False,
            author="capnspacehook",
            credits="danielbohannon, https://github.com/danielbohannon/Invoke-DOSfuscation"
        )

        self.stubs = [
            Stub(
                name="python for loop",
                binariesUsed=["python"],
                sizeRating=3,
                timeRating=2,
                escapeQuotes=True,
                stub="""python -c 'VAR1="CMD1";print("".join([VAR1[int(VAR2)] for VAR2 in "CMD2".split(",")]))'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        shuffledCmd = list(set(userCmd))
        self.randGen.randShuffle(shuffledCmd)
        shuffledCmd = "".join(shuffledCmd)

        ogCmdIdxes = []
        for char in userCmd:
            ogCmdIdxes.append(shuffledCmd.find(char))

        obCmd = [shuffledCmd, "".join([str(i) + "," for i in ogCmdIdxes])[:-1]]

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
                name="bash rev",
                binariesUsed=["rev"],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""printf "CMD"|rev"""
            ),
            Stub(
                name="perl scalar reverse",
                binariesUsed=["perl"],
                sizeRating=3,
                timeRating=1,
                escapeQuotes=True,
                stub="""perl -e 'print scalar reverse "CMD"'"""
            ),
            Stub(
                name="python list reverse",
                binariesUsed=["python"],
                sizeRating=2,
                timeRating=1,
                escapeQuotes=True,
                stub="""python -c 'print("CMD"[::-1])'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = self.originalCmd[::-1]
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload
