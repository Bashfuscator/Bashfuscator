"""
Token Obfuscators used by the framework.
"""
from binascii import hexlify
from collections import OrderedDict
import string
import re

from bashfuscator.common.objects import Mutator


class TokenObfuscator(Mutator):
    """
    Base class for all token obfuscators. If an obfuscator is able to
    be deobfuscated and executed by bash at runtime, without bash
    having to execute a stub or any code, then it is a Token Obfuscator.

    :param name: name of the TokenObfuscator
    :type name: str
    :param description: short description of what the TokenObfuscator
        does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how much the 
        TokenObfuscator increases the size of the overall payload
    :type sizeRating: int
    :param fileWrite: True if the Token Obfuscator requires 
        creating/writing to files, False otherwise
    :type fileWrite: bool
    :param notes: see :class:`bashfuscator.common.objects.Mutator`
    :type notes: str
    :param author: see :class:`bashfuscator.common.objects.Mutator`
    :type author: str
    :param credits: see :class:`bashfuscator.common.objects.Mutator`
    :type credits: str
    """

    def __init__(self, name, description, sizeRating, timeRating, binariesUsed=[], fileWrite=False, notes=None, author=None, credits=None, evalWrap=True):
        super().__init__(name, "token", description, notes, author, credits, evalWrap)

        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.fileWrite = fileWrite
        self.binariesUsed = binariesUsed
        self.originalCmd = ""
        self.payload = ""


class AnsiCQuote(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="ANSI-C Quote",
            description="ANSI-C quotes a string",
            sizeRating=3,
            timeRating=1,
            author="capnspacehook",
            credits=["DissectMalware, https://twitter.com/DissectMalware/status/1023682809368653826"],
            notes="Requires Bash 4.2 or above"
        )

        self.SUBSTR_QUOTE_PROB = 33

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = "printf %s $'\\"

        if sizePref < 2:
            maxChoice = 2
        elif sizePref < 3:
            maxChoice = 3
        else:
            maxChoice = 4

        for char in self.originalCmd:
            choice = self.randGen.randChoice(maxChoice)

            # If sizePref is 3, randomly ANSI-C quote substrings of the original
            # userCmd and randomly add empty strings
            if sizePref == 4 and self.randGen.probibility(self.SUBSTR_QUOTE_PROB):
                obCmd = obCmd[:-1] + "'" + "".join("''" for x in range(
                    self.randGen.randGenNum(0, 5))) + "$'\\"

            if choice == 0:
                obCmd += oct(ord(char))[2:] + "\\"
            elif choice == 1:
                obCmd += hex(ord(char))[1:] + "\\"
            elif choice == 2:
                obCmd += "u00" + hex(ord(char))[2:] + "\\"
            else:
                obCmd += "U000000" + hex(ord(char))[2:] + "\\"

        self.payload = obCmd[:-1] + "'"

        return self.payload


class SpecialCharOnly(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="Special Char Only",
            description="Converts commands to only use special characters",
            sizeRating=4,
            timeRating=2,
            binariesUsed=["cat"],
            author="capnspacehook",
            credits=["danielbohannon, https://github.com/danielbohannon/Invoke-Obfuscation",
                "Digital Trauma, https://codegolf.stackexchange.com/questions/22533/weirdest-obfuscated-hello-world"],
            evalWrap=False
        )

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.indexCounter = 0
        self.mainArrayName = self.randGen.randUniqueStr(3, 5, "_")

        # build list of different commands that will return '0'
        zeroCmdSyntax = [":", "${__}", "_=;", "_=()", "${__[@]}", "${!__[@]}", ":(){ :; };", \
            "_(){ _; };", "_(){ _; };:", "_(){ :; };", "_(){ :; };_", "_(){ :; };:"]

        self.symbols = [" ", "#", "$", "%", "&", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "^", "_", "|", "~"]

        zeroCmd = self.randGen.randSelect(zeroCmdSyntax)

        # 1/2 of the time wrap zeroCmd in braces
        if self.randGen.probibility(50):
            if zeroCmd[-1:] != ";":
                zeroCmd += ";"

            zeroCmd = "{ " + zeroCmd + " }"

        initialDigitVar = self.randGen.randUniqueStr(3, 26, "_")

        if self.randGen.probibility(50):
            if zeroCmd[-1:] != ";":
                zeroCmd += ";"

            arrayInstantiationStr = "{0}{1}=$?{2}".format(zeroCmd, initialDigitVar, self.genCommandSeporatorStr())

        else:
            if self.randGen.probibility(50) and zeroCmd[-1:] != ";":
                zeroCmd += ";"

            arrayInstantiationStr = "{0}=`{1}`{2}".format(initialDigitVar, zeroCmd, self.genCommandSeporatorStr())

        incrementSyntaxChoices = ["(({0}={1}++)){2}", "{0}=$(({1}++)){2}", "{0}=$[{1}++]{2}"]
        self.digitVars = []

        # build variables that will hold the digits 0-9
        for i in range(0, 10):
            self.digitVars.append(self.randGen.randUniqueStr(3, 26, "_"))

            incrementStr = self.randGen.randSelect(incrementSyntaxChoices)
            incrementStr = incrementStr.format(self.digitVars[i], initialDigitVar, self.genCommandSeporatorStr())

            arrayInstantiationStr += incrementStr

        procPIDDirsArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=(/????/$$/????){1}".format(procPIDDirsArrayVar, self.genCommandSeporatorStr())

        procPIDAttrArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}[${2}]}}{3}".format(procPIDAttrArrayVar, procPIDDirsArrayVar, self.digitVars[0], self.genCommandSeporatorStr())

        procPathArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=(${{{1}//\// }}){2}".format(procPathArrayVar, procPIDAttrArrayVar, self.genCommandSeporatorStr())

        attrVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}[${2}]}}{3}".format(attrVar, procPathArrayVar, self.digitVars[2], self.genCommandSeporatorStr())

        cattrVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}: -${2}:${2}}}${3}{4}".format(cattrVar, procPathArrayVar, self.digitVars[1], attrVar, self.genCommandSeporatorStr())

        catVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}:{2}:{3}}}{4}".format(catVar, cattrVar, self.digitVars[0], self.digitVars[3], self.genCommandSeporatorStr())

        aVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}:{2}:{3}}}{4}".format(aVar, attrVar, self.digitVars[0], self.digitVars[1], self.genCommandSeporatorStr())

        AVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=${{{1}^}}{2}".format(AVar, aVar, self.genCommandSeporatorStr())

        fromAtoaVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += r". <(${0}<<<{1}=\({{${2}..${3}}}\)){4}".format(catVar, fromAtoaVar, AVar, aVar, self.genCommandSeporatorStr())

        upperAlphabetVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=(${{{1}[@]:${2}:${3}${4}}}){5}".format(upperAlphabetVar, fromAtoaVar, self.digitVars[0], self.digitVars[2], self.digitVars[6], self.genCommandSeporatorStr())

        lowerAlphabetVar = self.randGen.randUniqueStr(3, 26, "_")
        arrayInstantiationStr += "{0}=(${{{1}[@],,}}){2}".format(lowerAlphabetVar, upperAlphabetVar, self.genCommandSeporatorStr())

        arrayInitializationStrs = []

        evalVar = self.getNextArrayIndex()
        arrayInstantiationStr += "{0}={1}{2}".format(self.genSetElementStr(evalVar), self.genSymbolAlphabetStr(lowerAlphabetVar, upperAlphabetVar, "eval"), self.genCommandSeporatorStr())

        tempVar = self.getNextArrayIndex()
        cmdSubstitutionsStr = "$(:)"
        arrayInstantiationStr += "{0}=`{1} '{{ {2}; }} '${3}'>&'${4}`{5}{6}=${{#{7}}}{8}".format(
            self.genSetElementStr(tempVar), 
            self.genAccessElementStr(evalVar),
            cmdSubstitutionsStr,
            self.digitVars[2],
            self.digitVars[1],
            self.genCommandSeporatorStr(),
            self.digitVars[0],
            self.genSetElementStr(tempVar),
            self.genCommandSeporatorStr()
        )

        arithemticOperators = ["+", "-"]
        arithmeticExpansionSyntax = ["{0}=$(({1}{2}{3})){4}", "{0}=$[{1}{2}{3}]{4}", "(({0}={1}{2}{3})){4}"]
        for i in range(1, 10):
            arithmeticSyntax = self.randGen.randSelect(arithmeticExpansionSyntax)

            arrayInitializationStrs.append(arithmeticSyntax.format(
                self.digitVars[i], 
                self.digitVars[i],
                self.randGen.randSelect(arithemticOperators),
                self.digitVars[0],
                self.genCommandSeporatorStr()
            ))

        catKeyVar = self.getNextArrayIndex()
        arrayInitializationStrs.append("{0}=${1}{2}".format(self.genSetElementStr(catKeyVar), catVar, self.genCommandSeporatorStr()))
        catVar = catKeyVar

        # TODO: fine-tune debug crash line
        arrayInitializationStrs.append(": {0} '{{ $[{1}]; }} '${2}'>&'${3}{4}".format(
            self.genAccessElementStr(evalVar), 
            self.genAccessElementStr(tempVar),
            self.digitVars[2],
            self.digitVars[1],
            self.genCommandSeporatorStr()
        ))

        self.randGen.randShuffle(arrayInitializationStrs)
        arrayInstantiationStr += "".join(arrayInitializationStrs)

        # build the string 'printf' from substrings of error messages
        badStubstitutionErrMsg = " bad substitution"
        badStubstitutionErrVar = self.getNextArrayIndex()
        badStubstitutionErrStr = "{0}=`{1} '{{ ${{}}; }} '${2}'>&'${3}`{4}{0}=${{{0}##*:}}{5}".format(
            self.genSetElementStr(badStubstitutionErrVar),
            self.genAccessElementStr(evalVar),
            self.digitVars[2],
            self.digitVars[1],
            self.genCommandSeporatorStr(False),
            self.genCommandSeporatorStr()
        )

        noSuchFileOrDirErrSymbols = ["!", "#", "$", "%", "+", ",", "-", ":", "=", "@", "[", "]", "^", "_", "{", "}", "~"]
        noSuchFileOrDirErrCmdSymbol = self.randGen.randSelect(noSuchFileOrDirErrSymbols)
        noSuchFileOrDirErrMsg = " No such file or directory"
        noSuchFileOrDirErrVar = self.getNextArrayIndex()
        noSuchFileOrDirErrStr = "{0}=`{1} '{{ ./{2}; }} '${3}'>&'${4}`{5}{0}=${{{0}##*:}}{6}".format(
            self.genSetElementStr(noSuchFileOrDirErrVar),
            self.genAccessElementStr(evalVar),
            noSuchFileOrDirErrCmdSymbol,
            self.digitVars[2],
            self.digitVars[1],
            self.genCommandSeporatorStr(False),
            self.genCommandSeporatorStr()
        )

        # get the string 'bash'
        bashStrVar = self.getNextArrayIndex()
        bashStr = "{0}=${{{1}:{2}:{3}}}".format(
            self.genSetElementStr(bashStrVar),
            self.genSetElementStr(badStubstitutionErrVar),
            self.digitVars[0],
            self.digitVars[3],
        )

        bashStr += "${{{0}:{1}:{2}}}".format(
            self.genSetElementStr(noSuchFileOrDirErrVar),
            self.digitVars[4],
            self.digitVars[1]
        )

        bashStr += "${{{0}:{1}:{2}}}{3}".format(
            self.genSetElementStr(noSuchFileOrDirErrVar),
            self.digitVars[7],
            self.digitVars[1],
            self.genCommandSeporatorStr()
        )

        # get the character 'c' from the 'command not found' error message
        cCharVar = self.getNextArrayIndex()
        cCharStr = "{0}=${{{1}:{2}:{3}}}{4}".format(
            self.genSetElementStr(cCharVar),
            self.genSetElementStr(noSuchFileOrDirErrVar),
            self.digitVars[6],
            self.digitVars[1],
            self.genCommandSeporatorStr()
        )

        syntaxErrorMsg = "bash: -c: line 0: syntax error near unexpected token `;' bash: -c: line 0: `;'"
        syntaxErrorVar = self.getNextArrayIndex()
        syntaxErrorStr = """{0}=`{1} '{{ {2} -{3} ";"; }} '${4}'>&'${5}`{6}""".format(
            self.genSetElementStr(syntaxErrorVar),
            self.genAccessElementStr(evalVar),
            self.genAccessElementStr(bashStrVar),
            self.genAccessElementStr(cCharVar),
            self.digitVars[2],
            self.digitVars[1],
            self.genCommandSeporatorStr(False)
        )

        # get the character 'x' from the 'syntax' error message
        xCharVar = self.getNextArrayIndex()
        xCharStr = "{0}=${{{1}:${2}${3}:${4}}}{5}".format(
            self.genSetElementStr(xCharVar),
            self.genSetElementStr(syntaxErrorVar),
            self.digitVars[2],
            self.digitVars[3],
            self.digitVars[1],
            self.genCommandSeporatorStr()
        )

        printfInstanstiationStr = badStubstitutionErrStr + noSuchFileOrDirErrStr + bashStr + cCharStr + syntaxErrorStr + xCharStr


        #store all the characters of 'printf' from the stored error messages
        printfCharsInstatiationStrs = []
        printfCharVarNames = {}
        for char in "printf ":
            charVars = []

            for errMsg, errVar in [(badStubstitutionErrMsg, badStubstitutionErrVar), (noSuchFileOrDirErrMsg, noSuchFileOrDirErrVar), (syntaxErrorMsg, syntaxErrorVar)]:
                indexes = [i for i, letter in enumerate(errMsg) if letter == char]

                for idx in indexes:
                    charVarName = self.getNextArrayIndex()

                    digitAccessStr = ""
                    for digit in str(idx):
                        digitAccessStr += "$" + self.digitVars[int(digit)]

                    printfCharsInstatiationStrs.append("{0}=${{{1}:{2}:${3}}}{4}".format(
                        self.genSetElementStr(charVarName),
                        self.genSetElementStr(errVar),
                        digitAccessStr,
                        self.digitVars[1],
                        self.genCommandSeporatorStr()
                    ))

                    charVars.append(charVarName)

            printfCharVarNames[char] = charVars

        self.randGen.randShuffle(printfCharsInstatiationStrs)
        printfInstanstiationStr += "".join(printfCharsInstatiationStrs)

        # there are roughly 2058 ways to generate the string 'printf' from the error messages that
        # are stored as variables. If the input exceeds the number of 'printf' vars, pre-assign the
        # 'printf' vars to make the payload smaller
        self.largeCmd = False
        if len(self.originalCmd) > 2000:
            self.largeCmd = True
            instantiationStrPieces = OrderedDict()
            printfVarsInstatiationStrs = {}
            printfVars = {}

            for pCharVar in printfCharVarNames["p"]:
                instantiationStrPieces["p"] = self.genAccessElementStr(pCharVar)
                for rCharVar in printfCharVarNames["r"]:
                    instantiationStrPieces["r"] = self.genAccessElementStr(rCharVar)
                    for iCharVar in printfCharVarNames["i"]:
                        instantiationStrPieces["i"] = self.genAccessElementStr(iCharVar)
                        for nCharVar in printfCharVarNames["n"]:
                            instantiationStrPieces["n"] = self.genAccessElementStr(nCharVar)
                            for tCharVar in printfCharVarNames["t"]:
                                instantiationStrPieces["t"] = self.genAccessElementStr(tCharVar)
                                for fCharVar in printfCharVarNames["f"]:
                                    instantiationStrPieces["f"] = self.genAccessElementStr(fCharVar)

                                    #if (self.randGen.probibility(33)):
                                    #    instantiationStrPieces.append(self.genAccessElementStr(self.randGen.randSelect(printfCharVarNames[" "])))

                                    printfVar = self.getNextArrayIndex()
                                    printfVarsInstatiationStrs[printfVar] = "{0}={1}{2}".format(
                                        self.genSetElementStr(printfVar), 
                                        "".join(instantiationStrPieces.values()),
                                        self.genCommandSeporatorStr()
                                    )
                                    printfVars[printfVar] = False

            printfVarsList = list(printfVars.keys())


        self.printfCmdCounter = 0
        symbolCommandStr = '{0} "$('.format(self.genAccessElementStr(evalVar))
        for cmdChar in userCmd:
            if self.largeCmd:
                printfVar = self.randGen.randSelect(printfVarsList)
                printfVars[printfVar] = True
                printfStr = self.genAccessElementStr(printfVar)

            else:
                printfStr = ""
                for printfChar in "printf":
                    printfStr += self.genAccessElementStr(self.randGen.randSelect(printfCharVarNames[printfChar]))

            digitsAccess = ""
            # if char's hex representation only contains alpha chars, 1/2 of the time use that for the printf statement
            hexCode = str(hex(ord(cmdChar)))[2:]
            if hexCode.isdigit() and self.randGen.probibility(50):
                for char in hexCode:
                    digitsAccess += "$" + self.digitVars[int(char)]

                symbolCommandStr += r'{0} "\\{1}{2}"'.format(printfStr, self.genAccessElementStr(xCharVar), digitsAccess)

            else:
                octCode = str(oct(ord(cmdChar)))[2:]
                for char in octCode:
                    digitsAccess += "$" + self.digitVars[int(char)]

                symbolCommandStr += r'{0} "\\{1}"'.format(printfStr, digitsAccess)

            symbolCommandStr += self.genCommandSeporatorStr(printfStr=True)
        
        if self.randGen.probibility(50):
            symbolCommandStr = symbolCommandStr[:-1]

        symbolCommandStr += ')"'

        # declare and assign the printf variables that were randomly selected to be used
        if self.largeCmd:
            printfInstanstiationStrs = []
            for var, used in printfVars.items():
                if used:
                    printfInstanstiationStrs.append(printfVarsInstatiationStrs[var])

            self.randGen.randShuffle(printfInstanstiationStrs)
            printfInstanstiationStr += "".join(printfInstanstiationStrs)

        self.payload = arrayInstantiationStr + printfInstanstiationStr + symbolCommandStr

        return self.payload


    def genCommandSeporatorStr(self, printfStr=False):
        if printfStr:
            if self.printfCmdCounter == 0:
                self.printfCmdCounter += 1
                self.cmdOffset = self.randGen.randGenNum(1250, 1750)
                seporator = ";"
            
            elif self.printfCmdCounter == self.cmdOffset:
                self.printfCmdCounter = 0
                seporator = "\n"

            else:
                self.printfCmdCounter += 1
                seporator = ";"

        else:
            seporator = ";"

        return seporator

    def genSymbolAlphabetStr(self, lowerArrayName, upperArrayName, initialStr):
        invertSyntaxChoices = ["~", "~~"]
        lowerSyntaxChoices = [",", ",,"] + invertSyntaxChoices
        upperSyntaxChoices = ["^", "^^"] + invertSyntaxChoices

        symbolStr = ""
        for c in initialStr:
            if c in string.punctuation + " ":
                symbolStr += '"{0}"'.format(c)

            elif c in string.ascii_lowercase:
                index = string.ascii_lowercase.find(c)

                indexStr = ""
                for i in str(index):
                    indexStr += "${0}".format(self.digitVars[int(i)])
                
                if self.randGen.probibility(50):
                    symbolStr += "${{{0}[{1}]{2}}}".format(lowerArrayName, indexStr, "")
                else:
                    symbolStr += "${{{0}[{1}]{2}}}".format(upperArrayName, indexStr, self.randGen.randSelect(lowerSyntaxChoices))

            elif c in string.ascii_uppercase:
                index = string.ascii_uppercase.find(c)

                indexStr = ""
                for i in str(index):
                    indexStr += "${0}".format(self.digitVars[int(i)])

                if self.randGen.probibility(50):
                    symbolStr += "${{{0}[{1}]{2}}}".format(upperArrayName, indexStr, "")
                else:
                    symbolStr += "${{{0}[{1}]{2}}}".format(lowerArrayName, indexStr, self.randGen.randSelect(upperSyntaxChoices))

        return symbolStr

    def getNextArrayIndex(self):
        nextIndex = self.indexCounter
        self.indexCounter += 1

        return nextIndex

    def genAccessElementStr(self, index):
        return '${{{0}[{1}]}}'.format(self.mainArrayName, self.getIndexVars(index))

    def genSetElementStr(self, index):
        return '{0}[{1}]'.format(self.mainArrayName, self.getIndexVars(index))
 
    def getIndexVars(self, index):
        varIndexStr= ""        
        for num in str(index):
            varIndexStr += "$" + self.digitVars[int(num)]

        return varIndexStr
