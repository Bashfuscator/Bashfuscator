from bashfuscator.core.mutators.encoder import Encoder


class RotN(Encoder):
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

        encpayload = self.escapeQuotes(final)
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
        self.mangler.addPayloadLine(f"""? ?{signVar}=$(* *:printf:% %%d% %"'${{{caesar}:#0#:#1#}}"* *)* *END0""")
        self.mangler.addPayloadLine(f"? ?for^ ^((* *{count}* *=* *#1#;* *{count}* *<* *${{#{caesar}}};* *{count}* *+=* *#3#))? ?END")
        self.mangler.addPayloadLine(f"? ?do^ ^{chunk}=${{{caesar}\:{count}\:#3#}}* *END0")
        self.mangler.addPayloadLine(f"? ?{char}=${{{chunk}:#0#:#1#}}* *END0")
        self.mangler.addPayloadLine(f"""? ?{base}=$(* *:printf:% %%d% %"'${{{chunk}:#1#:#1#}}"* *)* *END0""")
        self.mangler.addPayloadLine(f"""? ?{sign}=$(* *:printf:% %%d% %"'${{{chunk}:#2#:#1#}}"* *)* *END0""")
        self.mangler.addPayloadLine(f'? ?if^ ^((* *${sign}* *>=* *${signVar}* *))? ?END')
        self.mangler.addPayloadLine(rf"""? ?then^ ^{new}=$(* *:printf:% %"\\$(* *:printf:% %%o% %"$((* *$(* *:printf:% %%d% %"'${char}"* *)* *-* *${base}* *))"* *)"* *)* *END""")
        self.mangler.addPayloadLine(f'? ?elif^ ^((* *${sign}* *<* *${signVar}* *))? ?END')
        self.mangler.addPayloadLine(rf"""? ?then^ ^{new}=$(* *:printf:% %"\\$(* *:printf:% %%o% %"$((* *$(* *:printf:% %%d% %"'${char}"* *)* *+* *${base}* *))"* *)"* *);fi? ?END0""")
        self.mangler.addPayloadLine(f"? ?{done}+=${new}? ?END")
        self.mangler.addPayloadLine("done? ?END0")
        self.mangler.addPayloadLine(f'* *:eval:% %"${done}"* *END')

        return self.mangler.getFinalPayload()
