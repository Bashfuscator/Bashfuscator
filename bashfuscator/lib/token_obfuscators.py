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
                obCmd = obCmd[:-1] + "'" + "".join("''" for x in range(self.randGen.randGenNum(0, 5))) + "$'\\"

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
        
