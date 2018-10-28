"""
Compressors used by the framework.
"""
import bz2
from base64 import b64encode
import gzip

from bashfuscator.common.objects import Mutator


class Compressor(Mutator):
    """
    Base class for all compressors. A compressor is a Mutator that
    takes input, mutates it to make it smaller, and restores it to
    the original input with a decompression stub.

    :param name: name of the Compressor
    :type name: str
    :param description: short description of what the Compressor does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how effectively the 
        Compressor decreases the size of the overall payload. Smaller
        is better
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the
        Compressor increases the execution time of the overall
        payload
    :type timeRating: int
    :param binariesUsed: list of all the binaries the Compressor uses
    :type binariesUsed: list of strs
    :param fileWrite: True if the Compressor requires 
        creating/writing to files, False otherwise
    :type fileWrite: bool
    :param notes: see :class:`bashfuscator.common.objects.Mutator`
    :type notes: str
    :param author: see :class:`bashfuscator.common.objects.Mutator`
    :type author: str
    :param credits: see :class:`bashfuscator.common.objects.Mutator`
    :type credits: str
    """

    def __init__(self, name, description, sizeRating, timeRating, binariesUsed=[], fileWrite=False, notes=None, author=None, credits=None, evalWrap=True):
        super().__init__(name, "compress", description, notes, author, credits, evalWrap)

        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.binariesUsed = binariesUsed
        self.fileWrite = fileWrite


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

    def mutate(self, sizePref, timePref, userCmd):
        compressedCmd = bz2.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.mangler.addPayloadLine('''* *:printf:^ ^{0}* *|* *:base64:^ ^-d* *|* *:bunzip2:^ ^-c* *'''.format(compressedCmd))

        return self.mangler.getFinalPayload()


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

    def mutate(self, sizePref, timePref, userCmd):
        compressedCmd = gzip.compress(userCmd.encode("utf-8"))
        compressedCmd = b64encode(compressedCmd).decode("utf-8")
        self.mangler.addPayloadLine('''* *:printf:^ ^{0}* *|* *:base64:^ ^-d* *|* *:gunzip:^ ^-c* *'''.format(compressedCmd))

        return self.mangler.getFinalPayload()
