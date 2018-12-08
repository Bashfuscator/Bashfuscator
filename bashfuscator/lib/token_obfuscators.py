"""
Token Obfuscators used by the framework.
"""
from binascii import hexlify
from collections import OrderedDict
import string
import re

from bashfuscator.common.helpers import strToArrayElements
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

    def __init__(self, name, description, sizeRating, timeRating, binariesUsed=[], fileWrite=False, notes=None, author=None, credits=None, evalWrap=True, unreadableOutput=False):
        super().__init__(name, "token", description, notes, author, credits, evalWrap, unreadableOutput)

        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.fileWrite = fileWrite
        self.binariesUsed = binariesUsed


class ForCode(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="ForCode",
            description="Shuffle command and reassemble it in a for loop",
            sizeRating=2,
            timeRating=3,
            author="capnspacehook",
            credits=["danielbohannon, https://github.com/danielbohannon/Invoke-DOSfuscation",
                "DisectMalare, https://twitter.com/DissectMalware/status/1029629127727431680"]
        )

    def mutate(self, userCmd):
        # get a set of unique chars in original command
        shuffledCmd = list(set(userCmd))
        self.randGen.randShuffle(shuffledCmd)
        shuffledCmd = "".join(shuffledCmd)

        # build a list of the indexes of where each char in the original command
        # is in the array that holds the individual chars
        ogCmdIdxes = []
        for char in userCmd:
            ogCmdIdxes.append(shuffledCmd.find(char))

        cmdIndexes = "".join([str(i) + "% %" for i in ogCmdIdxes])[:-3]

        shuffledCmd = strToArrayElements(shuffledCmd)

        charArrayVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine(f"? ?{charArrayVar}=({shuffledCmd})* *END0")

        indexVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine(f"? ?for^ ^{indexVar}^ ^in^ ^{cmdIndexes}* *END")

        # randomly choose between the two different for loop syntaxes
        if self.randGen.probibility(50):
            self.mangler.addPayloadLine(f'? ?{{^ ^:printf:^ ^%s^ ^"${{{charArrayVar}[* *${indexVar}* *]}}"* *;? ?}}? ?END* *')

        else:
            self.mangler.addPayloadLine(f'? ?do^ ^:printf:^ ^%s^ ^"${{{charArrayVar}[* *${indexVar}* *]}}"* *;? ?done? ?END* *')

        return self.mangler.getFinalPayload()


class SpecialCharOnly(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="Special Char Only",
            description="Converts commands to only use special characters",
            sizeRating=4,
            timeRating=2,
            binariesUsed=["cat"],
            notes="Will break when run in Bash's debug mode. Also compresses extremely well",
            author="capnspacehook",
            credits=["danielbohannon, https://github.com/danielbohannon/Invoke-Obfuscation",
                "Digital Trauma, https://codegolf.stackexchange.com/questions/22533/weirdest-obfuscated-hello-world"],
            evalWrap=False
        )

    def mutate(self, userCmd):
        self.indexCounter = 0
        self.mainArrayName = self.randGen.randUniqueStr(3, 26, "_")

        # test with BOBL syntax
        # build list of different commands that will return '0'
        zeroCmdSyntax = [":", "${__}", "_=END", "_=()", "${__[@]}", "${!__[@]}", ":(){ :; }END", \
            "_(){ _END }END", "_(){ _END }END:", "_(){ :END }END", "_(){ :END }END_", "_(){ :END }END:"]

        self.symbols = [" ", "#", "$", "%", "&", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "^", "_", "|", "~"]

        zeroCmd = self.randGen.randSelect(zeroCmdSyntax)

        # 1/2 of the time wrap zeroCmd in braces
        if zeroCmd[-3:] != "END" and self.randGen.probibility(50):
            zeroCmd += "END"

            zeroCmd = "{ " + zeroCmd + " }"

        initialDigitVar = self.randGen.randUniqueStr(3, 26, "_")

        if zeroCmd[-3:] != "END" and self.randGen.probibility(50):
            zeroCmd += "END"

            self.mangler.addPayloadLine(f"{zeroCmd}{initialDigitVar}=$?END0")

        else:
            if zeroCmd[-3:] != "END" and self.randGen.probibility(50):
                zeroCmd += "END"

            self.mangler.addPayloadLine(f"{initialDigitVar}=`{zeroCmd}`END0")

        incrementSyntaxChoices = ["(({0}={1}++))END0", "{0}=$(({1}++))END0", "{0}=$[{1}++]END0"]

        self.digitVars = []
        self.digitVars.append(self.randGen.randUniqueStr(3, 26, "_"))

        incrementStr = self.randGen.randSelect(incrementSyntaxChoices)
        if incrementStr == incrementSyntaxChoices[0]:
            #if the in-place arithmetic expansion is used when instantiating the first digitVar,
            # the command will return 1 for some reason
            incrementStr = incrementStr[:-1] + "1"

        self.mangler.addPayloadLine(incrementStr.format(self.digitVars[0], initialDigitVar))

        # build variables that will hold the digits 0-9
        for i in range(1, 10):
            self.digitVars.append(self.randGen.randUniqueStr(3, 26, "_"))

            incrementStr = self.randGen.randSelect(incrementSyntaxChoices)
            self.mangler.addPayloadLine(incrementStr.format(self.digitVars[i], initialDigitVar))

        procPIDDirsArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{procPIDDirsArrayVar}=(/????/$$/????)END0")

        procPIDAttrArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{procPIDAttrArrayVar}=${{{procPIDDirsArrayVar}[${self.digitVars[0]}]}}END0")

        procPathArrayVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{procPathArrayVar}=(${{{procPIDAttrArrayVar}//\// }})END0")

        attrVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{attrVar}=${{{procPathArrayVar}[${self.digitVars[2]}]}}END0")

        cattrVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{cattrVar}=${{{procPathArrayVar}: -${self.digitVars[1]}:${self.digitVars[1]}}}${attrVar}END0")

        catVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(rf"{catVar}=${{{cattrVar}\:{self.digitVars[0]}\:{self.digitVars[3]}}}END0")

        aVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(rf"{aVar}=${{{attrVar}\:{self.digitVars[0]}\:{self.digitVars[1]}}}END0")

        AVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{AVar}=${{{aVar}^}}END0")

        fromAtoaVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(rf". <(${catVar}<<<{fromAtoaVar}=\({{${AVar}..${aVar}}}\))END0")

        upperAlphabetVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{upperAlphabetVar}=(${{{fromAtoaVar}[@]:${self.digitVars[0]}:${self.digitVars[2]}${self.digitVars[6]}}})END0")

        lowerAlphabetVar = self.randGen.randUniqueStr(3, 26, "_")
        self.mangler.addPayloadLine(f"{lowerAlphabetVar}=(${{{upperAlphabetVar}[@],,}})END0")

        evalVar = self.getNextArrayIndex()
        evalSymbolStr = self.genSymbolAlphabetStr(lowerAlphabetVar, upperAlphabetVar, "eval")
        self.mangler.addPayloadLine(f"{self.genSetElementStr(evalVar)}={evalSymbolStr}END0")

        tempVar = self.getNextArrayIndex()
        cmdSubstitutionsStr = "$(:)"

        self.mangler.addPayloadLine(f"{self.genSetElementStr(tempVar)}=`{self.genAccessElementStr(evalVar)} '{{ {cmdSubstitutionsStr}END }} '${self.digitVars[2]}'>&'${self.digitVars[1]}`END0")
        self.mangler.addPayloadLine(f"{self.digitVars[0]}=${{#{self.genSetElementStr(tempVar)}}}END0")

        arithemticOperators = ["+", "-"]
        arithmeticExpansionSyntax = ["{0}=$(({1}{2}{3}))END0", "{0}=$[{1}{2}{3}]END0", "(({0}={1}{2}{3}))END0"]
        arrayInitializationStrs = []

        for i in range(1, 10):
            arithmeticSyntax = self.randGen.randSelect(arithmeticExpansionSyntax)

            arrayInitializationStrs.append(arithmeticSyntax.format(
                self.digitVars[i],
                self.digitVars[i],
                self.randGen.randSelect(arithemticOperators),
                self.digitVars[0]
            ))

        catKeyVar = self.getNextArrayIndex()
        arrayInitializationStrs.append(f"{self.genSetElementStr(catKeyVar)}=${catVar}END0")
        catVar = catKeyVar

        # TODO: fine-tune debug crash line
        arrayInitializationStrs.append(f": {self.genAccessElementStr(evalVar)} '{{ $[{self.genAccessElementStr(tempVar)}]END }} '${self.digitVars[2]}'>&'${self.digitVars[1]}END0")

        self.mangler.addLinesInRandomOrder(arrayInitializationStrs)


        # build the string 'printf' from substrings of error messages
        badStubstitutionErrMsg = " bad substitution"
        badStubstitutionErrVar = self.getNextArrayIndex()
        self.mangler.addPayloadLine(f"{self.genSetElementStr(badStubstitutionErrVar)}=`{self.genAccessElementStr(evalVar)} '{{ ${{}}END }} '${self.digitVars[2]}'>&'${self.digitVars[1]}`END1")
        self.mangler.addPayloadLine(f"{self.genSetElementStr(badStubstitutionErrVar)}=${{{self.genSetElementStr(badStubstitutionErrVar)}##*:}}END0")

        noSuchFileOrDirErrSymbols = ["!", "#", "$", "%", "+", ",", "-", ":", "=", "@", "[", "]", "^", "_", "{", "}", "~"]
        noSuchFileOrDirErrCmdSymbol = self.randGen.randSelect(noSuchFileOrDirErrSymbols)
        noSuchFileOrDirErrMsg = " No such file or directory"
        noSuchFileOrDirErrVar = self.getNextArrayIndex()
        self.mangler.addPayloadLine(f"{self.genSetElementStr(noSuchFileOrDirErrVar)}=`{self.genAccessElementStr(evalVar)} '{{ ./{noSuchFileOrDirErrCmdSymbol}END }} '${self.digitVars[2]}'>&'${self.digitVars[1]}`END1")
        self.mangler.addPayloadLine(f"{self.genSetElementStr(noSuchFileOrDirErrVar)}=${{{self.genSetElementStr(noSuchFileOrDirErrVar)}##*:}}END0")

        # get the string 'bash'
        bashStrVar = self.getNextArrayIndex()
        bashStr = rf"{self.genSetElementStr(bashStrVar)}=${{{self.genSetElementStr(badStubstitutionErrVar)}\:{self.digitVars[0]}\:{self.digitVars[3]}}}"
        bashStr += rf"${{{self.genSetElementStr(noSuchFileOrDirErrVar)}\:{self.digitVars[4]}\:{self.digitVars[1]}}}"
        bashStr += rf"${{{self.genSetElementStr(noSuchFileOrDirErrVar)}\:{self.digitVars[7]}\:{self.digitVars[1]}}}END0"
        self.mangler.addPayloadLine(bashStr)

        # get the character 'c' from the 'command not found' error message
        cCharVar = self.getNextArrayIndex()
        self.mangler.addPayloadLine(rf"{self.genSetElementStr(cCharVar)}=${{{self.genSetElementStr(noSuchFileOrDirErrVar)}\:{self.digitVars[6]}\:{self.digitVars[1]}}}END0")

        syntaxErrorMsg = "bash: -c: line 0: syntax error near unexpected token `;' bash: -c: line 0: `;'"
        syntaxErrorVar = self.getNextArrayIndex()
        self.mangler.addPayloadLine(f"""{self.genSetElementStr(syntaxErrorVar)}=`{self.genAccessElementStr(evalVar)} '{{ {self.genAccessElementStr(bashStrVar)} -{self.genAccessElementStr(cCharVar)} ";"END }} '${self.digitVars[2]}'>&'${self.digitVars[1]}`END1""")

        # get the character 'x' from the 'syntax' error message
        xCharVar = self.getNextArrayIndex()
        self.mangler.addPayloadLine(f"{self.genSetElementStr(xCharVar)}=${{{self.genSetElementStr(syntaxErrorVar)}:${self.digitVars[2]}${self.digitVars[3]}:${self.digitVars[1]}}}END0")


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

                    printfCharsInstatiationStrs.append(f"{self.genSetElementStr(charVarName)}=${{{self.genSetElementStr(errVar)}:{digitAccessStr}:${self.digitVars[1]}}}END0")
                    charVars.append(charVarName)

            printfCharVarNames[char] = charVars

        self.mangler.addLinesInRandomOrder(printfCharsInstatiationStrs)

        # there are roughly 2058 ways to generate the string 'printf' from the error messages that
        # are stored as variables. If the input exceeds the number of 'printf' vars, pre-assign the
        # 'printf' vars to make the payload smaller
        largeCmd = False
        if len(userCmd) > 2000:
            largeCmd = True
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
                                    printfVarsInstatiationStrs[printfVar] = f'{self.genSetElementStr(printfVar)}={"".join(instantiationStrPieces.values())}END0'
                                    printfVars[printfVar] = False

            printfVarsList = list(printfVars.keys())


        self.printfCmdCounter = 0
        symbolCommandStr = f'{self.genAccessElementStr(evalVar)} "$('
        for cmdChar in userCmd:
            if largeCmd:
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

                symbolCommandStr += rf'{printfStr} "\\{self.genAccessElementStr(xCharVar)}{digitsAccess}"'

            else:
                octCode = str(oct(ord(cmdChar)))[2:]
                for char in octCode:
                    digitsAccess += "$" + self.digitVars[int(char)]

                symbolCommandStr += rf'{printfStr} "\\{digitsAccess}"'

            symbolCommandStr += "END0"

        symbolCommandStr += ')"'

        # declare and assign the printf variables that were randomly selected to be used
        if largeCmd:
            printfInstanstiationStrs = []
            for var, used in printfVars.items():
                if used:
                    printfInstanstiationStrs.append(printfVarsInstatiationStrs[var])

            self.mangler.addLinesInRandomOrder(printfInstanstiationStrs)

        self.mangler.addPayloadLine(symbolCommandStr)

        return self.mangler.getFinalPayload()


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
