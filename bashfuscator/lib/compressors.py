import bz2
from base64 import b64encode
import gzip

from bashfuscator.common.objects import Mutator


class Compressor(Mutator):
    def __init__(self, name, description, sizeRating, timeRating, notes=None, author=None, credits=None):
        super().__init__(name, "compress", notes, author, credits)
        
        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""


class Bzip2(Compressor):
    def __init__(self):
        super().__init__(
            name="Bzip2",
            description="Compress command with bzip2",
            sizeRating=3,
            timeRating=3,
            author="capnspacehook"
        )

    def compress(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        compressedCmd = bz2.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.payload = '''printf {0}|base64 -d|bunzip2 -c'''.format(compressedCmd)

        return self.payload


class Gzip(Compressor):
    def __init__(self):
        super().__init__(
            name="Gzip",
            description="Compress command with gzip",
            sizeRating=3,
            timeRating=3,
            author="capnspacehook"
        )

    def compress(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        compressedCmd = gzip.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.payload = '''printf {0}|base64 -d|gunzip -c'''.format(compressedCmd)

        return self.payload
