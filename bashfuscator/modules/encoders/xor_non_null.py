from bashfuscator.core.mutators.encoder import Encoder


class XorNonNull(Encoder):
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
                charWhiteList = self.randGen._randStrCharList[:]

                for char in nullchars:
                    if char in charWhiteList:
                        charWhiteList.remove(char)

                if len(charWhiteList) > 0:
                    # Replace character that would cause a null byte
                    xorKeyBytes[i] = int.from_bytes(bytes(self.randGen.randSelect(charWhiteList), "utf-8"), byteorder='big')
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

        xorKey = self.escapeQuotes(xorKeyBytes.decode("utf-8"))
        data = self.escapeQuotes(cmdBytes.decode("utf-8"))

        variableInstantiations = {
            f"? ?{cmdVar}='DATA'* *END0": data,
            f"? ?{keyVar}='{xorKey}'* *END0": None
        }
        self.mangler.addLinesInRandomOrder(variableInstantiations)
        self.mangler.addPayloadLine(f"? ?for^ ^((* *{iteratorVar}=0* *;* *{iteratorVar}* *<* *${{#{cmdVar}}}* *;* *{iteratorVar}* *++* *))? ?END")
        self.mangler.addPayloadLine(f'''? ?do^ ^{cmdCharVar}="${{{cmdVar}:${iteratorVar}:#1#? ?}}"* *END0''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="$((* *{iteratorVar}* * %* *${{#{keyVar}}}* *))"* *END0''')
        self.mangler.addPayloadLine(f'''? ?{keyCharVar}="${{{keyVar}:${keyCharVar}:#1#}}"* *END0''')
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
