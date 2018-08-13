import gzip

from bashfuscator.common.objects import Mutator


class Compressor(Mutator):
    def __init__(self, name, description, sizeRating, timeRating, credits=None):
        super().__init__(name, "compressor", credits)
        
        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""


class Gzip(Compressor):
    def __init__(self):
        super().__init__(
            "Gzip",
            "Compress command with gzip",
            3,
            3,
            "capnspacehook"
        )

    def compress(self, userCmd):
        self.originalCmd = userCmd

        self.payload = gzip.compress(userCmd)
        self.payload = '''eval "$(printf {0}|gunzip -c)"'''.format(self.payload)
