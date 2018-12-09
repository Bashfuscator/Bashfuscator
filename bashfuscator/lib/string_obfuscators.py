"""
String Obfuscators used by the framework.
"""
import math
import hashlib
import string

from bashfuscator.common.helpers import escapeQuotes
from bashfuscator.common.objects import Mutator
from base64 import b64encode


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

    def __init__(self, name, description, sizeRating, timeRating, binariesUsed=[], fileWrite=False, notes=None, author=None, credits=None, evalWrap=True, unreadableOutput=False):
        super().__init__(name, "string", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

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
                f"* *:printf:^ ^%s^ ^'DATA'? ?>? ?'{self.workingDir}/" +
                format(i, "0" + str(cmdLogLen) + "b").replace("0", "?").replace("1", "\n") + "'* *END0": cmdCharsSection
            })

        # TODO: randomize ordering of 'rm' statements
        self.mangler.addPayloadLine(f"* *:mkdir:^ ^-p^ ^'{self.workingDir}'* *END0")
        self.mangler.addLinesInRandomOrder(printLines)
        self.mangler.addPayloadLine(f"* *:cat:^ ^'{self.workingDir}'/{'?' * cmdLogLen}* *END0")
        self.mangler.addPayloadLine(f"* *:rm:^ ^'{self.workingDir}'/{'?' * cmdLogLen}* *END0")

    def setSizes(self, userCmd):
        if self.sizePref == 1:
            self.sectionSize = int(len(userCmd) / 10 + 1)
        elif self.sizePref == 2:
            self.sectionSize = int(len(userCmd) / 100 + 1)
        elif self.sizePref == 3:
            self.sectionSize = 1

        self.startingDir = escapeQuotes(self.writeDir + self.randGen.randUniqueStr())


class FileGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="File Glob",
            description="Uses files and glob sorting to reassemble a string",
            sizeRating=5,
            timeRating=5,
            author="Elijah-Barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)
        self.generate(userCmd)
        self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.workingDir}'END0* *")

        return self.mangler.getFinalPayload()


class FolderGlob(GlobObfuscator):
    def __init__(self):
        super().__init__(
            name="Folder Glob",
            description="Same as file glob, but better",
            sizeRating=5,
            timeRating=5,
            author="Elijah-Barker"
        )

    def mutate(self, userCmd):
        self.setSizes(userCmd)

        cmdChunks = [userCmd[i:i + self.sectionSize] for i in range(0, len(userCmd), self.sectionSize)]

        for chunk in cmdChunks:
            self.generate(chunk, self.randGen.randUniqueStr())
            self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.workingDir}'END0")

        self.mangler.addPayloadLine(f"* *:rmdir:^ ^'{self.startingDir}'END0* *")

        return self.mangler.getFinalPayload()


class HexHash(StringObfuscator):
    def __init__(self):
        super().__init__(
            name="Hex Hash",
            description="Uses the output of md5 to encode strings",
            sizeRating=5,
            timeRating=5,
            binariesUsed=["cut", "md5sum"],
            author="Elijah-Barker"
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
            self.mangler.addPayloadLine(f"""* *:printf:^ ^"\\x$(* *:printf:^ ^%s^ ^'{randomString}'* *|* *:md5sum:* *|* *:cut:^ ^-b^ ^{str(index + 1)}-{str(index + 2)}* *)"* *END0""")

        self.mangler.addJunk()

        return self.mangler.getFinalPayload()


class XorNonNull(StringObfuscator):
    def __init__(self):
        super().__init__(
            name="Xor Non Null",
            description="Uses the xor operator in perl to encode strings",
            sizeRating=5,
            timeRating=5,
            binariesUsed=["perl"],
            notes="May contain non-printable Ascii characters",
            author="Elijah-Barker",
            unreadableOutput=True
        )

    def genXorKey(self, keyLen, userCmd):
        xorKeyBytes = bytearray(self.randGen.randGenStr(minStrLen=keyLen, maxStrLen=keyLen), "utf-8")

        for i in range(keyLen):
            nullchars = set(userCmd[i::keyLen])
            if chr(xorKeyBytes[i]) in nullchars:
                # copies the current char set for initialization of blacklist
                charBlackList = self.randGen._randStrCharList[:]

                for char in nullchars:
                    if char in charBlackList:
                        charBlackList.remove(char)

                if len(charBlackList) > 0:
                    # Replace character that would cause a null byte
                    xorKeyBytes[i] = int.from_bytes(bytes(self.randGen.randSelect(charBlackList), "utf-8"), byteorder='big')
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

        if self.sizePref == 1:
            keyLen = int(len(userCmd) / 100 + 1)
        elif self.sizePref == 2:
            keyLen = int(len(userCmd) / 10 + 1)
        elif self.sizePref == 3:
            keyLen = len(userCmd)

        xorKeyBytes = None
        while not xorKeyBytes:
            keyLen = keyLen + 1
            xorKeyBytes = self.genXorKey(keyLen, userCmd)

        cmdBytes = bytearray(userCmd, 'utf-8')
        for i in range(len(userCmd)):
            cmdBytes[i] ^= xorKeyBytes[i % keyLen]

        xorKey = escapeQuotes(xorKeyBytes.decode("utf-8"))
        data = escapeQuotes(cmdBytes.decode("utf-8"))

        variableInstantiations = {
            f"? ?{cmdVar}='DATA'* *END0": data,
            f"? ?{keyVar}='{xorKey}'* *END0": None
        }
        self.mangler.addLinesInRandomOrder(variableInstantiations)
        self.mangler.addPayloadLine(f"? ?for^ ^((* *{iteratorVar}=0* *END* *{iteratorVar}* *<* *${{#{cmdVar}}}* *END* *{iteratorVar}* *++* *))? ?END")
        self.mangler.addPayloadLine(f'''? ?do^ ^{cmdCharVar}="${{{cmdVar}:${iteratorVar}:1? ?}}"* *END0''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="$((* *{iteratorVar}* * %* *${{#{keyVar}}}* *))"* *END0''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="${{{keyVar}:${keyCharVar}:1}}"* *END0''')
        perlEscapes = [
            f'''? ?[[^ ^"${cmdCharVar}"^ ^==^ ^"'"^ ^]]? ?&&? ?{cmdCharVar}="\\\\'"* *END''',
            f'''? ?[[^ ^"${keyCharVar}"^ ^==^ ^"'"^ ^]]? ?&&? ?{keyCharVar}="\\\\'"* *END''',
            f"""? ?[[^ ^"${cmdCharVar}"^ ^==^ ^"\\\\"^ ^]]? ?&&? ?{cmdCharVar}='\\\\'* *END""",
            f"""? ?[[^ ^"${keyCharVar}"^ ^==^ ^"\\\\"^ ^]]? ?&&? ?{keyCharVar}='\\\\'* *END"""
        ]
        self.mangler.addLinesInRandomOrder(perlEscapes)
        self.mangler.addPayloadLine(f'''? ?:perl:^ ^-e^ ^"? ?print^ ^'${cmdCharVar}'? ?^? ?'${keyCharVar}'? ?"* *END''')
        self.mangler.addPayloadLine("? ?done? ?END0")

        return self.mangler.getFinalPayload()

class RotN(StringObfuscator):
    def __init__(self):
        super().__init__(
            name="RotN",
            description="Offsets each character a random number of times across the ASCII charset",
            sizeRating=1,
            timeRating=1,
            binariesUsed=[],
            author="343iChurch",
            evalWrap=False,
            unreadableOutput=True
        )

    # TODO: randomize +,- chars, replace base64 encoded blobs with chars that the incoming char is rotated by
    def mutate(self, userCmd):
        rotd = []
        rotn = []
        sign = []
        final = ""
        numsign = ""
        for ch in userCmd:
            badrot = True
            gen = 0
            while badrot:
                minus = False
                plus = False
                signarr = ["+", "-"]
                gen = self.randGen.randGenNum(1, 127)

                if ord(ch) - gen > 0:
                    numsign = "-"
                    minus = True
                if ord(ch) + gen <= 127:
                    numsign = "+"
                    plus = True
                if minus and plus:
                    numsign = self.randGen.randSelect(signarr)
                # the rotated character can't be a null byte
                if (minus or plus) and (ord(ch) + gen != 0):
                    badrot = False

            sign.append(numsign)
            rotd.append(ord(ch))
            rotn.append(gen)

        signChar = chr(self.randGen.randGenNum(2, 127))
        final += signChar
        randSignChar = ""

        for i, num in enumerate(rotd):
            if sign[i] == "+":
                rotd[i] += rotn[i]
                randSignChar = chr(self.randGen.randGenNum(ord(signChar), 127))
            elif sign[i] == "-":
                rotd[i] -= rotn[i]
                randSignChar = chr(self.randGen.randGenNum(1, ord(signChar) - 1))

            final += chr(rotd[i])
            final += chr(rotn[i])
            final += randSignChar

        encpayload = escapeQuotes(final)
        caesar = self.randGen.randGenVar()
        signVar = self.randGen.randGenVar()
        count = self.randGen.randGenVar()
        chunk = self.randGen.randGenVar()
        char = self.randGen.randGenVar()
        base = self.randGen.randGenVar()
        sign = self.randGen.randGenVar()
        new = self.randGen.randGenVar()
        done = self.randGen.randGenVar()

        # TODO: put signVar in random position in encpayload
        self.mangler.addPayloadLine(f"? ?{caesar}='{encpayload}'* *END0")
        self.mangler.addPayloadLine(f"""? ?{signVar}=$(* *:printf:% %%d% %"'${{{caesar}\:0\:1}}"* *)* *END0""")
        self.mangler.addPayloadLine(f"? ?for^ ^((* *{count}* *=* *1;* *{count}* *<* *${{#{caesar}}};* *{count}* *+=* *3))? ?END")
        self.mangler.addPayloadLine(f"? ?do^ ^{chunk}=${{{caesar}\:{count}\:3}}* *END0")
        self.mangler.addPayloadLine(f"? ?{char}=${{{chunk}\:0\:1}}* *END0")
        self.mangler.addPayloadLine(f"""? ?{base}=$(* *:printf:% %%d% %"'${{{chunk}\:1\:1}}"* *)* *END0""")
        self.mangler.addPayloadLine(f"""? ?{sign}=$(* *:printf:% %%d% %"'${{{chunk}\:2\:1}}"* *)* *END0""")
        self.mangler.addPayloadLine(f'? ?if^ ^((* *${sign}* *>=* *${signVar}* *))? ?END')
        self.mangler.addPayloadLine(rf"""? ?then^ ^{new}=$(* *:printf:% %"\\$(* *:printf:% %%o% %"$((* *$(* *:printf:% %%d% %"'${char}"* *)* *-* *${base}* *))"* *)"* *)* *END""")
        self.mangler.addPayloadLine(f'? ?elif^ ^((* *${sign}* *<* *${signVar}* *))? ?END')
        self.mangler.addPayloadLine(rf"""? ?then^ ^{new}=$(* *:printf:% %"\\$(* *:printf:% %%o% %"$((* *$(* *:printf:% %%d% %"'${char}"* *)* *+* *${base}* *))"* *)"* *);fi? ?END0""")
        self.mangler.addPayloadLine(f"? ?{done}+=${new}? ?END")
        self.mangler.addPayloadLine("done? ?END0")
        self.mangler.addPayloadLine(f'* *:eval:% %"${done}"* *END')

        return self.mangler.getFinalPayload()
