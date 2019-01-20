"""
Base class for Token Obfuscators used by the framework
"""
from bashfuscator.core.mutators.mutator import Mutator


class TokenObfuscator(Mutator):
    """
    Base class for all token obfuscators. If an obfuscator is able to
    be deobfuscated and executed by bash at runtime, without bash
    having to execute a stub or any code, then it is a Token Obfuscator.

    :param name: name of the TokenObfuscator
    :type name: str
    :param description: short description of what the TokenObfuscator
        does
    :type description: str
    :param sizeRating: rating from 1 to 5 of how much the
        TokenObfuscator increases the size of the overall payload
    :type sizeRating: int
    :param fileWrite: True if the Token Obfuscator requires
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
        super().__init__(name, "token", description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput)

        self.fileWrite = fileWrite
        self.binariesUsed = binariesUsed
