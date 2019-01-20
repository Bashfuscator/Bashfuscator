from urllib.parse import quote_plus

from bashfuscator.core.mutators.encoder import Encoder


class UrlEncode(Encoder):
    def __init__(self):
        super().__init__(
            name="UrlEncode",
            description="Url encode command",
            sizeRating=3,
            timeRating=1,
            author="capnspacehook",
            evalWrap=False,
            postEncoder=True,
        )

    def mutate(self, userCmd):
        self.originalCmd = userCmd

        self.payload = quote_plus(userCmd)

        return self.payload
