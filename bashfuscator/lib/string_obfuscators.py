"""
String Obfuscators used by the framework.
"""
import math
import hashlib
import string

from bashfuscator.common.objects import Mutator


class StringObfuscator(Mutator):
    """
    Base class for all String Obfuscators. A String Obfuscator is a
    Mutator that builds the input string by executing a series of
    commands to build chunks of the original string, and reorganizing
    and concatenating those chunks to reassemble the original string.

    :param name: name of the StringObfuscator
    :type name: str
    :param description: short description of what the StringObfuscator 
            does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how much the 
            StringObfuscator increases the size of the overall payload
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the
            StringObfuscator increases the execution time of the overall
            payload
    :type timeRating: int
    :param binariesUsed: list of all the binaries the StringObfuscator
            uses
    :type binariesUsed: list of strs
    :param fileWrite: True if the Command Obfuscator requires 
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
        super().__init__(name, "string", description, notes, author, credits, evalWrap)

        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.fileWrite = fileWrite
        self.binariesUsed = binariesUsed
        self.originalCmd = ""
        self.payload = ""


class GlobObfuscator(StringObfuscator):
    def __init__(self, name, description, sizeRating, timeRating, author):
        super().__init__(
            name=name,
            description=description,
            sizeRating=sizeRating,
            timeRating=timeRating,
            binariesUsed=["cat", "mkdir", "rm"],
            fileWrite=True,
            author=author
        )

        self.writeableDir = ""
        self.workingDir = ""
        self.minDirLen = None
        self.maxDirLen = None
        self.sectionSize = None

    def generate(self, sizePref, userCmd, writeableDir=None):
        # TODO: create a tempDir option where the user can pick the dir to write to
        if writeableDir is None or writeableDir == "":
            self.writeableDir = ("/tmp/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen))

        self.workingDir = self.writeableDir.replace("'", "'\"'\"'")

        cmdChars = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
        cmdLen = len(cmdChars)
        cmdLogLen = int(math.ceil(math.log(cmdLen, 2)))
        if cmdLogLen <= 0:
            cmdLogLen = 1

        parts = []
        for i in range(cmdLen):
            ch = cmdChars[i]
            ch = ch.replace("'", "'\"'\"'")
            parts.append(
                "printf -- '" + ch + "' > '" + self.workingDir + "/" +
                format(i, "0" + str(cmdLogLen) + "b").replace("0", "?").replace("1", "\n") + "';"
            )
        self.randGen.randShuffle(parts)

        self.payload = ""
        self.payload += "mkdir -p '" + self.workingDir + "';"
        self.payload += "".join(parts)
        self.payload += "cat '" + self.workingDir + "'/" + "?" * cmdLogLen + ";"
        self.payload += "rm '" + self.workingDir + "'/" + "?" * cmdLogLen + ";"

    def setSizes(self, sizePref, userCmd):
        if sizePref == 0:
            self.minDirLen = self.maxDirLen = 1
            self.sectionSize = int(len(userCmd) / 3 + 1)
        elif sizePref == 1:
            self.minDirLen = 1
            self.maxDirLen = 3
            self.sectionSize = int(len(userCmd) / 10 + 1)
        elif sizePref == 2:
            self.minDirLen = 6
            self.maxDirLen = 12
            self.sectionSize = int(len(userCmd) / 100 + 1)
        elif sizePref == 3:
            self.minDirLen = 12
            self.maxDirLen = 24
            self.sectionSize = 3
        elif sizePref == 4:
            self.minDirLen = self.maxDirLen = 32
            self.sectionSize = 1


class FileGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="File Glob",
            description="Uses files and glob sorting to reassemble a string",
            sizeRating=5,
            timeRating=5,
            author="elijah-barker"
        )

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.setSizes(sizePref, userCmd)
        self.generate(sizePref, userCmd)

        return self.payload


class FolderGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="Folder Glob",
            description="Same as file glob, but better",
            sizeRating=5,
            timeRating=5,
            author="elijah-barker"
        )

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.setSizes(sizePref, userCmd)
        self.writeableDir = ("/tmp/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen))
        self.workingDir = self.writeableDir.replace("'", "'\"'\"'")

        cmdChunks = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
        parts = []
        for chunk in cmdChunks:
            self.generate(sizePref, chunk, self.writeableDir + "/" + self.randGen.randUniqueStr(self.minDirLen, self.maxDirLen))
            parts.append(self.payload)

        self.payload = "".join(parts)

        return self.payload


class HexHash(StringObfuscator):
    def __init__(self):
        super().__init__(
            name="Hex Hash",
            description="Uses the output of md5 to encode strings",
            sizeRating=5,
            timeRating=5,
            binariesUsed=["cut", "md5sum"],
            author="elijah-barker"
        )

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        obCmd = ""
        for ch in userCmd:
            hexchar = str(bytes(ch, "utf-8").hex())
            randomhash = ""

            while not hexchar in randomhash:
                m = hashlib.md5()
                randomString = self.randGen.randGenStr(1, 3)
                m.update(bytes(randomString, "utf-8"))
                randomhash = m.digest().hex()

            index = randomhash.find(hexchar)
            obCmd += 'printf "\\x$(printf -- \'' + randomString + "\'|md5sum|cut -b" + str(index + 1) + "-" + str(index + 2) + ')";'

        self.payload = obCmd

        return self.payload
