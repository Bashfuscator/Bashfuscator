from helpers import RandomGen
from obfuscator import Obfuscator

from binascii import hexlify
import string


class StringObfuscator(Obfuscator):
    """
    Base class for all string obfuscators. Every
    string obfuscator should have an obfuscate()
    method that takes no params and returns an obfuscated
    version of self.userCmd
    """
    def __init__(self, name, description, sizeRating, sizePref, userCmd):
        super().__init__()

        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.sizePref = sizePref
        self.userCmd = userCmd
        self.payload = ""


class AnsiCString(StringObfuscator):
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
        elif self.sizePref == 2:
            maxChoice = 3
        else:
            maxChoice = 4

        for char in self.userCmd:
            choice = self.randGen.randChoice(maxChoice)

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
