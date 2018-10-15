"""
Encoders used by the framework.
"""
from base64 import b64encode
from urllib.parse import quote_plus

from bashfuscator.common.objects import Mutator


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
    :param notes: see :class:`bashfuscator.common.objects.Mutator`
    :type notes: str
    :param author: see :class:`bashfuscator.common.objects.Mutator`
    :type author: str
    :param credits: see :class:`bashfuscator.common.objects.Mutator`
    :type credits: str
    """

    def __init__(self, name, description, sizeRating, timeRating, notes=None, author=None, credits=None):
        super().__init__(name, "encode", notes, author, credits)

        self.description = description
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.originalCmd = ""
        self.payload = ""


class Base64(Encoder):
    def __init__(self):
        super().__init__(
            name="Base64",
            description="Base64 encode command",
            sizeRating=2,
            timeRating=1,
            author="capnspacehook"
        )

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        b64EncodedBlob = b64encode(userCmd.encode("utf-8"))
        b64EncodedBlob = b64EncodedBlob.decode("utf-8").replace("\n", "")
        self.payload = "printf {0}|base64 -d".format(b64EncodedBlob)

        return self.payload


class UrlEncode(Encoder):
    def __init__(self):
        super().__init__(
            name="UrlEncode",
            description="Url encode command",
            sizeRating=3,
            timeRating=1,
            author="capnspacehook"
        )

    def mutate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd

        self.payload = quote_plus(userCmd)

        return self.payload
