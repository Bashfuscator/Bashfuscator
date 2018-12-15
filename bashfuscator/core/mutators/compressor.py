"""
Base class for Compressors used by the framework
"""
from bashfuscator.core.mutators.mutator import Mutator


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

    def __init__(self, name, description, sizeRating, timeRating, binariesUsed=[], fileWrite=False, notes=None, author=None, credits=None, evalWrap=True, unreadableOutput=False):
        super().__init__(name, "compress", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

        self.binariesUsed = binariesUsed
        self.fileWrite = fileWrite
