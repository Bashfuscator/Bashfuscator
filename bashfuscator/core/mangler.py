"""
Class to manage obfuscation technuqies that are applied on all Mutators
"""
import re

from bashfuscator.common.random import RandomGen


class Mangler(object):
    """
    Class to handle mangling of individual payload lines
    """
    binaryRegexStr = r":\w+:"
    requiredWhitespaceRegexStr = r"\^ \^"
    optionalWhitespaceRegexStr = r"\? \?"
    requiredWhitespaceAndRandCharsRegexStr = "% %"
    optionalWhitespaceAndRandCharsRegexStr = r"\* \*"
    commandEndRegexStr = "END[01]?"

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
        self.debug = None

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
        self.nonBooleanCmdTerminator = False

        self.extraJunk = ""
        self.cmdCounter = 0
        self.cmdBufferOffset = None
        self.quoted = False
        self.terminatedCmdLast = False
        self.payloadLines = []
        self.finalPayload = ""

        self.randGen = RandomGen()


    def _initialize(self, sizePref, enableMangling, mangleBinaries, binaryManglePercent, randWhitespace, randWhitespaceRange, insertChars, insertCharsRange, misleadingCmds, misleadingCmdsRange, debug):
        self.sizePref = sizePref
        self.randGen.sizePref = self.sizePref

        self.extraJunk = ""
        self.payloadLines.clear()
        self.finalPayload = ""

        if debug:
            self.debug = debug
        else:
            self.debug = False

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
        """
        Add lines contained in payloadLines to the final payload in a
        random order.

        :param payloadLines: sequence of lines to be added to the final
            payload. Can be a list, or a dict, with the keys being the
            lines to add, and the values being the data to add into the
            line after BOBL expansions are processed.
        :type payloadLines: list or dict
        """
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
        """
        Mangle a line, preform any final processing and return its
        output.

        :param payloadLine: line to be mangled. If the line contains
            more than 2 characters of unknown input data, 'DATA' should
            be substituted for where the input data should go, and
            the inputChunk parameter should contain the input data
        :type payloadLine: str
        :param inputChunk: unknown input data to be substituted into
            the line after it undergoes mangling
        :type inputChunk: str or None
        :returns: mangled line as str
        """
        self.addPayloadLine(payloadLine, inputChunk)

        return self.getFinalPayload()

    def addPayloadLine(self, payloadLine, inputChunk=None):
        """
        Mangle a line and add it to the final payload.

        :param payloadLine: line to be mangled. If the line contains
            more than 2 characters of unknown input data, 'DATA' should
            be substituted for where the input data should go, and
            the inputChunk parameter should contain the input data
        :type payloadLine: str
        :param inputChunk: unknown input data to be substituted into
            the line after it undergoes mangling
        :type inputChunk: str or None
        """
        mangledPayloadLine = self._mangleLine(payloadLine, inputChunk)

        self.payloadLines.append(mangledPayloadLine)

    def _mangleLine(self, payloadLine, inputChunk=None):
        """
        Return a mangled line. Should not be called directly, use
        :meth:`~Mangler.addPayloadLine` or
        :meth:`~Mangler.getMangledLine` instead.

        :param payloadLine: line to be mangled. If the line contains
            more than 2 characters of unknown input data, 'DATA' should
            be substituted for where the input data should go, and
            the inputChunk parameter should contain the input data
        :type payloadLine: str
        :param inputChunk: unknown input data to be substituted into
            the line after it undergoes mangling
        :type inputChunk: str or None
        :returns: mangled line as str
        """
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
                    mangledPayloadLine = self._mangleBinary(boblSyntaxMatch, mangledPayloadLine)

                elif Mangler.requiredWhitespaceRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self._insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, True, False)

                elif Mangler.optionalWhitespaceRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self._insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, False, False)

                elif Mangler.requiredWhitespaceAndRandCharsRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self._insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, True, True)

                elif Mangler.optionalWhitespaceAndRandCharsRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self._insertWhitespaceAndRandChars(boblSyntaxMatch, mangledPayloadLine, False, True)

                elif Mangler.commandEndRegex.match(boblSyntaxMatch.group()):
                    mangledPayloadLine = self._getCommandTerminator(boblSyntaxMatch, mangledPayloadLine)

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

    def addJunk(self, prependJunk=False):
        """
        Add random whitespace and useless commands to the beginning or
        end of the final payload.

        :param prependJunk: True if junk should be added to beginning
            of payload
        :type prependJunk: bool
        """
        randJunk = self._getWhitespaceAndRandChars(False, True)

        if prependJunk:
            self.finalPayload += randJunk
        else:
            self.extraJunk += randJunk

    def _mangleBinary(self, binaryMatch, payloadLine):
        """

        """
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
                        mangledBinary += self._getAnsiCQuotedStr(char)
                    else:
                        mangledBinary += self._getRandChars() + char

                else:
                    mangledBinary += char

        else:
            mangledBinary = binaryStr

        mangledPayloadLine = payloadLine[:binaryMatch.start()] + mangledBinary + payloadLine[binaryMatch.end():]

        return mangledPayloadLine

    def _getAnsiCQuotedStr(self, inStr):
        """
        Return an Ansi-C quoted string. Apply longer forms of
        Ansi-C quoting depending on the user's sizePref.

        :param inStr: string to Ansi-C quote
        :type inStr: str
        :returns: Ansi-C quoted str
        """
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

    def _insertWhitespaceAndRandChars(self, whitespaceMatch, payloadLine, whitespaceRequired, insertRandChars):
        randCharsAndWhitespace = self._getWhitespaceAndRandChars(whitespaceRequired, insertRandChars)

        mangledPayloadLine = payloadLine[:whitespaceMatch.start()] + randCharsAndWhitespace + payloadLine[whitespaceMatch.end():]

        return mangledPayloadLine

    def _getWhitespaceAndRandChars(self, whitespaceRequired, insertRandChars):
        randCharsAndWhitespace = ""

        if not (insertRandChars and self.insertChars):
            randCharsAndWhitespace = self._getRandWhitespace(whitespaceRequired)

        elif insertRandChars and self.insertChars:
            charsInsertNum = self.randGen.randGenNum(self.insertCharsRange[0], self.insertCharsRange[1])

            for i in range(charsInsertNum):
                if self.randWhitespace:
                    randCharsAndWhitespace += self._getRandWhitespace(whitespaceRequired)

                randCharsAndWhitespace += self._getRandChars()

            randCharsAndWhitespace += self._getRandWhitespace(whitespaceRequired)

        return randCharsAndWhitespace

    def _getRandWhitespace(self, whitespaceRequired):
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

    def _getRandChars(self):
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
            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{self._getRandWhitespace(False)}}}"

        elif choice > 8 and choice <= 14:
            randParameterExpansionOperator = self.randGen.randSelect(["#", "##", "%", "%%", "/", "//"])
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randWhitespace = self._getRandWhitespace(False)

            if randStr[-1:] == "\\" and randWhitespace == "":
                randStr += "\\"

            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{randStr}{randWhitespace}}}"

        else:
            randStr = self.randGen.randGenStr(escapeChars=charsToEscape)
            randParameterExpansionOperator = self.randGen.randSelect(["/", "//"])
            randStr2 = self.randGen.randGenStr(escapeChars=charsToEscape)
            randWhitespace = self._getRandWhitespace(False)

            if randStr2[-1:] == "\\" and randWhitespace == "":
                randStr2 += "\\"

            randChars += f"${{{varSymbol}{randParameterExpansionOperator}{randStr}/{randStr2}{randWhitespace}}}"

        if self.quoted:
            randChars += '"'

        return randChars

    def _getCommandTerminator(self, terminatorMatch, payloadLine):
        endDigit = False
        cmdReturnsTrue = False
        self.booleanCmdTerminator = False
        self.nonBooleanCmdTerminator = True

        if payloadLine[terminatorMatch.end() - 1].isdigit():
            self.nonBooleanCmdTerminator = False

            if payloadLine[terminatorMatch.end() - 1] == "0":
                cmdReturnsTrue = True
                endDigit = True

            if payloadLine[terminatorMatch.end() - 1] == "1":
                endDigit = True

        if self.debug:
            cmdTerminator = "\n"

        else:
            if self.cmdCounter == 0:
                self.cmdBufferOffset = self.randGen.randGenNum(1250, 1750)

            if self.cmdCounter == self.cmdBufferOffset:
                self.cmdCounter = 0
                cmdTerminator = "\n"

            else:
                if not self.nonBooleanCmdTerminator and self.randGen.probibility(50):
                    self.booleanCmdTerminator = True

                    if cmdReturnsTrue:
                        cmdTerminator = "&&"
                    else:
                        cmdTerminator = "||"

                else:
                    cmdTerminator = ";"

            self.cmdCounter += 1

        self.cmdTerminatorPos = terminatorMatch.start()

        mangledPayloadLine = payloadLine[:terminatorMatch.start()] + cmdTerminator + payloadLine[terminatorMatch.end():]

        return mangledPayloadLine

    def getFinalPayload(self):
        """
        Apply any final processing and return the final payload.
        """
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
        elif not self.nonBooleanCmdTerminator and self.cmdTerminatorPos != 0 and self.randGen.probibility(50):
            if len(self.payloadLines[-1]) > self.cmdTerminatorPos + 1:
                finalJunk = self.payloadLines[-1][self.cmdTerminatorPos + 1:]

            self.payloadLines[-1] = self.payloadLines[-1][:self.cmdTerminatorPos] + finalJunk

        self.finalPayload += "".join(self.payloadLines)
        self.finalPayload += self.extraJunk

        return self.finalPayload
