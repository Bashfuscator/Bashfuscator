"""
Base classes used throughout the framework.
"""
import re

from bashfuscator.common.random import RandomGen
from bashfuscator.core.mangler import Mangler


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

    def __init__(self, name, mutatorType, description, notes, author, credits, evalWrap, postEncoder=False):
        self.name = name
        self.mutatorType = mutatorType
        self.description = description
        self.longName = self.mutatorType + "/" + self.name.replace(" ", "_").lower()
        self.notes = notes
        self.author = author
        self.credits = credits
        self.evalWrap = evalWrap
        self.postEncoder = postEncoder

        self.sizePref = None
        self.timePref = None
        self.writeDir = None
        self._originalCmd = ""
        self._obfuscatedCmd = ""

        self.mangler = Mangler()
        self.randGen = self.mangler.randGen
