import re

from bashfuscator.common.random import RandomGen


class Mangler(object):
    binaryRegexStr = r":\w+:"
    requiredWhitespaceRegexStr = r"\^ \^"
    optionalWhitespaceRegexStr = r"\? \?"
    requiredWhitespaceAndRandCharsRegexStr = "% %"
    optionalWhitespaceAndRandCharsRegexStr = r"\* \*"
    
    binaryRegex = re.compile(binaryRegexStr)
    requiredWhitespaceRegex = re.compile(requiredWhitespaceRegexStr)
    optionalWhitespaceRegex = re.compile(optionalWhitespaceRegexStr)
    requiredWhitespaceAndRandCharsRegex = re.compile(requiredWhitespaceAndRandCharsRegexStr)
    optionalWhitespaceAndRandCharsRegex = re.compile(optionalWhitespaceAndRandCharsRegexStr)

    boblRegex = re.compile("{0}|{1}|{2}|{3}|{4}".format(
        binaryRegexStr,
        requiredWhitespaceRegexStr,
        optionalWhitespaceRegexStr,
        requiredWhitespaceAndRandCharsRegexStr,
        optionalWhitespaceAndRandCharsRegexStr
    ))

    def __init__(self):
        self.mangleBinaries = True
        self.manglePercent = None
        self.mangleLayers = None
        self.randWhitespace = True
        self.randWhitespaceRange = (0, 5)
        self.insertChars = True
        self.insertCharsRange = None
        self.insertMisleadingCmds = None
        self.insertMisleadingCmdsRange = None

        self.payloadLines = []

        self.randGen = RandomGen()

    def addPayloadLine(self, payloadLine, inputChunk=None):
        mangledPayloadLine = self.mangleLine(payloadLine, inputChunk)

        self.payloadLines.append(mangledPayloadLine)

    def mangleLine(self, payloadLine, inputChunk=None):
        mangledPayloadLine = payloadLine

        boblSyntaxMatch = Mangler.boblRegex.search(mangledPayloadLine)
        while boblSyntaxMatch:
            if Mangler.binaryRegex.match(boblSyntaxMatch.group()):
                mangledPayloadLine = self.mangleBinary(boblSyntaxMatch, mangledPayloadLine)

            elif Mangler.requiredWhitespaceRegex.match(boblSyntaxMatch.group()):
                mangledPayloadLine = self.insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, True, False)

            elif Mangler.optionalWhitespaceRegex.match(boblSyntaxMatch.group()):
                mangledPayloadLine = self.insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, False, False)

            elif Mangler.requiredWhitespaceAndRandCharsRegex.match(boblSyntaxMatch.group()):
                mangledPayloadLine = self.insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, True, True)

            elif Mangler.optionalWhitespaceAndRandCharsRegex.match(boblSyntaxMatch.group()):
                mangledPayloadLine = self.insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, False, True)

            boblSyntaxMatch = Mangler.boblRegex.search(mangledPayloadLine, pos=boblSyntaxMatch.start())

        if inputChunk:
            mangledPayloadLine = mangledPayloadLine.replace("DATA", inputChunk)

        return mangledPayloadLine

    def mangleBinary(self, binaryMatch, payloadLine):
        mangledBinary = ""
        binaryStr = payloadLine[binaryMatch.start() + 1:binaryMatch.end() - 1]

        for char in binaryStr:
            
            mangledBinary += "\\" + char

        mangledPayloadLine = payloadLine[:binaryMatch.start()] + mangledBinary + payloadLine[binaryMatch.end():]

        return mangledPayloadLine

    def insertWhitespaceAndRandChars(self, whitespaceMatch, payloadLine, whitespaceRequired, insertRandChars):
        if self.randWhitespace:
            if whitespaceRequired and self.randWhitespaceRange[0] == 0:
                minSpace = 1
            else:
                minSpace = self.randWhitespaceRange[0]

            whitespaceAmount = self.randGen.randGenNum(minSpace, self.randWhitespaceRange[1])
            mangledWhitespace = " "*whitespaceAmount

        #if insertRandChars and self.insertChars:


        mangledPayloadLine = payloadLine[:whitespaceMatch.start()] + mangledWhitespace + payloadLine[whitespaceMatch.end():]

        return mangledPayloadLine

    def getFinalPayload(self):
        return "".join(self.payloadLines)
        

#mangler = Mangler()
#mangler.addPayloadLine("* *:printf:^ ^%s^ ^'Hello World'* *;")