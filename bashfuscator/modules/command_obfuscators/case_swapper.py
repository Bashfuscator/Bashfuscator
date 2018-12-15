from bashfuscator.core.mutators.command_obfuscator import CommandObfuscator
from bashfuscator.core.mutators.command_obfuscator import Stub


class CaseSwapper(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Case Swapper",
            description="Flips the case of all alpha chars",
            sizeRating=1,
            timeRating=1,
            author="capnspacehook",
            reversible=True
        )

        self.stubs = [
            Stub(
                name="bash case swap expansion",
                sizeRating=1,
                timeRating=1,
                binariesUsed=[],
                fileWrite=False,
                escapeQuotes=True,
                stub='''? ?VAR1='CMD'* *END0* *:printf:^ ^%s^ ^"${VAR1~~}"* *END0* *'''
            )
        ]

    def mutate(self, userCmd):
        obCmd = userCmd.swapcase()

        return self.deobStub.genStub(obCmd)
