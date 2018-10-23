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
        self.manglePercent = 50
        self.mangleLayers = None
        self.randWhitespace = True
        self.randWhitespaceRange = (0, 5)
        self.insertChars = True
        self.insertCharsRange = (0, 3)
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
            if self.randGen.probibility(self.manglePercent/2):
                if self.randGen.probibility(50):
                    mangledBinary += '""'
                else:
                    mangledBinary += "''"
            
            if self.randGen.probibility(self.manglePercent):
                if self.randGen.probibility(50):
                    mangledBinary += "\\" + char
                else:
                    mangledBinary += self.getRandChars() + char
            
            else:
                mangledBinary += char

        mangledPayloadLine = payloadLine[:binaryMatch.start()] + mangledBinary + payloadLine[binaryMatch.end():]

        return mangledPayloadLine

    def insertWhitespaceAndRandChars(self, whitespaceMatch, payloadLine, whitespaceRequired, insertRandChars):
        mangledWhitespace = ""
        
        if self.randWhitespace and not (insertRandChars and self.insertChars):
            mangledWhitespace = self.getRandWhitespace(whitespaceRequired)

        elif insertRandChars and self.insertChars:
            charsInsertNum = self.randGen.randGenNum(self.insertCharsRange[0], self.insertCharsRange[1])

            for i in range(charsInsertNum):
                if self.randWhitespace:
                    mangledWhitespace += self.getRandWhitespace(whitespaceRequired)

                mangledWhitespace += self.getRandChars()

        mangledPayloadLine = payloadLine[:whitespaceMatch.start()] + mangledWhitespace + payloadLine[whitespaceMatch.end():]

        return mangledPayloadLine

    def getRandWhitespace(self, whitespaceRequired):
        if whitespaceRequired and self.randWhitespaceRange[0] == 0:
            minSpace = 1
        else:
            minSpace = self.randWhitespaceRange[0]

        whitespaceAmount = self.randGen.randGenNum(minSpace, self.randWhitespaceRange[1])
        
        return " "*whitespaceAmount

    def getRandChars(self):
        randChars = ""
        quoted = False
        charsToEscape = "[!(){}'`" + '"'

        varSymbol = self.randGen.randSelect(["@", "*"])
        choice = self.randGen.randChoice(17)

        if varSymbol == "@" and choice != 2 and self.randGen.probibility(50):
            randChars = '"'
            quoted = True

        if choice == 0:
            randChars += "$" + varSymbol

        elif choice == 1:
            randChars += "${{{0}}}".format(varSymbol)

        elif choice == 2:
            randChars += "${{!{0}}}".format(varSymbol)

        elif choice > 2 and choice <= 8:
            randChars += "${{{0}{1}{2}}}".format(varSymbol, self.randGen.randSelect(["^", "^^", ",", ",,", "~", "~~"]), self.getRandWhitespace(False))

        elif choice > 8 and choice <= 14:
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            
            if randStr[-1:] == "\\":
                randStr += "\\"

            randChars += "${{{0}{1}{2}{3}}}".format(varSymbol, self.randGen.randSelect(["#", "##", "%", "%%", "/", "//"]), randStr, self.getRandWhitespace(False))

        elif choice > 14 and choice <= 16:
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randStr2 = self.randGen.randGenStr(escapeChars=charsToEscape)
            
            if randStr[-1:] == "\\":
                randStr += "\\"
            if randStr2[-1:] == "\\":
                randStr += "\\"

            randChars += "${{{0}{1}{2}/{3}{4}}}".format(varSymbol, self.randGen.randSelect(["/", "//"]), randStr, randStr2, self.getRandWhitespace(False))

        if quoted:
            randChars += '"'

        return randChars


    def getFinalPayload(self):
        return "".join(self.payloadLines)
