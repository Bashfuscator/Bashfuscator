"""
String Obfuscators used by the framework.
"""
import math
import hashlib
import string

from bashfuscator.common.helpers import escapeQuotes, strToArrayElements
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


class GlobObfuscator(StringObfuscator):
    def __init__(self, name, description, sizeRating, timeRating, author):
        super().__init__(
            name=name,
            description=description,
            sizeRating=sizeRating,
            timeRating=timeRating,
            binariesUsed=["cat", "mkdir", "rm", "rmdir"],
            fileWrite=True,
            author=author
        )

        self.workingDir = None
        self.minDirLen = None
        self.maxDirLen = None
        self.sectionSize = None

    def generate(self, userCmd, writeableDir=None):
        if writeableDir:
            self.workingDir = self.startingDir + "/" + escapeQuotes(writeableDir)
        else:
            self.workingDir = self.startingDir

        cmdChars = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]
        cmdLen = len(cmdChars)
        cmdLogLen = int(math.ceil(math.log(cmdLen, 2)))
        if cmdLogLen <= 0:
            cmdLogLen = 1

        printLines = {}
        for i in range(cmdLen):
            cmdCharsSection = cmdChars[i]
            cmdCharsSection = escapeQuotes(cmdCharsSection)
            printLines.update({
                "* *:printf:^ ^%s^ ^'DATA'^ ^>^ ^'" + self.workingDir + "/" +
                format(i, "0" + str(cmdLogLen) + "b").replace("0", "?").replace("1", "\n") + "'* *END": cmdCharsSection
            })

        # TODO: randomize ordering of 'rm' statements
        self.mangler.addPayloadLine("* *:mkdir:^ ^-p^ ^'" + self.workingDir + "'* *END")
        self.mangler.addLinesInRandomOrder(printLines)
        self.mangler.addPayloadLine("* *:cat:^ ^'" + self.workingDir + "'/" + "?" * cmdLogLen + "* *END")
        self.mangler.addPayloadLine("* *:rm:^ ^'" + self.workingDir + "'/" + "?" * cmdLogLen + "* *END")

    def setSizes(self, userCmd):
        if self.sizePref == 1:
            self.sectionSize = int(len(userCmd) / 10 + 1)
        elif self.sizePref == 2:
            self.sectionSize = int(len(userCmd) / 100 + 1)
        elif self.sizePref == 3:
            self.sectionSize = 3

        self.startingDir = escapeQuotes(self.writeDir + self.randGen.randUniqueStr())


class FileGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="File Glob",
            description="Uses files and glob sorting to reassemble a string",
            sizeRating=5,
            timeRating=5,
            author="elijah-barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)
        self.generate(userCmd)
        self.mangler.addPayloadLine("* *:rmdir:^ ^'" + self.workingDir + "'END* *")

        return self.mangler.getFinalPayload()


class FolderGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="Folder Glob",
            description="Same as file glob, but better",
            sizeRating=5,
            timeRating=5,
            author="elijah-barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)

        cmdChunks = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]

        for chunk in cmdChunks:
            self.generate(chunk, self.randGen.randUniqueStr())
            self.mangler.addPayloadLine("* *:rmdir:^ ^'" + self.workingDir + "'END")

        self.mangler.addPayloadLine("* *:rmdir:^ ^'" + self.startingDir + "'END* *")

        return self.mangler.getFinalPayload()


class ForCode(StringObfuscator):
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

        cmdIndexes = "".join([str(i) + " " for i in ogCmdIdxes])[:-1]

        shuffledCmd = strToArrayElements(shuffledCmd)

        charArrayVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine("? ?{0}=({1})* *END".format(charArrayVar, shuffledCmd))

        indexVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine("^ ^for^ ^{0}^ ^in^ ^{1}* *END0".format(indexVar, cmdIndexes))

        # randomly choose between the two different for loop syntaxes
        if self.randGen.probibility(50):
            self.mangler.addPayloadLine('? ?{{^ ^:printf:^ ^%s^ ^"${{{0}[${1}]}}"* *;? ?}}? ?END0* *'.format(charArrayVar, indexVar))

        else:
            self.mangler.addPayloadLine('? ?do^ ^:printf:^ ^%s^ ^"${{{0}[${1}]}}"* *;? ?done? ?END0* *'.format(charArrayVar, indexVar))

        return self.mangler.getFinalPayload()


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

    def mutate(self, userCmd):
        for ch in userCmd:
            hexchar = str(bytes(ch, "utf-8").hex())
            randomhash = ""

            while not hexchar in randomhash:
                m = hashlib.md5()
                randomString = self.randGen.randGenStr()
                m.update(bytes(randomString, "utf-8"))
                randomhash = m.hexdigest()

            index = randomhash.find(hexchar)
            self.mangler.addPayloadLine('* *:printf:^ ^"\\x$(:printf:^ ^%s^ ^\'' + randomString + "\'* *|* *:md5sum:* *|* *:cut:^ ^-b^ ^" + str(index + 1) + "-" + str(index + 2) + '* *)"* *END')

        self.mangler.addJunk()

        return self.mangler.getFinalPayload()


class XorNonNull(StringObfuscator):
    def __init__(self):
        super().__init__(
            name="xor non null",
            description="Uses the xor operator in perl to encode strings",
            sizeRating=5,
            timeRating=5,
            binariesUsed=["perl"],
            author="elijah-barker"
        )

    def genXorKey(self, keyLen, userCmd):
        
        xorKeyBytes = bytearray(self.randGen.randGenStr(minStrLen=keyLen, maxStrLen=keyLen), "utf8")
        
        for i in range(keyLen):
            nullchars = set(userCmd[i::keyLen])
            if chr(xorKeyBytes[i]) in nullchars:
                charBlackList = list(self.randGen._randStrCharList[:])
                for char in nullchars:
                    if char in charBlackList:
                        charBlackList.remove(char)
                if len(charBlackList) > 0:
                    # Replace character that would cause a null byte
                    xorKeyBytes[i] = int.from_bytes(bytes(self.randGen.randGenStr(minStrLen=1, maxStrLen=1, charList=charBlackList), "utf8"), byteorder='big')
                else:
                    # Die: Impossible key length modulus (there are no
                    # characters that don't cause a null byte)
                    # solution: try a different key length
                    return None
        return xorKeyBytes

    def mutate(self, userCmd):
        
        cmdVar = self.randGen.randGenVar()
        keyVar = self.randGen.randGenVar()
        cmdCharVar = self.randGen.randGenVar()
        keyCharVar = self.randGen.randGenVar()
        iteratorVar = self.randGen.randGenVar()
        
        keyLen = 40 # TODO: base on sizePref
        xorKeyBytes = None
        while xorKeyBytes is None:
            keyLen = keyLen + 1
            xorKeyBytes = self.genXorKey(keyLen, userCmd)
        
        cmdBytes = bytearray(userCmd, 'utf8')
        for i in range(len(userCmd)):
            cmdBytes[i] ^= xorKeyBytes[i%keyLen]
            
        xorKey = escapeQuotes(xorKeyBytes.decode("utf8"))
        data = escapeQuotes(cmdBytes.decode("utf8"))

        self.mangler.addPayloadLine(f"? ?{cmdVar}='DATA'* *END", data)
        self.mangler.addPayloadLine(f"? ?{keyVar}='{xorKey}'* *END")
        self.mangler.addPayloadLine(f"? ?for^ ^((* *{iteratorVar}=0* *;* *{iteratorVar}* *<* *${{#{cmdVar}}}* *;* *{iteratorVar}* *++* *))? ?END0")
        self.mangler.addPayloadLine(f'''? ?do^ ^{cmdCharVar}="${{{cmdVar}:${iteratorVar}:1? ?}}"* *END''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="$(({iteratorVar}%${{#{keyVar}}}))"* *END''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="${{{keyVar}:${keyCharVar}:1}}"* *END''')
        perlEscapes = [
            f'''? ?[[^ ^"${cmdCharVar}"^ ^==^ ^"'"^ ^]]? ?&&? ?{cmdCharVar}="\\\\'"* *END0''',
            f'''? ?[[^ ^"${keyCharVar}"^ ^==^ ^"'"^ ^]]? ?&&? ?{keyCharVar}="\\\\'"* *END0''',
            f"""? ?[[^ ^"${cmdCharVar}"^ ^==^ ^"\\\\"^ ^]]? ?&&? ?{cmdCharVar}='\\\\'* *END0""",
            f"""? ?[[^ ^"${keyCharVar}"^ ^==^ ^"\\\\"^ ^]]? ?&&? ?{keyCharVar}='\\\\'* *END0"""
        ]
        self.mangler.addLinesInRandomOrder(perlEscapes)
        self.mangler.addPayloadLine(f'''? ?:perl:^ ^-e^ ^"print '${cmdCharVar}'^'${keyCharVar}'"* *END0''')
        self.mangler.addPayloadLine("? ?done? ?END")

        return self.mangler.getFinalPayload()

