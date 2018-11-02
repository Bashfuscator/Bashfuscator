import re

from bashfuscator.common.random import RandomGen


class Mangler(object):
    binaryRegexStr = r":\w+:"
    requiredWhitespaceRegexStr = r"\^ \^"
    optionalWhitespaceRegexStr = r"\? \?"
    requiredWhitespaceAndRandCharsRegexStr = "% %"
    optionalWhitespaceAndRandCharsRegexStr = r"\* \*"
    commandEndRegexStr = "END"

    binaryEscapedRegexStr = r"\\:\w+\\:"
    requiredWhitespaceEscapedRegexStr = r"\\\^ \\\^"
    optionalWhitespaceEscapedRegexStr = r"\\\? \\\?"
    requiredWhitespaceAndRandCharsEscapedRegexStr = r"\\% \\%"
    optionalWhitespaceAndRandCharsEscapedRegexStr = r"\\\* \\\*"

    binaryRegex = re.compile(binaryRegexStr)
    requiredWhitespaceRegex = re.compile(requiredWhitespaceRegexStr)
    optionalWhitespaceRegex = re.compile(optionalWhitespaceRegexStr)
    requiredWhitespaceAndRandCharsRegex = re.compile(requiredWhitespaceAndRandCharsRegexStr)
    optionalWhitespaceAndRandCharsRegex = re.compile(optionalWhitespaceAndRandCharsRegexStr)
    commandEndRegex = re.compile(commandEndRegexStr)

    boblRegex = re.compile("{0}|{1}|{2}|{3}|{4}|{5}".format(
        binaryRegexStr,
        requiredWhitespaceRegexStr,
        optionalWhitespaceRegexStr,
        requiredWhitespaceAndRandCharsRegexStr,
        optionalWhitespaceAndRandCharsRegexStr,
        commandEndRegexStr
    ))

    escapedBoblRegex = re.compile("{0}|{1}|{2}|{3}|{4}".format(
        binaryEscapedRegexStr,
        requiredWhitespaceEscapedRegexStr,
        optionalWhitespaceEscapedRegexStr,
        requiredWhitespaceAndRandCharsEscapedRegexStr,
        optionalWhitespaceAndRandCharsEscapedRegexStr
    ))


    def __init__(self):
        self.sizePref = None

        self.mangleBinaries = None
        self.binaryManglePercent = None
        self.randWhitespace = None
        self.randWhitespaceRange = None
        self.insertChars = None
        self.insertCharsRange = None
        self.misleadingCmds = None
        self.misleadingCmdsRange = None

        self.cmdTerminatorPos = 0
        self.booleanCmdTerminator = False
        self.nonBinaryCmdTerminator = False

        self.cmdCounter = 0
        self.cmdBufferOffset = None
        self.quoted = False
        self.terminatedCmdLast = False
        self.payloadLines = []
        self.finalPayload = ""

        self.randGen = RandomGen()


    def initialize(self, sizePref, enableMangling, mangleBinaries, binaryManglePercent, randWhitespace, randWhitespaceRange, insertChars, insertCharsRange, misleadingCmds, misleadingCmdsRange):
        self.sizePref = sizePref
        self.randGen.sizePref = self.sizePref

        self.payloadLines.clear()
        self.finalPayload = ""
        
        if enableMangling is False:
            return

        if mangleBinaries is not None:
            self.mangleBinaries = mangleBinaries
        else:
            self.mangleBinaries = True

        if binaryManglePercent:
            self.binaryManglePercent = binaryManglePercent
        else:
            if self.sizePref == 1:
                self.binaryManglePercent = 35
            elif self.sizePref == 2:
                self.binaryManglePercent = 50
            else:
                self.binaryManglePercent = 75

        if randWhitespace is not None:
            self.randWhitespace = randWhitespace
        else:
            self.randWhitespace = True

        if randWhitespaceRange:
            self.randWhitespaceRange = randWhitespaceRange
        else:
            if self.sizePref == 1:
                self.randWhitespaceRange = (0, 2)
            elif self.sizePref == 2:
                self.randWhitespaceRange = (1, 3)
            else:
                self.randWhitespaceRange = (2, 5)

        if insertChars is not None:
            self.insertChars = insertChars
        else:
            self.insertChars = True

        if insertCharsRange:
            self.insertCharsRange = insertCharsRange
        else:
            if self.sizePref == 1:
                self.insertCharsRange = (0, 1)
            elif self.sizePref == 2:
                self.insertCharsRange = (1, 2)
            else:
                self.insertCharsRange = (1, 3)

        if misleadingCmds is not None:
            self.misleadingCmds = misleadingCmds
        else:
            self.misleadingCmds = True

        if misleadingCmdsRange:
            self.misleadingCmdsRange = misleadingCmdsRange
        else:
            if self.sizePref == 1:
                self.misleadingCmdsRange = (0, 1)
            elif self.sizePref == 2:
                self.misleadingCmdsRange = (1, 2)
            else:
                self.misleadingCmdsRange = (1, 3)

    def addLinesInRandomOrder(self, payloadLines):
        if isinstance(payloadLines, list):
            self.randGen.randShuffle(payloadLines)

            for line in payloadLines:
                self.addPayloadLine(line)

        elif isinstance(payloadLines, dict):
            keys = list(payloadLines.keys())
            self.randGen.randShuffle(keys)
            
            for line in keys:
                self.addPayloadLine(line, payloadLines[line])

    def getMangledLine(self, payloadLine, inputChunk=None):
        self.addPayloadLine(payloadLine, inputChunk)

        return self.getFinalPayload()

    def addPayloadLine(self, payloadLine, inputChunk=None):
        mangledPayloadLine = self.mangleLine(payloadLine, inputChunk)

        self.payloadLines.append(mangledPayloadLine)

    def mangleLine(self, payloadLine, inputChunk=None):
        mangledPayloadLine = payloadLine

        escapedBoblSyntaxMatch = Mangler.escapedBoblRegex.search(mangledPayloadLine)

        if not escapedBoblSyntaxMatch:
            boblSyntaxMatch = Mangler.boblRegex.search(mangledPayloadLine)

        while escapedBoblSyntaxMatch or boblSyntaxMatch:
            if escapedBoblSyntaxMatch:
                escapedData = mangledPayloadLine[escapedBoblSyntaxMatch.start() + 1:escapedBoblSyntaxMatch.end() - 2] + mangledPayloadLine[escapedBoblSyntaxMatch.end() - 1]
                mangledPayloadLine = mangledPayloadLine[:escapedBoblSyntaxMatch.start()] + escapedData + mangledPayloadLine[escapedBoblSyntaxMatch.end():]

            else:
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

                elif Mangler.commandEndRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self.getCommandTerminator(boblSyntaxMatch, mangledPayloadLine)

            if escapedBoblSyntaxMatch:
                searchPos = escapedBoblSyntaxMatch.end() - 1
            else:
                searchPos = boblSyntaxMatch.start()

            escapedBoblSyntaxMatch = Mangler.escapedBoblRegex.search(mangledPayloadLine, pos=searchPos)

            if not escapedBoblSyntaxMatch:
                boblSyntaxMatch = Mangler.boblRegex.search(mangledPayloadLine, pos=searchPos)

        if inputChunk:
            mangledPayloadLine = mangledPayloadLine.replace("DATA", inputChunk)

        return mangledPayloadLine

    def addJunk(self):
        self.finalPayload += self.getWhitespaceAndRandChars(False, True)

    def mangleBinary(self, binaryMatch, payloadLine):
        mangledBinary = ""
        binaryStr = payloadLine[binaryMatch.start() + 1:binaryMatch.end() - 1]

        if self.mangleBinaries:
            for char in binaryStr:
                if self.randGen.probibility(self.binaryManglePercent / 2):
                    if self.randGen.probibility(50):
                        mangledBinary += '""'
                    else:
                        mangledBinary += "''"

                if self.randGen.probibility(self.binaryManglePercent):
                    choice = self.randGen.randChoice(3)
                    if choice == 0:
                        mangledBinary += "\\" + char
                    elif choice == 1:
                        mangledBinary += self.getAnsiCQuotedStr(char)
                    else:
                        mangledBinary += self.getRandChars() + char

                else:
                    mangledBinary += char

        else:
            mangledBinary = binaryStr

        mangledPayloadLine = payloadLine[:binaryMatch.start()] + mangledBinary + payloadLine[binaryMatch.end():]

        return mangledPayloadLine

    def getAnsiCQuotedStr(self, inStr):
        if self.sizePref == 1:
            maxChoice = 2
        elif self.sizePref == 2:
            maxChoice = 3
        else:
            maxChoice = 4

        encodedStr = "$'\\"

        for char in inStr:
            choice = self.randGen.randChoice(maxChoice)

            if choice == 0:
                encodedStr += oct(ord(char))[2:] + "\\"
            elif choice == 1:
                encodedStr += hex(ord(char))[1:] + "\\"
            elif choice == 2:
                encodedStr += "u00" + hex(ord(char))[2:] + "\\"
            else:
                encodedStr += "U000000" + hex(ord(char))[2:] + "\\"

        return encodedStr[:-1] + "'"

    def insertWhitespaceAndRandChars(self, whitespaceMatch, payloadLine, whitespaceRequired, insertRandChars):
        randCharsAndWhitespace = self.getWhitespaceAndRandChars(whitespaceRequired, insertRandChars)

        mangledPayloadLine = payloadLine[:whitespaceMatch.start()] + randCharsAndWhitespace + payloadLine[whitespaceMatch.end():]

        return mangledPayloadLine

    def getWhitespaceAndRandChars(self, whitespaceRequired, insertRandChars):
        randCharsAndWhitespace = ""
        
        if not (insertRandChars and self.insertChars):
            randCharsAndWhitespace = self.getRandWhitespace(whitespaceRequired)

        elif insertRandChars and self.insertChars:
            charsInsertNum = self.randGen.randGenNum(self.insertCharsRange[0], self.insertCharsRange[1])

            for i in range(charsInsertNum):
                if self.randWhitespace:
                    randCharsAndWhitespace += self.getRandWhitespace(whitespaceRequired)

                randCharsAndWhitespace += self.getRandChars()

            randCharsAndWhitespace += self.getRandWhitespace(whitespaceRequired)

        return randCharsAndWhitespace

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
            randChars += f"${{{varSymbol}}}"

        elif choice == 2:
            randChars += f"${{!{varSymbol}}}"

        elif choice > 2 and choice <= 8:
            randParameterExpansionOperator = self.randGen.randSelect(["^", "^^", ",", ",,", "~", "~~"])
            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{self.getRandWhitespace(False)}}}"

        elif choice > 8 and choice <= 14:
            randParameterExpansionOperator = self.randGen.randSelect(["#", "##", "%", "%%", "/", "//"])
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randWhitespace = self.getRandWhitespace(False)
            
            if randStr[-1:] == "\\" and randWhitespace == "":
                randStr += "\\"

            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{randStr}{randWhitespace}}}"

        else:
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randParameterExpansionOperator = self.randGen.randSelect(["/", "//"])
            randStr2 = self.randGen.randGenStr(escapeChars=charsToEscape)
            randWhitespace = self.getRandWhitespace(False)
            
            if randStr2[-1:] == "\\" and randWhitespace == "":
                randStr2 += "\\"

            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{randStr}/{randStr2}{randWhitespace}}}"

        if self.quoted:
            randChars += '"'

        return randChars

    def getCommandTerminator(self, terminatorMatch, payloadLine):
        endDigit = False
        self.nonBinaryCmdTerminator = False
        
        if self.cmdCounter == 0:
            self.cmdBufferOffset = self.randGen.randGenNum(1250, 1750)
        
        if self.cmdCounter == self.cmdBufferOffset:
            self.cmdCounter = 0
            cmdTerminator = "\n"

        else:
            cmdReturnsError = False

            if len(payloadLine) > terminatorMatch.end():
                if payloadLine[terminatorMatch.end()] == "0":
                    self.nonBinaryCmdTerminator = True
                    endDigit = True

                if payloadLine[terminatorMatch.end()] == "1":
                    cmdReturnsError = True
                    endDigit = True

            if not self.nonBinaryCmdTerminator and self.randGen.probibility(50):
                self.booleanCmdTerminator = True
                
                if cmdReturnsError:
                    cmdTerminator = "||"
                else:
                    cmdTerminator = "&&"

            else:
                self.booleanCmdTerminator = False
                cmdTerminator = ";"

        self.cmdCounter += 1
        self.cmdTerminatorPos = terminatorMatch.start()

        if endDigit:
            terminatorMatchEndPos = terminatorMatch.end() + 1
        else:
            terminatorMatchEndPos = terminatorMatch.end()

        mangledPayloadLine = payloadLine[:terminatorMatch.start()] + cmdTerminator + payloadLine[terminatorMatchEndPos:]

        return mangledPayloadLine

    def getFinalPayload(self):
        finalJunk = ""

        # if the final cmd terminator of the payload is '&&' or '||', bash will throw errors
        if self.booleanCmdTerminator:
            if len(self.payloadLines[-1]) > self.cmdTerminatorPos + 2:
                finalJunk = self.payloadLines[-1][self.cmdTerminatorPos + 2:]

            self.payloadLines[-1] = self.payloadLines[-1][:self.cmdTerminatorPos]

            # randomly replace '&&' or '||' with ';'
            if self.randGen.probibility(50):
                self.payloadLines[-1] += ";"

            self.payloadLines[-1] += finalJunk

        # randomly remove the final command terminator
        elif not self.nonBinaryCmdTerminator and self.cmdTerminatorPos != 0 and self.randGen.probibility(50):
            if len(self.payloadLines[-1]) > self.cmdTerminatorPos + 1:
                finalJunk = self.payloadLines[-1][self.cmdTerminatorPos + 1:]

            self.payloadLines[-1] = self.payloadLines[-1][:self.cmdTerminatorPos] + finalJunk

        self.finalPayload += "".join(self.payloadLines)

        return self.finalPayload
