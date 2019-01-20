import hashlib

from bashfuscator.core.mutators.string_obfuscator import StringObfuscator


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
            self.mangler.addPayloadLine(f"""* *:printf:^ ^"\\x$(* *:printf:^ ^%s^ ^'{randomString}'* *|* *:md5sum:* *|* *:cut:^ ^-b^ ^&{str(index + 1)}&-&{str(index + 2)}&* *)"* *END0""")

        self.mangler.addJunk()

        return self.mangler.getFinalPayload()
