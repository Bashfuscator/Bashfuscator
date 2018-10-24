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

        self.quoted = False
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

        if self.mangleBinaries:
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

        else:
            mangledBinary = binaryStr

        mangledPayloadLine = payloadLine[:binaryMatch.start()] + mangledBinary + payloadLine[binaryMatch.end():]

        return mangledPayloadLine

    def insertWhitespaceAndRandChars(self, whitespaceMatch, payloadLine, whitespaceRequired, insertRandChars):
        mangledWhitespace = ""
        
        if not (insertRandChars and self.insertChars):
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
        if not self.randWhitespace:
            if whitespaceRequired:
                whitespaceAmount = 1
            else:
                whitespaceAmount = 0
        else:
            if whitespaceRequired and self.randWhitespaceRange[0] == 0:
                minSpace = 1
            else:
                minSpace = self.randWhitespaceRange[0]

            whitespaceAmount = self.randGen.randGenNum(minSpace, self.randWhitespaceRange[1])
        
        return " "*whitespaceAmount

    def getRandChars(self):
        randChars = ""
        charsToEscape = "[!(){}'`" + '"'

        varSymbol = self.randGen.randSelect(["@", "*"])
        choice = self.randGen.randChoice(17)

        if self.quoted and choice == 2:
            while choice == 2:
                choice = self.randGen.randChoice(17)

        if varSymbol == "@" and choice != 2 and self.randGen.probibility(50):
            randChars = '"'
            self.quoted = True
        else:
            self.quoted = False

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
            randWhitespace = self.getRandWhitespace(False)
            
            if randStr[-1:] == "\\" and randWhitespace == "":
                randStr += "\\"

            randChars += "${{{0}{1}{2}{3}}}".format(varSymbol, self.randGen.randSelect(["#", "##", "%", "%%", "/", "//"]), randStr, randWhitespace)

        else:
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randStr2 = self.randGen.randGenStr(escapeChars=charsToEscape)
            randWhitespace = self.getRandWhitespace(False)
            
            if randStr2[-1:] == "\\" and randWhitespace == "":
                randStr2 += "\\"

            randChars += "${{{0}{1}{2}/{3}{4}}}".format(varSymbol, self.randGen.randSelect(["/", "//"]), randStr, randStr2, randWhitespace)

        if self.quoted:
            randChars += '"'

        return randChars


    def getFinalPayload(self):
        return "".join(self.payloadLines)
