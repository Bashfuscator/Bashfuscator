"""
Defines RandomGen, a wrapper around all common functions relying on
randomness.
"""
import string
import random
import re


class RandomGen(object):
    """
    Wrapper around :py:class:`random.SystemRandom`.
    Provided for ease of use and to avoid
    having to initialize a SystemRandom object
    every time something random is desired.

    .. note::
        The default character set when generating random variable names
        or strings is the alphanumeric charset, or the (almost) full ASCII
        charset if :meth:`~RandomGen.setFullAsciiStrings` is called.
    """
    randGen = random.SystemRandom()
    _generatedVars = set()
    _uniqueRandStrs = set()

    _randStrCharList = [c for c in string.ascii_letters + string.digits + string.punctuation]
    _randStrCharList.remove("'")
    _randStrCharList.remove("/")

    _reservedVars = {"auto_resume", "BASH", "BASH_ENV", "BASH_VERSINFO", "BASH_VERSION", "CDPATH", "COLUMNS", "COMP_CWORD", "COMP_LINE", "COMP_POINT", "COMPREPLY", "COMP_WORDS", "DIRSTACK", "EUID", "FCEDIT", "FIGNORE", "FUNCNAME", "GLOBIGNORE", "GROUPS", "histchars", "HISTCMD", "HISTCONTROL", "HISTFILE", "HISTFILESIZE", "HISTIGNORE", "HISTSIZE", "HOME", "HOSTFILE", "HOSTNAME", "HOSTTYPE", "IFS", "IGNOREEOF", "INPUTRC", "LANG", "LC_ALL", "LC_COLLATE", "LC_CTYPE", "LC_MESSAGES", "LC_NUMERIC", "LINENO", "LINES", "MACHTYPE", "MAIL", "MAILCHECK", "MAILPATH", "OLDPWD", "OPTARG", "OPTERR", "OPTIND", "OSTYPE", "PATH", "PIPESTATUS", "POSIXLY_CORRECT", "PPID", "PROMPT_COMMAND", "PS1", "PS2", "PS3", "PS4", "PWD", "RANDOM", "REPLY", "SECONDS", "SHELLOPTS", "SHLVL", "TIMEFORMAT", "TMOUT", "UID"}
    _boblReservedStrsRegex = re.compile("DATA|END")

    _boblSyntaxRegex = re.compile(r":\w+:|\^ \^|\? \?|% %|\* \*|#\d+#|&\d+&|DATA|END")

    def __init__(self):
        self.sizePref = None

    def setFullAsciiStrings(self):
        """
        Set the default charset used when generating random
        variables and strings to the (almost) full ASCII charset.
        Only "'" and "/" are not used.
        """
        RandomGen._randStrCharList = [chr(i) for i in range(1, 128)]
        RandomGen._randStrCharList.remove("'")
        RandomGen._randStrCharList.remove("/")

    # TODO: make this functionality local to each RandomGen instance
    def forgetUniqueStrs(self):
        """
        Clear the sets of previously generated variable names
        and strings. Should be called when random variable
        names/strings are needed but can have the same name as
        previously generated variable names/strings without
        causing conflicts.
        """
        RandomGen._generatedVars.clear()
        RandomGen._uniqueRandStrs.clear()

    def randGenNum(self, min, max):
        """
        Randomly generate an integer inclusively.

        :param min: minimum integer that can be returned
        :type min: int
        :param max: maximum integer that can be returned
        :type max: int
        """
        return RandomGen.randGen.randint(min, max)

    def randChoice(self, max):
        """
        Generate a random choice. Useful when you need to choose
        between a set number of choices randomly.

        :param max: maximum integer that can be returned
        :returns: integer from 0 to max-1 inclusively
        """
        return self.randGenNum(0, max - 1)

    def probibility(self, prob):
        """
        Return True a certain percentage of the time.

        :param prob: probability of returning True
        :type prob: int
        :returns: True prob percent of the time, False otherwise
        """
        randNum = self.randGenNum(0, 100)

        return randNum <= prob

    def randSelect(self, seq):
        """
        Randomly select an element from a sequence. If the argument
        'seq' is a dict, a randomly selected key will be returned.

        :param seq: sequence to randomly select from
        :type seq: list
        :returns: element from seq if seq is a list, a key if seq
            is a dict, or None if seq is empty
        """
        if isinstance(seq, dict):
            selection = RandomGen.randGen.choice(list(seq.keys()))

        elif seq:
            selection = RandomGen.randGen.choice(seq)
        else:
            selection = None

        return selection

    def randShuffle(self, seq):
        """
        Randomly shuffle a sequence in-place.

        :param seq: sequence to shuffle randomly
        :type seq: list
        """
        RandomGen.randGen.shuffle(seq)

    def randGenVar(self, minVarLen=None, maxVarLen=None):
        """
        Generate a unique randomly named variable. Variable names can
        consist of uppercase and lowercase letters, digits, and
        underscores, but will always start with a letter or underscore.

        :param sizePref: sizePref user option. Controls the minimum and
            maximum length of generated variable names
        :type sizePref: int
        :returns: unique random variable name

        .. note::
            :meth:`~RandomGen.randUniqueStr` is called under the hood,
            therefore the same performance concerns apply.
        """
        minVarLen, maxVarLen = self._getSizes(minVarLen, maxVarLen)

        randVarCharList = string.ascii_letters + string.digits + "_"

        while True:
            randomVar = self.randSelect(string.ascii_letters + "_")
            randomVar += self.randGenStr(minVarLen, maxVarLen - 1, randVarCharList)

            if len(randomVar) == 1 and randomVar.isdigit():
                continue

            if RandomGen._boblReservedStrsRegex.search(randomVar):
                continue

            if randomVar not in RandomGen._generatedVars and randomVar not in RandomGen._reservedVars:
                break

        RandomGen._generatedVars.add(randomVar)

        return randomVar

    def randUniqueStr(self, minStrLen=None, maxStrLen=None, charList=None, escapeChars="", noBOBL=True):
        """
        Generate a random string that is guaranteed to be unique.

        :param minStrLen: minimum length of generated string
        :type minStrLen: int
        :param maxStrLen: maximum length of generated string
        :type maxStrLen: int
        :param charList: list of characters that will be used when
            generating the random string. If it is not specified, the
            default character set will be used
        :type charList: str or list of chrs
        :returns: unique random string

        .. note::
            Runtime will increase incrementally as more and more unique
            strings are generated, unless
            :meth:`~RandomGen.forgetUniqueStrs` is called.
        """
        minStrLen, maxStrLen = self._getSizes(minStrLen, maxStrLen)

        if charList is None:
            charList = RandomGen._randStrCharList

        commonStrNum = 0

        while True:
            randStr = self.randGenStr(minStrLen, maxStrLen, charList, escapeChars, noBOBL)

            if randStr not in RandomGen._uniqueRandStrs:
                break
            else:
                commonStrNum += 1
                # if 5 collisions are generated in a row, chances are that we are reaching the upper bound
                # of our keyspace, so make the keyspace bigger so we can keep generating unique strings
                if commonStrNum == 5:
                    minStrLen = maxStrLen
                    maxStrLen += 1
                    commonStrNum = 0

        RandomGen._uniqueRandStrs.add(randStr)

        return randStr

    def randGenStr(self, minStrLen=None, maxStrLen=None, charList=None, escapeChars="", noBOBL=True):
        """
        Generate a random string. Functions the same as
        :meth:`~RandomGen.randUniqueStr`, the only difference being
        that the generated string is NOT guaranteed to be unique.
        """
        minStrLen, maxStrLen = self._getSizes(minStrLen, maxStrLen)

        if charList is None:
            charList = RandomGen._randStrCharList

        randStrLen = RandomGen.randGen.randint(minStrLen, maxStrLen)
        randStr = "".join(self.randSelect(charList) for x in range(randStrLen))

        if noBOBL:
            while RandomGen._boblSyntaxRegex.search(randStr):
                randStr = "".join(self.randSelect(charList) for x in range(randStrLen))

        # escape 'escapeChars', making sure that an already escaped char isn't
        # accidentally un-escaped by adding an extra '\'
        for char in escapeChars:
            randStr = re.sub(r"(?<!\\)(\\{2})*(?!\\)" + re.escape(char), "\g<1>\\" + char, randStr)

        return randStr

    def _getSizes(self, minLen, maxLen):
        if minLen is None or maxLen is None:
            if self.sizePref == 1:
                defaultMinLen = 1
            elif self.sizePref == 2:
                defaultMinLen = 4
            else:
                defaultMinLen = 8

            defaultMaxLen = defaultMinLen * 2

            if minLen is None:
                minLen = defaultMinLen

            if maxLen is None:
                maxLen = defaultMaxLen

        return (minLen, maxLen)
