from urllib.parse import quote_plus

from bashfuscator.common.objects import Mutator


class Encoder(Mutator):
    def __init__(self, name, description, sizeRating, timeRating, notes=None, author=None, credits=None):
        super().__init__(name, "encode", notes, author, credits)
        
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""

    
class Base64(Encoder):
    def __init__(self):
        super().__init__(
            name="Base64",
            description="Base64 encode command",
            sizeRating=2,
            timeRating=1,
            author="capnspacehook"
        )

    def encode(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.payload = userCmd.encode("base64").replace("\n", "")
        self.payload = '''eval "$(printf {0}|base64 -d)"'''.format(self.payload)

        return self.payload


class UrlEncode(Encoder):
    def __init__(self):
        super().__init__(
            name="UrlEncode",
            description="Url encode command",
            sizeRating=3,
            timeRating=1,
            author="capnspacehook"
        )

    def encode(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.payload = quote_plus(userCmd)

        return self.payload