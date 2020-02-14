"""
Base class for Encoders used by the framework
"""
from bashfuscator.core.mutators.mutator import Mutator


class Encoder(Mutator):
    """
    Base class for all Encoders. An Encoder is a Mutator that mutates
    the entire input given, so none of the input is visible after
    encoding.

    :param name: name of the Encoder
    :type name: str
    :param description: short description of what the Encoder does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how effectively the
        Encoder increases the size of the overall payload
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the
        Encoder increases the execution time of the overall
        payload
    :type timeRating: int
    :param binariesUsed: list of all the binaries the Encoder uses
    :type binariesUsed: list of strs
    :param fileWrite: True if the Encoder requires
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
        super().__init__(name, "encode", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

        self.binariesUsed = binariesUsed
        self.fileWrite = fileWrite
