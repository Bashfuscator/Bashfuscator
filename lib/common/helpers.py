"""

This file contains miscellaneous functions used by the framework

"""

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


    def randGenVar(self, minVarLen, maxVarLen):
        """
        Returns a unique randomly named variable, with length 
        randomly chosen from minVarLen to maxVarLen.
        Variable name can consist of uppercase and 
        lowercase letters, as well as digits
        """
        charList = string.ascii_letters + string.digits

        while True:
            randVarLen = RandomGen.randGen.randint(minVarLen, maxVarLen)
            randomVar = RandomGen.randGen.choice(string.ascii_letters)
            randomVar += "".join(RandomGen.randGen.choice(charList) for x in range(randVarLen - 1))

            if randomVar not in RandomGen.generatedVars:
                break

        RandomGen.generatedVars.append(randomVar)

        return randomVar


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


def obfuscateInt(num, smallExpr):
    """
    Obfuscate an integer by replacing the int
    with an arithmetic expression. Returns a string that
    when evaluated mathematically, is equal to the int entered.
    @capnspacehook 
    """
    randGen = RandomGen()
    exprStr, baseExprPieces = genSimpleExpr(num, smallExpr)
    if smallExpr:
        numExpr = exprStr % (baseExprPieces[0], baseExprPieces[1], baseExprPieces[2])
    else:
        subExprs = []
        for piece in baseExprPieces:
            expr, pieces = genSimpleExpr(piece, smallExpr)
            subExprs.append(expr % (pieces[0], pieces[1], pieces[2]))
        numExpr = exprStr % (subExprs[0], subExprs[1], subExprs[2])
        
    # Randomly replace '+' with '--'. Same thing, more confusing
    match = re.search(r"\+\d+", numExpr)
    beginingExprLen = 0
    while match is not None:   
        match = list(match.span())
        match[0] += beginingExprLen
        match[1] += beginingExprLen
        choice = randGen.randChoice(2)
        if choice:
            numExpr = numExpr[:match[0]] + "-(-" + numExpr[match[0] + 1:match[1]] + ")" + numExpr[match[1]:]
        beginingExprLen = len(numExpr[:match[1]])
        match = re.search(r"\+\d+", numExpr[match[1]:])
    
    # Properly separate any double '-' signs. Some langs complain
    match = re.search(r"--\d+", numExpr)
    beginingExprLen = 0
    while match is not None:   
        match = list(match.span())
        match[0] += beginingExprLen
        match[1] += beginingExprLen
        numExpr = numExpr[:match[0]] + "-(" + numExpr[match[0] + 1:match[1]] + ")" + numExpr[match[1]:]
        beginingExprLen = len(numExpr[:match[1]])
        match = re.search(r"--\d+", numExpr[match[1]:])
    
    # Bash requires mathematical expressions to be in $((expression)) syntax
    numExpr = "$((" + numExpr + "))"
    return numExpr


def genSimpleExpr(n, smallExpr):
    """
    Generates a simple mathematical expression of 3 terms
    that equal the number passed. Returns a template
    expression string, and a tuple of the values of the 
    terms in the generated expression.
    @capnspacehook
    """
    randGen = RandomGen()

    if type(n) == str:
        n = int(eval(n))
    if n == 0:
        N = 0
        while N == 0:
            N = randGen.randGenNum(-99999, 99999)
    else:
        N = n
    choice = randGen.randGenNum(0, 2)
    left = 0
    if choice == 0:
        if N < 0:
            left = randGen.randGenNum(N * 2, -N + 1)
            right = randGen.randGenNum(N - 1, -N * 2)
        else:
            left = randGen.randGenNum(-N * 2, N - 1)
            right = randGen.randGenNum(-N + 1, N * 2)
        if left + right < n:
            offset = n - (left + right)
            expr = "((%s+%s)+%s)"
        else:
            offset = (left + right) - n
            expr = "(-(-(%s+%s)+%s))"
    elif choice == 1:
        if N < 0:
            left = randGen.randGenNum(N - 1, -N * 2)
            right = randGen.randGenNum(N * 2, N - 1)
        else:
            left = randGen.randGenNum(-N + 1, N * 2)
            right = randGen.randGenNum(-N * 2, N + 1)
        if left - right < n:
            offset = n - (left - right)
            expr = "((%s-%s)+%s)"
        else:
            offset = (left - right) - n
            expr = "(-(-(%s-%s)+%s))"
    elif choice == 2:
        if N < 0:
            left = randGen.randGenNum(int(N / 2), -int(N / 2) - 2)
            right = randGen.randGenNum(int(N / 3), -int(N / 3))
        else:
            left = randGen.randGenNum(-int(n / 2), int(n / 2) + 2)
            right = randGen.randGenNum(-int(n / 3), int(n / 3))
        if left * right < n:
            offset = n - (left * right)
            expr = "((%s*%s)+%s)"
        else:
            offset = (left * right) - n
            expr = "(-(-(%s*%s)+%s))"

    # Replace all zeros with an expression. Zeros make arithmetic easy
    if not smallExpr:
        if left == 0:
            zeroExpr, terms = genSimpleExpr(0, smallExpr)
            left = zeroExpr % (terms[0], terms[1], terms[2])
        if right == 0:
            zeroExpr, terms = genSimpleExpr(0, smallExpr)
            right = zeroExpr % (terms[0], terms[1], terms[2])
        if offset == 0:
            zeroExpr, terms = genSimpleExpr(0, smallExpr)
            offset = zeroExpr % (terms[0], terms[1], terms[2])
    return (expr, (left, right, offset))
