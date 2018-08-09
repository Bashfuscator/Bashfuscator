from binascii import hexlify
import string

from helpers import RandomGen
from obfuscator import Obfuscator


class TokenObfuscator(Obfuscator):
    """
    Base class for all token obfuscators. If the obfuscator is able to
    be deobfuscated and executed by bash at runtime, without a stub, 
    then it is a token obfuscator.

    :param name: name of the Token Obfuscator
    :param description: short description of what the TokenObfuscator does
    :param sizeRating: rating from 1 to 5 of how much the TokenObfuscator 
    increases the size of the overall payload
    """
    def __init__(self, name, description, sizeRating):
        super().__init__(name)

        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.originalCmd = ""
        self.payload = ""


class AnsiCQuote(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="ANSI-C Quote",
            description="ANSI-C quotes a string",
            sizeRating=3
        )
    
        self.SUBSTR_QUOTE_PROB = 33

    def obfuscate(self, sizePref, userCmd):
        self.originalCmd = userCmd
        
        obCmd = "$'\\"

        if sizePref == 1:
            maxChoice = 2
        else:
            maxChoice = 4

        for char in self.originalCmd:
            choice = self.randGen.randChoice(maxChoice)

            # If sizePref is 3, randomly ANSI-C quote substrings of the original 
            # userCmd and randomly add empty strings
            if sizePref == 3 and len(obCmd) > 3 and self.randGen.probibility(self.SUBSTR_QUOTE_PROB):
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
        