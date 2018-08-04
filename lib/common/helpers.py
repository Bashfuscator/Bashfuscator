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
    
    
    def __init__(self):
        self.generatedVars = []
        self.underscoreVarLens = []
    

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


    def randSelection(self, seq):
        """
        Returns a random element from the sequence
        seq
        """
        return RandomGen.randGen.choice(seq)


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
            randomVar = "".join(RandomGen.randGen.choice(charList) for x in range(randVarLen))

            if randomVar not in self.generatedVars:
                break

        self.generatedVars.append(randomVar)

        return randomVar


def obfuscateInt(num, smallExpr):
    """
    Obfuscate an integer by replacing the int
    with an arithmetic expression. Returns a string that
    when evaluated mathematically, is equal to the int entered.
    @capnspacehook 
    """
    randGen = random.SystemRandom()
    exprStr, baseExprPieces = gen_simple_expr(num, smallExpr)
    if smallExpr:
        portExpr = exprStr % (baseExprPieces[0], baseExprPieces[1], baseExprPieces[2])
    else:
        subExprs = []
        for piece in baseExprPieces:
            expr, pieces = gen_simple_expr(piece, smallExpr)
            subExprs.append(expr % (pieces[0], pieces[1], pieces[2]))
        portExpr = exprStr % (subExprs[0], subExprs[1], subExprs[2])
        
    # Randomly replace '+' with '--'. Same thing, more confusing
    match = re.search("\+\d+", portExpr)
    beginingExprLen = 0
    while match is not None:   
        match = list(match.span())
        match[0] += beginingExprLen
        match[1] += beginingExprLen
        choice = randGen.randint(0, 1)
        if choice:
            portExpr = portExpr[:match[0]] + "-(-" + portExpr[match[0] + 1:match[1]] + ")" + portExpr[match[1]:]
        beginingExprLen = len(portExpr[:match[1]])
        match = re.search("\+\d+", portExpr[match[1]:])
    
    # Properly separate any double '-' signs. Some langs complain
    match = re.search("--\d+", portExpr)
    beginingExprLen = 0
    while match is not None:   
        match = list(match.span())
        match[0] += beginingExprLen
        match[1] += beginingExprLen
        portExpr = portExpr[:match[0]] + "-(" + portExpr[match[0] + 1:match[1]] + ")" + portExpr[match[1]:]
        beginingExprLen = len(portExpr[:match[1]])
        match = re.search("--\d+", portExpr[match[1]:])
    
    # Bash requires mathematical expressions to be in $((expression)) syntax
    portExpr = "$((" + portExpr + "))"
    return portExpr


def gen_simple_expr(n, smallExpr):
    """
    Generates a simple mathematical expression of 3 terms
    that equal the number passed. Returns a template
    expression string, and a tuple of the values of the 
    terms in the generated expression.
    @capnspacehook
    """
    randGen = random.SystemRandom()
    if type(n) == str:
        n = int(eval(n))
    if n == 0:
        N = 0
        while N == 0:
            N = randGen.randint(-99999, 99999)
    else:
        N = n
    choice = randGen.randint(0, 2)
    left = 0
    if choice == 0:
        if N < 0:
            left = randGen.randint(N * 2, -N + 1)
            right = randGen.randint(N - 1, -N * 2)
        else:
            left = randGen.randint(-N * 2, N - 1)
            right = randGen.randint(-N + 1, N * 2)
        if left + right < n:
            offset = n - (left + right)
            expr = "((%s+%s)+%s)"
        else:
            offset = (left + right) - n
            expr = "(-(-(%s+%s)+%s))"
    elif choice == 1:
        if N < 0:
            left = randGen.randint(N - 1, -N * 2)
            right = randGen.randint(N * 2, N - 1)
        else:
            left = randGen.randint(-N + 1, N * 2)
            right = randGen.randint(-N * 2, N + 1)
        if left - right < n:
            offset = n - (left - right)
            expr = "((%s-%s)+%s)"
        else:
            offset = (left - right) - n
            expr = "(-(-(%s-%s)+%s))"
    elif choice == 2:
        if N < 0:
            left = randGen.randint(int(N / 2), -int(N / 2) - 2)
            right = randGen.randint(int(N / 3), -int(N / 3))
        else:
            left = randGen.randint(-int(n / 2), int(n / 2) + 2)
            right = randGen.randint(-int(n / 3), int(n / 3))
        if left * right < n:
            offset = n - (left * right)
            expr = "((%s*%s)+%s)"
        else:
            offset = (left * right) - n
            expr = "(-(-(%s*%s)+%s))"

    # Replace all zeros with an expression. Zeros make arithmetic easy
    if not smallExpr:
        if left == 0:
            zeroExpr, terms = gen_simple_expr(0, smallExpr)
            left = zeroExpr % (terms[0], terms[1], terms[2])
        if right == 0:
            zeroExpr, terms = gen_simple_expr(0, smallExpr)
            right = zeroExpr % (terms[0], terms[1], terms[2])
        if offset == 0:
            zeroExpr, terms = gen_simple_expr(0, smallExpr)
            offset = zeroExpr % (terms[0], terms[1], terms[2])
    return (expr, (left, right, offset))
