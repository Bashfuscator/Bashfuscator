import bz2
from base64 import b64encode
import gzip

from bashfuscator.common.objects import Mutator


class Compressor(Mutator):
    def __init__(self, name, description, sizeRating, timeRating, credits=None):
        super().__init__(name, "compress", credits)
        
        self.name = name
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""


class Bzip2(Compressor):
    def __init__(self):
        super().__init__(
            "Bzip2",
            "Compress command with bzip2",
            3,
            3,
            "capnspacehook"
        )

    def compress(self, userCmd):
        self.originalCmd = userCmd

        compressedCmd = bz2.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.payload = '''printf {0}|base64 -d|bunzip2 -c'''.format(compressedCmd)

        return self.payload


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

        compressedCmd = gzip.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.payload = '''printf {0}|base64 -d|gunzip -c'''.format(compressedCmd)

        return self.payload
