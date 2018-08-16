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
    generatedVars = set()
    uniqueRandStrs = set()
    randStrCharList = string.ascii_letters + string.digits

    def setFullAsciiStrings(self):
        RandomGen.randStrCharList = "".join(chr(i) for i in range(1, 127) if i != 39 and i != 47 and i != 96)

    def forgetUniqueStrs(self):
        RandomGen.generatedVars.clear()
        RandomGen.uniqueRandStrs.clear()

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

    def randSelect(self, seq):
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
            minVarLen = 4
        else:
            minVarLen = 8

        maxVarLen = minVarLen * 2

        randVarCharList = string.ascii_letters + string.digits + "_"

        while True:
            randomVar = self.randSelect(string.ascii_letters + "_")
            randomVar += self.randGenStr(minVarLen, maxVarLen - 1, randVarCharList)

            if len(randomVar) == 1 and randomVar.isdigit():
                continue

            if randomVar not in RandomGen.generatedVars:
                break

        RandomGen.generatedVars.add(randomVar)

        return randomVar

    def randUniqueStr(self, minStrLen, maxStrLen, charList=None):
        """
        Returns a random string that is guaranteed to be unique
        """
        if charList is None:
            charList = RandomGen.randStrCharList

        minLen = minStrLen
        maxLen = maxStrLen
        commonStrNum = 0 

        while True:
            randStr = self.randGenStr(minLen, maxLen, charList)

            if randStr not in RandomGen.uniqueRandStrs:
                break 
            else:
                commonStrNum += 1
                if commonStrNum == 5:
                    minLen = maxLen
                    maxLen += 1
                    commonStrNum = 0 

        RandomGen.uniqueRandStrs.add(randStr)

        return randStr

    def randGenStr(self, minStrLen, maxStrLen, charList=None):
        """
        Returns a random string, ranging in size from minStrLen to
        maxStrLen, using characters from charList.
        """ 
        if charList is None:
            charList = RandomGen.randStrCharList

        randVarLen = RandomGen.randGen.randint(minStrLen, maxStrLen)
        randStr = "".join(self.randSelect(charList) for x in range(randVarLen))

        return randStr
