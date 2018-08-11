import string
import re
import random


class RandomGen(object):
    """
    Wrapper around random.SystemRandom().
    Provided for ease of use and to avoid
    having to initialize a SystemRandom object
    every time something random is desired.
    @capnspacehook
    """
    randGen = random.SystemRandom()
    generatedVars = []

    def randGenNum(self, min, max):
        """
        Returns a random number exclusively from
        min to max
        """
        return RandomGen.randGen.randint(min, max)

    def randChoice(self, max):
        """
        Returns a random number from 0 to max - 1.
        Useful when a random choice is needed
        """
        return self.randGenNum(0, max - 1)

    def probibility(self, percent):
        """
        Randomly generates a number from 0-100, 
        and returns the result of the generated
        number <= percent
        @capnspacehook
        """
        randNum = self.randGenNum(0, 100)

        return randNum <= percent

    @classmethod
    def randSelect(cls, seq):
        """
        Returns a random element from the sequence
        seq
        """
        if len(seq):
            selection = RandomGen.randGen.choice(seq)
        else:
            selection = None
        
        return selection

    def randShuffle(self, seq):
        """
        Randomly shuffles a list in-place
        """
        RandomGen.randGen.shuffle(seq)

    def randGenVar(self, sizePref):
        """
        Returns a unique randomly named variable, with length 
        randomly chosen from minVarLen to maxVarLen.
        Variable name can consist of uppercase and 
        lowercase letters, as well as digits
        """
        if sizePref == 0:
            minVarLen = 1
        elif sizePref == 1:
            minVarLen = 2
        elif sizePref == 2:
            minVarLen == 4
        else:
            minVarLen == 8

        maxVarLen = minVarLen * 2

        charList = string.ascii_letters + string.digits

        while True:
            randVarLen = RandomGen.randGen.randint(minVarLen, maxVarLen)
            randomVar = RandomGen.randGen.choice(string.ascii_letters)
            randomVar += "".join(RandomGen.randGen.choice(charList) for x in range(randVarLen - 1))

            if randVarLen == 1 and randomVar.isdigit():
                continue

            if randomVar not in RandomGen.generatedVars:
                break

        RandomGen.generatedVars.append(randomVar)

        return randomVar