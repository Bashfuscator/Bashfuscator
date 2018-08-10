from helpers import RandomGen

class Obfuscator(object):
    """
    Base class that StringObfuscator
    and CommandObfuscator inherit from
    """
    def __init__(self, name):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.randGen = RandomGen()