from base64 import b64encode

from bashfuscator.core.mutators.encoder import Encoder


class Base64(Encoder):
    def __init__(self):
        super().__init__(
            name="Base64",
            description="Base64 encode command",
            sizeRating=2,
            timeRating=1,
            binariesUsed=["base64"],
            author="capnspacehook"
        )

    def mutate(self, userCmd):

        b64EncodedBlob = b64encode(userCmd.encode("utf-8"))
        b64EncodedBlob = b64EncodedBlob.decode("utf-8").replace("\n", "")
        self.mangler.addPayloadLine(f'* *:printf:^ ^"{b64EncodedBlob}"* *|* *:base64:^ ^-d* *')

        return self.mangler.getFinalPayload()
