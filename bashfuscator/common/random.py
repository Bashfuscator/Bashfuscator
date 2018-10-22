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
    _randStrCharList = string.ascii_letters + string.digits
    _reservedVars = {"auto_resume", "BASH", "BASH_ENV", "BASH_VERSINFO", "BASH_VERSION", "CDPATH", "COLUMNS", "COMP_CWORD", "COMP_LINE", "COMP_POINT", "COMPREPLY", "COMP_WORDS", "DIRSTACK", "EUID", "FCEDIT", "FIGNORE", "FUNCNAME", "GLOBIGNORE", "GROUPS", "histchars", "HISTCMD", "HISTCONTROL", "HISTFILE", "HISTFILESIZE", "HISTIGNORE", "HISTSIZE", "HOME", "HOSTFILE", "HOSTNAME", "HOSTTYPE", "IFS", "IGNOREEOF", "INPUTRC", "LANG", "LC_ALL", "LC_COLLATE", "LC_CTYPE", "LC_MESSAGES", "LC_NUMERIC", "LINENO", "LINES", "MACHTYPE", "MAIL", "MAILCHECK", "MAILPATH", "OLDPWD", "OPTARG", "OPTERR", "OPTIND", "OSTYPE", "PATH", "PIPESTATUS", "POSIXLY_CORRECT", "PPID", "PROMPT_COMMAND", "PS1", "PS2", "PS3", "PS4", "PWD", "RANDOM", "REPLY", "SECONDS", "SHELLOPTS", "SHLVL", "TIMEFORMAT", "TMOUT", "UID"}
    _reservedVars.add("DATA")


    def setFullAsciiStrings(self):
        """
        Set the default charset used when generating random
        variables and strings to the (almost) full ASCII charset.
        Only "'" and "/" are not used.
        """
        RandomGen._randStrCharList = "".join(
            chr(i) for i in range(1, 127) if i != 39 and i != 47)

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

    def randGenVar(self, sizePref):
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

            if randomVar not in RandomGen._generatedVars and randomVar not in RandomGen._reservedVars:
                break

        RandomGen._generatedVars.add(randomVar)

        return randomVar

    # TODO: make sure random strings don't contain BOBL seqences
    def randUniqueStr(self, minStrLen, maxStrLen, charList=None):
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
        if charList is None:
            charList = RandomGen._randStrCharList

        minLen = minStrLen
        maxLen = maxStrLen
        commonStrNum = 0

        while True:
            randStr = self.randGenStr(minLen, maxLen, charList)

            if randStr not in RandomGen._uniqueRandStrs:
                break
            else:
                commonStrNum += 1
                # if 5 collisions are generated in a row, chances are that we are reaching the upper bound
                # of our keyspace, so make the keyspace bigger so we can keep generating unique strings
                if commonStrNum == 5:
                    minLen = maxLen
                    maxLen += 1
                    commonStrNum = 0

        RandomGen._uniqueRandStrs.add(randStr)

        return randStr

    def randGenStr(self, minStrLen, maxStrLen, charList=None):
        """
        Generate a random string. Functions the same as
        :meth:`~RandomGen.randUniqueStr`, the only difference being
        that the generated string is NOT guaranteed to be unique.
        """
        if charList is None:
            charList = RandomGen._randStrCharList

        randVarLen = RandomGen.randGen.randint(minStrLen, maxStrLen)
        randStr = "".join(self.randSelect(charList) for x in range(randVarLen))

        return randStr
