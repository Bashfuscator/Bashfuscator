"""
Base class for String Obfuscators used by the framework
"""
from bashfuscator.core.mutators.mutator import Mutator


class StringObfuscator(Mutator):
    """
    Base class for all String Obfuscators. A String Obfuscator is a
    Mutator that builds the input string by executing a series of
    commands to build chunks of the original string, and reorganizing
    and concatenating those chunks to reassemble the original string.

    :param name: name of the StringObfuscator
    :type name: str
    :param description: short description of what the StringObfuscator
            does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how much the
            StringObfuscator increases the size of the overall payload
    :type sizeRating: int
    :param timeRating: rating from 1 to 5 of how much the
            StringObfuscator increases the execution time of the overall
            payload
    :type timeRating: int
    :param binariesUsed: list of all the binaries the StringObfuscator
            uses
    :type binariesUsed: list of strs
    :param fileWrite: True if the Command Obfuscator requires
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
        super().__init__(name, "string", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

        self.fileWrite = fileWrite
        self.binariesUsed = binariesUsed
