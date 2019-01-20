import bz2
from base64 import b64encode

from bashfuscator.core.mutators.compressor import Compressor


class Bzip2(Compressor):
    def __init__(self):
        super().__init__(
            name="Bzip2",
            description="Compress command with bzip2",
            sizeRating=3,
            timeRating=3,
            binariesUsed=["base64", "bunzip2"],
            author="capnspacehook"
        )

    def mutate(self, userCmd):
        compressedCmd = bz2.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.mangler.addPayloadLine(f'''* *:printf:^ ^'{compressedCmd}'* *|* *:base64:^ ^-d* *|* *:bunzip2:^ ^-c* *''')

        return self.mangler.getFinalPayload()
