import math

from bashfuscator.core.mutators.string_obfuscator import StringObfuscator


class GlobObfuscator(StringObfuscator):
    def __init__(self, name, description, sizeRating, timeRating, author):
        super().__init__(
            name=name,
            description=description,
            sizeRating=sizeRating,
            timeRating=timeRating,
            binariesUsed=["cat", "mkdir", "rm", "rmdir"],
            fileWrite=True,
            author=author
        )

        self.workingDir = None
        self.minDirLen = None
        self.maxDirLen = None
        self.sectionSize = None

    def generate(self, userCmd, writeableDir=None):
        if writeableDir:
            self.workingDir = self.startingDir + "/" + self.escapeQuotes(writeableDir)
        else:
            self.workingDir = self.startingDir

        cmdChars = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
        cmdLen = len(cmdChars)
        cmdLogLen = int(math.ceil(math.log(cmdLen, 2)))
        if cmdLogLen <= 0:
            cmdLogLen = 1

        printLines = {}
        for i in range(cmdLen):
            cmdCharsSection = cmdChars[i]
            cmdCharsSection = self.escapeQuotes(cmdCharsSection)
            printLines.update({
                f"* *:printf:^ ^%s^ ^'DATA'? ?>? ?'{self.workingDir}/" +
                format(i, "0" + str(cmdLogLen) + "b").replace("0", "?").replace("1", "\n") + "'* *END0": cmdCharsSection
            })

        # TODO: randomize ordering of 'rm' statements
        self.mangler.addPayloadLine(f"* *:mkdir:^ ^-p^ ^'{self.workingDir}'* *END0")
        self.mangler.addLinesInRandomOrder(printLines)
        self.mangler.addPayloadLine(f"* *:cat:^ ^'{self.workingDir}'/{'?' * cmdLogLen}* *END0")
        self.mangler.addPayloadLine(f"* *:rm:^ ^'{self.workingDir}'/{'?' * cmdLogLen}* *END0")

    def setSizes(self, userCmd):
        if self.sizePref == 1:
            self.sectionSize = int(len(userCmd) / 10 + 1)
        elif self.sizePref == 2:
            self.sectionSize = int(len(userCmd) / 100 + 1)
        elif self.sizePref == 3:
            self.sectionSize = 1

        self.startingDir = self.escapeQuotes(self.writeDir + self.randGen.randUniqueStr())
