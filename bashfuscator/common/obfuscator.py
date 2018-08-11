import re

from bashfuscator.common.random import RandomGen


class Obfuscator(object):
    """
    Base class that StringObfuscator
    and CommandObfuscator inherit from
    """
    def __init__(self, name):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.randGen = RandomGen()


class Stub(object):
    """
    This class is in charge of generating a valid deobfuscation stub,
    taking care of properly escaping quotes in the user's input, 
    generating random variable names, and so on. 
    """
    def __init__(self, name, binariesUsed, sizeRating, timeRating, escapeQuotes, stub):
        self.name = name
        self.longName = self.name.replace(" ", "_").lower()
        self.binariesUsed = binariesUsed
        self.sizeRating = sizeRating
        self.timeRating = timeRating
        self.escapeQuotes = escapeQuotes
        self.stub = stub
        self.randGen = RandomGen()

    def genStub(self, sizePref, userCmd):
        if self.escapeQuotes:
            userCmd = userCmd.replace('"', '\\"')

        if sizePref == 1:
            minVarLen = 2
            maxVarLen = 3
        else:
            minVarLen = 6
            maxVarLen = 12
        
        genStub = self.stub
        for var in re.findall(r"VAR\d+", self.stub):
            genStub = self.stub.replace(var, self.randGen.randGenVar(minVarLen, maxVarLen))

        genStub = genStub.replace("CMD", userCmd)

        return "eval $({0})".format(genStub)


def choosePrefObfuscator(seq, sizePref, timePref=None, binaryPref=None, userStub=None):
    """
    Returns an obfuscator from seq which is of the desired sizeRating, 
    timeRating, with a stub that uses desired binaries
    """
    prefObfuscators = getPrefItems(seq, sizePref, timePref)

    validStub = False
    while not validStub:
        selObfuscator = RandomGen.randSelect(prefObfuscators)
        
        if timePref is not None:
            selStub = choosePrefStub(selObfuscator.stubs, sizePref, timePref, binaryPref, userStub)

            if selStub is not None:
                selObfuscator.deobStub = selStub
                validStub = True

        # we are selecting a TokenObfuscator, they don't have stubs
        else:
            validStub = True

    return selObfuscator


def choosePrefStub(stubs, sizePref, timePref, binaryPref, userStub=None):
    """
    Returns a stub which is of the desired sizeRating, timeRating, and 
    use desired binaries, or None if no stubs use desired binaries 
    unless the user has elected to manually select a stub. In that
    case, that specific stub is searched for and is checked to make 
    sure it aligns with the users preferences for used binaries
    """
    if binaryPref is not None:
        binList = binaryPref[0]
        includeBinary = binaryPref[1]
    
    # attempt to find the specific stub the user wants
    if userStub is not None:
        for stub in stubs:
            if stub.long_name == userStub:
                if binaryPref is not None:
                    for binary in stub.binariesUsed:
                        if (binary in binList) != includeBinary:
                            raise RuntimeError("{0} stub contains an unwanted binary".format(userStub))
                
                return stub

        raise KeyError("{0} stub not found".format(userStub))

    prefStubs = []
    if binaryPref is not None:
        for stub in stubs:
            for binary in stub.binariesUsed:
                if (binary in binList) == includeBinary:
                    prefStubs.append(stub)
    
    else:
        prefStubs = stubs


    if len(prefStubs):
        prefStubs = getPrefItems(prefStubs, sizePref, timePref)

    selStub = RandomGen.randSelect(prefStubs)

    return selStub


def getPrefItems(seq, sizePref, timePref):
    """
    Returns items from seq which are of the desired sizeRating and
    timeRating
    """
    minSize, maxSize = getPrefRange(sizePref)
    
    if timePref is not None:
        minTime, maxTime = getPrefRange(timePref)

    foundItem = False
    prefItems = []

    while not foundItem:
        for item in seq:
            if minSize <= item.sizeRating <= maxSize:
                if timePref is None or (minTime <= item.timeRating <= maxTime):
                    prefItems.append(item)
                    foundItem = True
        
        if not foundItem:
            if minSize > 1:
                minSize -= 1
            elif maxSize < 5:
                maxSize += 1

    return prefItems


def getPrefRange(pref):
    """
    Returns the minimum and maximum sizeRatings or timeRatings that 
    should be used to select obfuscator and stubs

    :param pref: sizePref or timePref
    """
    if pref == 0:
        min = max = 1
    elif pref == 1:
        min = 1
        max = 2
    elif pref < 4:
        min = 1
        max = pref + 2
    else:
        min = max = 5

    return (min, max)
