from helpers import RandomGen
from obfuscator import Obfuscator

from binascii import hexlify
import string


class TokenObfuscator(Obfuscator):
    """
    Base class for all token obfuscators. If the obfuscator is able to
    be deobfuscated and executed by bash at runtime, without a stub, 
    then it is a token obfuscator.
    """
    def __init__(self, name, description, sizeRating, sizePref, userCmd):
        super().__init__()

        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.sizePref = sizePref
        self.userCmd = userCmd
        self.payload = ""


class AnsiCString(TokenObfuscator):
    def __init__(self, sizePref, userCmd):
        super().__init__(
            name="ANSI-C String",
            description="ANSI-C quotes a string",
            sizeRating=3,
            sizePref=sizePref,
            userCmd=userCmd)
    
    def obfuscate(self):
        obCmd = "$'\\"

        if self.sizePref == 1:
            maxChoice = 2
        else:
            maxChoice = 4

        for char in self.userCmd:
            choice = self.randGen.randChoice(maxChoice)

            # If sizePref is 3, randomly ANSI-C quote substrings of the original 
            # userCmd and randomly add empty strings
            if self.sizePref == 3 and len(obCmd) > 3 and self.randGen.probibility(33):
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
        