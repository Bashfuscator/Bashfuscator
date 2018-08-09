import re

from helpers import RandomGen, choosePrefItem
from obfuscator import Obfuscator


class Stub(object):
    """
    This class is in charge of generating a valid deobfuscation stub,
    taking care of properly escaping quotes in the user's input, 
    generating random variable names, and so on. 
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
        if self.escapeQuotes:
            userCmd = userCmd.replace('"', '\\"')

        if sizePref == 1:
            minVarLen = 2
            maxVarLen = 3
        else:
            minVarLen = 6
            maxVarLen = 12
        
        genStub = self.stub
        for var in re.findall(r"VAR\d+", self.stub):
            genStub = self.stub.replace(var, self.randGen.randGenVar(minVarLen, maxVarLen))

        genStub = genStub.replace("CMD", userCmd)

        return "eval $({0})".format(genStub) 


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
    """
    def __init__(self, name, description, sizeRating, timeRating):
        super().__init__(name)
        
        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.stubs = []
        self.deobStub = None
        self.originalCmd = ""
        self.payload = ""

    def chooseStub(self, sizePref, timePref, binaryPref, usrStub):
        if usrStub is not None:
            for stub in self.stubs:
                if stub.long_name == usrStub:
                    self.deobStub = stub
                    return
        
        self.deobStub = choosePrefItem(self.stubs, sizePref, timePref, binaryPref)

    def addEval(self, obCmd):
        return 


class Reverse(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Command Reverser",
            description="Reverses a command",
            sizeRating=1,
            timeRating=1
        )

        self.stubs = [
            Stub(
                name="bash rev",
                binariesUsed="rev",
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""printf "CMD"|rev"""
            ),
            Stub(
                name="perl scalar reverse",
                binariesUsed="perl",
                sizeRating=3,
                timeRating=1,
                escapeQuotes=True,
                stub="""perl -lne 'print scalar reverse "CMD"'"""
            ),
            Stub(
                name="python list reverse",
                binariesUsed="python",
                sizeRating=2,
                timeRating=1,
                escapeQuotes=True,
                stub="""python -c 'print("CMD"[::-1])'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, userCmd, binaryPref=None, usrStub=None):
        self.originalCmd = userCmd
        self.chooseStub(sizePref, timePref, binaryPref, usrStub)
        
        obCmd = self.originalCmd[::-1]
        self.payload = self.deobStub.genStub(sizePref, obCmd)
        
        return self.payload


class CaseSwap(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Case Swapper",
            description="Flips the case of all alpha chars",
            sizeRating=2,
            timeRating=1
        )

        self.stubs = [
            Stub(
                name="bash case swap expansion",
                binariesUsed="bash",
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""VAR1="CMD";${VAR1~~}"""
            ),
            Stub(
                name="python swapcase",
                binariesUsed="python",
                sizeRating=2,
                timeRating=1,
                escapeQuotes=True,
                stub="""python -c 'print("CMD".swapcase())'"""
            )
        ]

    def obfuscate(self, sizePref, timePref, userCmd, binaryPref=None, usrStub=None):
        self.originalCmd = userCmd
        self.chooseStub(sizePref, timePref, binaryPref, usrStub)

        obCmd = self.originalCmd.swapcase()
        self.payload = self.deobStub.genStub(sizePref, obCmd)

        return self.payload
