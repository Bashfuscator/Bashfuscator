from bashfuscator.common.obfuscator import Obfuscator, Stub


class CommandObfuscator(Obfuscator):
    """
    Base class for all command obfuscators. If an obfuscator requires
    a deobfuscation stub to execute, then it is a command obfuscator.
    
    :param name: name of the CommandObfuscator
    :param description: short description of what the CommandObfuscator does
    :param sizeRating: rating from 1 to 5 of how much the CommandObfuscator 
    increases the size of the overall payload
    :param timeRating: rating from 1 to 5 of how much the CommandObfuscator 
    increases the execution time of the overall payload
    :param reversable: True if the obfuscator cancels itself out when run
    twice in a row on a command/script
    """
    def __init__(self, name, description, sizeRating, timeRating, reversible):
        super().__init__(name)
        
        self.name = name
        self.longName = "command/" + self.longName
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.reversible = reversible
        self.stubs = []
        self.deobStub = None
        self.originalCmd = ""
        self.payload = ""


class Reverse(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Reverse",
            description="Reverses a command",
            sizeRating=1,
            timeRating=1,
            reversible=True
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
                stub="""perl -lne 'print scalar reverse "CMD"'"""
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

    def obfuscate(self, sizePref, timePref, binaryPref, userCmd, usrStub=None):
        self.originalCmd = userCmd
        
        obCmd = self.originalCmd[::-1]
        self.payload = self.deobStub.genStub(sizePref, obCmd)
        
        return self.payload


class CaseSwap(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Case Swapper",
            description="Flips the case of all alpha chars",
            sizeRating=2,
            timeRating=1,
            reversible=True
        )

        self.stubs = [
            Stub(
                name="bash case swap expansion",
                binariesUsed=["bash"],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""VAR1="CMD";${VAR1~~}"""
            ),
            Stub(
                name="python swapcase",
                binariesUsed=["python"],
                sizeRating=2,
                timeRating=1,
                escapeQuotes=True,
                stub="""python -c 'print("CMD".swapcase())'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, binaryPref, userCmd, usrStub=None):
        self.originalCmd = userCmd

        obCmd = self.originalCmd.swapcase()
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload
