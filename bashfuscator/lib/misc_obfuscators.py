from bashfuscator.common.random import RandomGen


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
