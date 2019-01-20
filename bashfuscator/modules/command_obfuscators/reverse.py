from bashfuscator.core.mutators.command_obfuscator import CommandObfuscator
from bashfuscator.core.mutators.command_obfuscator import Stub


class Reverse(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Reverse",
            description="Reverses a command",
            sizeRating=1,
            timeRating=1,
            author="capnspacehook",
            reversible=True
        )

        self.stubs = [
            Stub(
                name="printf rev",
                sizeRating=1,
                timeRating=1,
                binariesUsed=["rev"],
                fileWrite=False,
                escapeQuotes=True,
                stub="""* *:printf:^ ^%s^ ^'CMD'* *|* *:rev:* *END0* *"""
            ),
            Stub(
                name="herestring rev",
                sizeRating=1,
                timeRating=1,
                binariesUsed=["rev"],
                fileWrite=False,
                escapeQuotes=True,
                stub="""* *:rev:^ ^<<<? ?'CMD'* *END0* *"""
            )
        ]

    def mutate(self, userCmd):
        obCmd = userCmd[::-1]

        return self.deobStub.genStub(obCmd)
