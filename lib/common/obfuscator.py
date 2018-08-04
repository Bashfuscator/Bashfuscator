from helpers import RandomGen

class Obfuscator(object):
    """
    Base class that StringObfuscator
    and CommandObfuscator inherit from
    """
    def __init__(self):
        self.randGen = RandomGen()