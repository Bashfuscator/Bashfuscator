from obfuscator import Obfuscator


class DeobfuscateStub(object):
    def __init__(self, name, sizeRating, speedRating, escapeQuotes, stub):
        self.name = name
        self.sizeRating = sizeRating
        self.speedRating = speedRating
        self.escapeQuotes = escapeQuotes
        self.stub = stub


    def genStub(self, userCmd):
        
        if self.escapeQuotes:
            userCmd = userCmd.replace("\"", '\\"')

        return self.stub.replace("CMD", userCmd)


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
        self.deobStub = None
        self.payload = ""


class CommandReverser(CommandObfuscator):
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
                escapeQuotes=False,
                stub="echo CMD|rev"
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

        self.deobStub = self.randGen.randSelection(self.stubs)

    def obfuscate(self):
        obCmd = self.userCmd[::-1]
        self.payload = self.deobStub.genStub(obCmd)
        
        return self.payload
