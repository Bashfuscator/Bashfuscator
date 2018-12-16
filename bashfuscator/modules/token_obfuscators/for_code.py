from bashfuscator.core.mutators.token_obfuscator import TokenObfuscator


class ForCode(TokenObfuscator):
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

        cmdIndexes = "".join([f"#{str(i)}#% %" for i in ogCmdIdxes])[:-3]

        shuffledCmd = self.strToArrayElements(shuffledCmd)

        charArrayVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine(f"? ?{charArrayVar}=({shuffledCmd})* *END0")

        indexVar = self.randGen.randGenVar()
        self.mangler.addPayloadLine(f"? ?for^ ^{indexVar}^ ^in^ ^{cmdIndexes}* *END")

        # randomly choose between the two different for loop syntaxes
        if self.randGen.probibility(50):
            self.mangler.addPayloadLine(f'? ?{{^ ^:printf:^ ^%s^ ^"${{{charArrayVar}[* *${indexVar}* *]}}"* *;? ?}}? ?END* *')

        else:
            self.mangler.addPayloadLine(f'? ?do^ ^:printf:^ ^%s^ ^"${{{charArrayVar}[* *${indexVar}* *]}}"* *;? ?done? ?END* *')

        return self.mangler.getFinalPayload()
