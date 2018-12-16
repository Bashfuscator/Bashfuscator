"""
Base class all modules inherit from
"""
import string

from bashfuscator.core.engine.mangler import Mangler
from bashfuscator.core.engine.random import RandomGen


class Mutator(object):
    """
    Base class that all Mutators inherit from. Automatically generates
    a longName attribute that is used to choose Mutators on the
    command line, and stores a
    :class:`bashfuscator.common.random.RandomGen` object.

    :param name: Name of the Mutator
    :type name: str
    :param mutatorType: child Mutator's type
    :type mutatorType: lowercase str
    :param notes: any additional information useful to know when using
        the Mutator
    :type notes: str
    :param author: creator of the Mutator
    :type author: str
    :param credits: whom or where inpiration for or the complete method
        of mutation was found at. Should be the name/handle of the
        person who inspired you, and/or a link to where you got the
        idea from. See
        :class:`bashfuscator.lib.token_obfuscators.AnsiCQuote` for an
        example
    :type credits: str
    """

    def __init__(self, name, mutatorType, description, sizeRating, timeRating, notes, author, credits, evalWrap, unreadableOutput=False):
        self.name = name
        self.mutatorType = mutatorType
        self.description = description
        self.longName = self.mutatorType + "/" + self.name.replace(" ", "_").lower()
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.notes = notes
        self.author = author
        self.credits = credits
        self.evalWrap = evalWrap
        self.unreadableOutput = unreadableOutput

        self.sizePref = None
        self.timePref = None
        self.writeDir = None
        self._obfuscatedCmd = None

        self.mangler = Mangler()
        self.randGen = self.mangler.randGen

    def escapeQuotes(self, inCmd):
        return inCmd.replace("'", "'\"'\"'")

    def strToArrayElements(self, inCmd):
        # escape all Ascii unprintable chars, as well as all special chars and space chars
        escapeChars = string.punctuation + " " + "".join(chr(i) for i in range(1, 33)) + chr(127)
        ansicQuoteChars = [chr(10), chr(11), chr(12), chr(13)]
        arrayElementsStr = "* *"

        for char in inCmd:
            if char in escapeChars:
                if char in ansicQuoteChars:
                    char = self.mangler._getAnsiCQuotedStr(char)
                else:
                    char = "\\" + char

            arrayElementsStr += char + "% %"

        return arrayElementsStr[:-3] + "* *"
