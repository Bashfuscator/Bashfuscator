from bashfuscator.common.objects import Mutator


class Encoder(Mutator):
    def __init__(self, name, description, sizeRating, timeRating, credits=None):
        super().__init__(name, "encoder", credits)
        
        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""

    
class Base64(Encoder):
    def __init__(self):
        super().__init__(
            "Base64",
            "Base64 encode command",
            2,
            1,
            "capnspacehook"
        )

    def encode(self, userCmd):
        self.originalCmd = userCmd

        self.payload = userCmd.encode("base64").replace("\n", "")
        self.payload = '''eval "$(printf {0}|base64 -d)"'''.format(self.payload)

        return self.payload


class UrlEncode(Encoder):
    def __init__(self):
        super().__init__(
            "UrlEncode",
            "Url encode command",
            3,
            1,
            "capnspacehook"
        )

    def encode(self, userCmd):
        self.originalCmd = userCmd

        for char in userCmd:
            self.payload += char + "\x00"

        return self.payload