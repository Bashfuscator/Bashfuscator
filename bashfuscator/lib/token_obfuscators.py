"""
Token Obfuscators used by the framework.
"""
from binascii import hexlify
import string

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
    :param notes: see :class:`bashfuscator.common.objects.Mutator`
    :type notes: str
    :param author: see :class:`bashfuscator.common.objects.Mutator`
    :type author: str
    :param credits: see :class:`bashfuscator.common.objects.Mutator`
    :type credits: str
    """

    def __init__(self, name, description, sizeRating, notes=None, author=None, credits=None):
        super().__init__(name, "token", notes, author, credits)

        self.description = description
        self.sizeRating = sizeRating
        self.originalCmd = ""
        self.payload = ""


class AnsiCQuote(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="ANSI-C Quote",
            description="ANSI-C quotes a string",
            sizeRating=3,
            author="capnspacehook",
            credits="DissectMalware, https://twitter.com/DissectMalware/status/1023682809368653826"
        )

        self.SUBSTR_QUOTE_PROB = 33

    def obfuscate(self, sizePref, userCmd):
        self.originalCmd = userCmd

        obCmd = "printf -- $'\\"

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


class SpecialCharCommand(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="Special Char Command",
            description="Converts commands to only use special characters",
            sizeRating=2,
        )

    def obfuscate(self, sizePref, userCmd):
        self.originalCmd = userCmd

        # build list of different commands that will return '0'
        zeroCmdSyntax = [":", "${__}", "_=;", "_=()", "${__[@]}", "${!__[@]}", ":(){ :; };", \
            "_(){ _; };", "_(){ _; };:", "_(){ :; };", "_(){ :; };_", "_(){ :; };:"]

        # TODO: test and build list of what symbols work as keys for associative arrays
        # '*', '\', '@', '[', ']', '`', '~' cause problems
        symbols = ["#", "$", "%", "&", "(", ")", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "^", "_", "{", "|", "}"]
        
        zeroCmd = self.randGen.randSelect(zeroCmdSyntax)

        # 1/2 of the time wrap zeroCmd in braces
        if self.randGen.probibility(50):
            if zeroCmd[-1:] != ";":
                zeroCmd += ";"
            
            zeroCmd = "{ " + zeroCmd + " }"

        digitArrayName = self.randGen.randUniqueStr(3, 5, "_")
        initialDigitVar = self.randGen.randUniqueStr(1, 1, symbols)

        # 1/2 of the time set the first index of the array to the return code of zeroCmd
        if self.randGen.probibility(50):
            if zeroCmd[-1:] != ";":
                zeroCmd += ";"

            digitsInstantiationStr = "{0}declare -A {1}".format(zeroCmd, digitArrayName)

            if self.randGen.probibility(50):
                digitsInstantiationStr += "['{0}']=$?;".format(initialDigitVar)
            else:
                digitsInstantiationStr += ";{0}['{1}']=$?;".format(digitArrayName, initialDigitVar)
        
        else:
            if self.randGen.probibility(50):
                if zeroCmd[-1:] != ";":
                    zeroCmd += ";"

            digitsInstantiationStr = "declare -A {0}".format(digitArrayName)
            
            zeroCmd = "$({0})".format(zeroCmd)

            if self.randGen.probibility(50):
                digitsInstantiationStr += "['{0}']={1};".format(initialDigitVar, zeroCmd)
            else:
                digitsInstantiationStr += ";{0}['{1}']={2};".format(digitArrayName, initialDigitVar, zeroCmd)

        self.accessElementStr = "${{" + digitArrayName + "['{0}']}}"
        self.setElementStr = digitArrayName + "['{0}']"
        setInitialElementStr = self.setElementStr.format(initialDigitVar)
        accessInitialElementStr = self.accessElementStr.format(initialDigitVar)

        # TODO: add and test more increment syntaxes
        incrementSyntaxChoices = ["(({0}={1}++));"]
        self.digitVars = []

        for i in range(0, 10):
            self.digitVars.append(self.randGen.randUniqueStr(1, 1, symbols))
            setNewDigitVarStr = self.setElementStr.format(self.digitVars[i])

            incrementStr = self.randGen.randSelect(incrementSyntaxChoices)
            incrementStr = incrementStr.format(setNewDigitVarStr, setInitialElementStr)

            digitsInstantiationStr += incrementStr

        # build the string 'printf' from substrings of error messages
        cmdNotFoundErrMsg = "bash: _: command not found"
        cmdNotFoundErrVar = self.randGen.randUniqueStr(1, 1, symbols)
        cmdNotFoundErrStr = "{0}=$({{ _; }} {1}>&{2});".format(
            self.setElementStr.format(cmdNotFoundErrVar),
            self.accessElementStr.format(self.digitVars[2]),
            self.accessElementStr.format(self.digitVars[1])
        )

        badStubstitutionErrMsg = "bash: ${}: bad substitution"
        badStubstitutionErrVar = self.randGen.randUniqueStr(1, 1, symbols)
        badStubstitutionErrStr = "{0}=$({{ ${{}}; }} {1}>&{2});".format(
            self.setElementStr.format(badStubstitutionErrVar),
            self.accessElementStr.format(self.digitVars[2]),
            self.accessElementStr.format(self.digitVars[1])
        )

        # get the string 'bash' from one of the error messages above
        bashStrVar = self.randGen.randUniqueStr(1, 1, symbols)
        bashStr = "{0}=${{{1}:{2}:{3}}};".format(
            self.setElementStr.format(bashStrVar),
            self.setElementStr.format(cmdNotFoundErrVar),
            self.accessElementStr.format(self.digitVars[0]),
            self.accessElementStr.format(self.digitVars[4])
        )

        # get the character 'c' from the 'command not found' error message
        cCharVar = self.randGen.randUniqueStr(1, 1, symbols)
        cCharStr = "{0}=${{{1}:{2}:{3}}};".format(
            self.setElementStr.format(cCharVar),
            self.setElementStr.format(cmdNotFoundErrVar),
            self.accessElementStr.format(self.digitVars[9]),
            self.accessElementStr.format(self.digitVars[1])
        )

        syntaxErrorMsg = "bash: -c: line 0: syntax error near unexpected token `;' bash: -c: line 0: `;'"
        syntaxErrorVar = self.randGen.randUniqueStr(1, 1, symbols)
        syntaxErrorStr = "{0}=$({{ {1} -{2} ';'; }} {3}>&{4});".format(
            self.setElementStr.format(syntaxErrorVar),
            self.accessElementStr.format(bashStrVar),
            self.setElementStr.format(cCharVar),
            self.accessElementStr.format(self.digitVars[2]),
            self.accessElementStr.format(self.digitVars[1])
        )

        printfInstanstiationStr = cmdNotFoundErrStr + badStubstitutionErrStr + bashStr + cCharStr + syntaxErrorStr

        return digitsInstantiationStr + printfInstanstiationStr

        symbolCommandStr = ""

        for char in userCmd:
            if char in string.punctuation:
                symbolCommandStr += '"{0}"'.format(char)
            else:
                symbolCommandStr += ''


    def getCharCode(self, char):
        octCode = str(oct(ord(char)))[2:]
        
        digitsAccess = ""
        for char in octCode:
            digitsAccess += '"' + self.accessElementStr.format(self.digitVars[int(char)]) + '"'

        return digitsAccess
