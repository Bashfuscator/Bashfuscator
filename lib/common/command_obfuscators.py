from helpers import RandomGen
from obfuscator import Obfuscator

import re


class DeobfuscateStub(object):
    def __init__(self, name, sizeRating, speedRating, escapeQuotes, stub):
        self.name = name
        self.sizeRating = sizeRating
        self.speedRating = speedRating
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
        for var in re.findall("VAR\d+", self.stub):
            genStub = self.stub.replace(var, self.randGen.randGenVar(minVarLen, maxVarLen))

        return genStub.replace("CMD", userCmd)


class CommandObfuscator(Obfuscator):
    def __init__(self, name, description, sizeRating, speedRating, sizePref, speedPref, userCmd):
        super().__init__()
        
        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.speedRating = speedRating
        self.sizePref = sizePref
        self.speedPref = speedPref 
        self.userCmd = userCmd
        self.stubs = []
        self.deobStub = None
        self.payload = ""


    def chooseStub(self):
        maxSize = self.sizePref + 2
        maxSpeed = self.speedPref + 2

        selectedStubs = [stub for stub in self.stubs if stub.sizeRating <= maxSize and stub.speedRating <= maxSpeed]
        self.deobStub = self.randGen.randSelection(selectedStubs)


class Reverse(CommandObfuscator):
    def __init__(self, sizePref, speedPref, userCmd):
        super().__init__(
            name="Command Reverser",
            description="Reverses a command",
            sizeRating=1,
            speedRating=1,
            sizePref=sizePref,
            speedPref=speedPref,
            userCmd=userCmd)

        self.stubs = [
            DeobfuscateStub(
                name="rev",
                sizeRating=1,
                speedRating=1,
                escapeQuotes=True,
                stub="""printf "CMD"|rev"""
            ),
            DeobfuscateStub(
                name="perl scalar reverse",
                sizeRating=3,
                speedRating=1,
                escapeQuotes=True,
                stub="""perl -lne 'print scalar reverse "CMD"'"""
            ),
            DeobfuscateStub(
                name="python list reverse",
                sizeRating=2,
                speedRating=1,
                escapeQuotes=True,
                stub="""python -c 'print("CMD"[::-1])'"""
            )
        ]

        self.chooseStub()

    def obfuscate(self):
        obCmd = self.userCmd[::-1]
        self.payload = self.deobStub.genStub(self.sizePref, obCmd)
        
        return self.payload


class CaseSwap(CommandObfuscator):
    def __init__(self, sizePref, speedPref, userCmd):
        super().__init__(
            name="Case Swapper",
            description="Flips the case of all alpha chars",
            sizeRating=2,
            speedRating=1,
            sizePref=sizePref,
            speedPref=speedPref,
            userCmd=userCmd
        )

        self.stubs = [
            DeobfuscateStub(
                name="bash case swap expansion",
                sizeRating=2,
                speedRating=1,
                escapeQuotes=True,
                stub="""VAR1="CMD";${VAR1~~}"""
            )
        ]

        self.chooseStub()
    
    def obfuscate(self):
        obCmd = self.userCmd.swapcase()
        self.payload = self.deobStub.genStub(self.sizePref, obCmd)

        return self.payload
