import gzip
from base64 import b64encode

from bashfuscator.core.mutators.compressor import Compressor


class Gzip(Compressor):
    def __init__(self):
        super().__init__(
            name="Gzip",
            description="Compress command with gzip",
            sizeRating=3,
            timeRating=3,
            binariesUsed=["base64", "gunzip"],
            author="capnspacehook"
        )

    def mutate(self, userCmd):
        compressedCmd = gzip.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.mangler.addPayloadLine(f'''* *:printf:^ ^'{compressedCmd}'* *|* *:base64:^ ^-d* *|* *:gunzip:^ ^-c* *''')

        return self.mangler.getFinalPayload()
