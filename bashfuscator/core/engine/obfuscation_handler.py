"""
Defines ObufscationHandler, which manages the obfuscation process.
"""
from bashfuscator.common.messages import printError, printWarning
from bashfuscator.core.engine.mangler import Mangler
from bashfuscator.core.engine.random import RandomGen
from bashfuscator.core.utils import import_mutators


class ObfuscationHandler(object):
    """
    Manages command and script obfuscation, taking into account all
    user options and preferences. This class is the heart of the
    framework.

    :param cmdObfuscators: CommandObfuscators useable during execution
    :type cmdObfuscators: list of
        :class:`bashfuscator.lib.command_mutators.CommandObfuscator`
    :param strObfuscators: StringObfuscators useable during execution
    :type strObfuscators: list of
        :class:`bashfuscator.lib.string_mutators.StringObfuscator`
    :param tokObfuscators: TokenObfuscators useable during execution
    :type tokObfuscators: list of
        :class:`bashfuscator.lib.token_mutators.TokenObfuscator`
    :param encoders: Encoders useable during execution
    :type encoders: list of
        :class:`bashfuscator.lib.encoders.Encoder`
    :param compressors: Compressors useable during execution
    :type compressors: list of
        :class:`bashfuscator.lib.compressors.Compressor`
    :param args: arguments specified on the command line. If this
        parameter is not supplied, default values will be set for
        ObfuscationHandler's attributes.
    :type args: arguments parsed from
        :py:meth:`argparse.ArgumentParser.parse_args` in
        :mod:`bashfuscator.bin.bashfuscator`

    .. note::
        If not set, the cmdObfuscators, cmdObfuscators, tokObfuscators,
        encoders, and compressors arguments will default to all of the
        respective Mutator Types contained by the framework.
    """

    def __init__(self, cmdObfuscators=None, strObfuscators=None, tokObfuscators=None, encoders=None, compressors=None, args=None):
        if cmdObfuscators and strObfuscators and tokObfuscators and encoders and compressors:
            self.cmdObfuscators = cmdObfuscators
            self.strObfuscators = strObfuscators
            self.tokObfuscators = tokObfuscators
            self.encoders = encoders
            self.compressors = compressors
        else:
            self.cmdObfuscators, self.strObfuscators, self.tokObfuscators, self.encoders, self.compressors = import_mutators()

        if args:
            self.layers = args.layers
            self.sizePref = args.payload_size
            self.timePref = args.execution_time
            self.binaryPref = args.binaryPref
            self.filePref = args.no_file_write
            self.writeDir = args.write_dir
            self.full_ascii_strings = args.full_ascii_strings
            self.debug = args.debug
            self.clip = args.clip
            self.originalCmd = args.command

            if args.choose_mutators:
                self.userMutators = args.choose_mutators
            elif args.choose_all:
                self.userMutators = args.choose_all
            else:
                self.userMutators = None

            if args.no_mangling is not None:
                self.enableMangling = args.no_mangling
            else:
                self.enableMangling = None

            if args.no_binary_mangling is not None:
                self.mangleBinaries = args.no_binary_mangling
            else:
                self.mangleBinaries = None

            if args.binary_mangle_percent:
                self.binaryManglePercent = args.binary_mangle_percent
            else:
                self.binaryManglePercent = None

            if args.no_random_whitespace is not None:
                self.randWhitespace = args.no_random_whitespace
            else:
                self.randWhitespace = None

            if args.random_whitespace_range:
                self.randWhitespaceRange = args.random_whitespace_range
            else:
                self.randWhitespaceRange = None

            if args.no_insert_chars is not None:
                self.insertChars = args.no_insert_chars
            else:
                self.insertChars = None

            if args.insert_chars_range:
                self.insertCharsRange = args.insert_chars_range
            else:
                self.insertCharsRange = None

            if args.no_misleading_commands is not None:
                self.misleadingCmds = args.no_misleading_commands
            else:
                self.misleadingCmds = None

            if args.misleading_commands_range:
                self.misleadingCmdsRange = args.misleading_commands_range
            else:
                self.misleadingCmdsRange = None

            if args.no_integer_mangling is not None:
                self.mangleIntegers = args.no_integer_mangling
            else:
                self.mangleIntegers = None

            if args.no_integer_expansion is not None:
                self.expandIntegers = args.no_integer_expansion
            else:
                self.expandIntegers = None

            if args.no_integer_base_randomization is not None:
                self.randomizeIntegerBases = args.no_integer_base_randomization
            else:
                self.randomizeIntegerBases = None

            if args.integer_expansion_depth:
                self.integerExpansionDepth = args.integer_expansion_depth
            else:
                self.integerExpansionDepth = None

            if args.no_terminator_randomization is not None:
                self.randomizeTerminators = args.no_terminator_randomization
            else:
                self.randomizeTerminators = None

        else:
            self.sizePref = 2
            self.timePref = 2
            self.binaryPref = None
            self.filePref = True
            self.writeDir = "/tmp/"
            self.full_ascii_strings = False
            self.debug = False
            self.clip = False
            self.userMutators = None

            self.enableMangling = None
            self.mangleBinaries = None
            self.binaryManglePercent = None
            self.randWhitespace = None
            self.randWhitespaceRange = None
            self.insertChars = None
            self.insertCharsRange = None
            self.misleadingCmds = None
            self.misleadingCmdsRange = None
            self.mangleIntegers = None
            self.expandIntegers = None
            self.randomizeIntegerBases = None
            self.integerExpansionDepth = None
            self.randomizeTerminators = None

        self.prevCmdOb = None
        self.mutatorList = []

        self.randGen = RandomGen()

        if args and args.full_ascii_strings:
            self.randGen.setFullAsciiStrings()

    def generatePayload(self):
        """
        Generate the final payload. Obfuscates the original input by
        feeding it into Mutators a number of times as specified by the
        '--layers' option.

        :returns: a str containing the final obfuscated payload
        """
        payload = self.originalCmd

        for i in range(self.layers):
            if self.userMutators:
                for userMutator in self.userMutators:
                    userStub = None
                    if userMutator.count("/") == 2:
                        if userMutator[-1] == "/":
                            userMutator = userMutator[:-1]
                        else:
                            userStub = userMutator.split("/")[2]
                            userMutator = userMutator[:-int(len(userStub) + 1)]

                    self.mutatorList.append(self.getMutator(userMutator, userStub, self.sizePref, self.timePref, self.binaryPref, self.filePref))

            else:
                self.mutatorList.append(self.getMutator(sizePref=self.sizePref, timePref=self.timePref, binaryPref=self.binaryPref, filePref=self.filePref))

        self.checkMutatorList()

        for mutator in self.mutatorList:
            mutator.writeDir = self.writeDir
            mutator.mangler._initialize(self.sizePref, self.enableMangling, self.mangleBinaries, self.binaryManglePercent, self.randWhitespace, self.randWhitespaceRange, self.insertChars, self.insertCharsRange, self.misleadingCmds, self.misleadingCmdsRange, self.mangleIntegers, self.expandIntegers, self.randomizeIntegerBases, self.integerExpansionDepth, self.randomizeTerminators, self.debug)
            payload = mutator.mutate(payload)
            mutator._obfuscatedCmd = payload

            self.randGen.forgetUniqueStrs()
            payload = self.evalWrap(payload, mutator)

        return payload

    def checkMutatorList(self):
        reverseableMutator = ""
        nonReadableWarning = False

        for i, mutator in enumerate(self.mutatorList):
            if self.clip and ((mutator.unreadableOutput and not nonReadableWarning) or self.full_ascii_strings):
                printWarning("Output may consist of unreadable ASCII characters and probably won't execute from your clipboard correctly. Saving output with '-o' is recommended")
                nonReadableWarning = True

            if mutator.mutatorType == "command" and mutator.reversible:
                if reverseableMutator == mutator.longName:
                    printWarning(f"{mutator.longName} used twice in a row, part of the output may be in the clear")
                    reverseableMutator = ""

                else:
                    reverseableMutator = mutator.longName

            else:
                reverseableMutator = ""

    def getMutator(self, userMutator=None, userStub=None, sizePref=None, timePref=None, binaryPref=None, filePref=None):
        selMutator = None

        if userMutator:
            mutatorType = userMutator.split("/")[0]

            if mutatorType == "command":
                selMutator = self.choosePrefMutator(self.cmdObfuscators, sizePref, timePref,
                    binaryPref, filePref, self.prevCmdOb, userMutator, userStub)
                self.prevCmdOb = selMutator

            elif mutatorType == "string":
                selMutator = self.choosePrefMutator(self.strObfuscators, binaryPref=binaryPref, filePref=filePref, userMutator=userMutator)

            elif mutatorType == "token":
                selMutator = self.choosePrefMutator(self.tokObfuscators, binaryPref=binaryPref, filePref=filePref, userMutator=userMutator)

            elif mutatorType == "encode":
                selMutator = self.choosePrefMutator(self.encoders, binaryPref=binaryPref, filePref=filePref, userMutator=userMutator)

            elif mutatorType == "compress":
                selMutator = self.choosePrefMutator(self.compressors, binaryPref=binaryPref, filePref=filePref, userMutator=userMutator)

            else:
                printError(f"{mutatorType} isn't a valid mutator type")
        else:
            # TODO: handle case when no mutators of chosen type are compatible with user's preferences
            obChoice = self.randGen.randChoice(3)

            if obChoice == 0:
                selMutator = self.choosePrefMutator(self.cmdObfuscators, sizePref, timePref,
                    binaryPref, filePref, self.prevCmdOb)
                self.prevCmdOb = selMutator

            elif obChoice == 1:
                selMutator = self.choosePrefMutator(self.strObfuscators, sizePref, timePref,
                    binaryPref, filePref)

            else:
                selMutator = self.choosePrefMutator(self.tokObfuscators, sizePref, timePref)

        selMutator.sizePref = sizePref
        selMutator.timePref = timePref

        return selMutator

    # TODO: update docs
    def genObfuscationLayer(self, payload, userMutator=None, userStub=None, sizePref=None, timePref=None, binaryPref=None, filePref=None, writeDir=None, enableMangling=None, mangleBinaries=None, binaryManglePercent=None, randWhitespace=None, randWhitespaceRange=None, insertChars=None, insertCharsRange=None, misleadingCmds=None, misleadingCmdsRange=None, mangleIntegers=None, expandIntegers=None, randomizeIntegerBases=None, integerExpansionDepth=None, randomizeTerminators=None, debug=None):
        """
        Generate one layer of obfuscation. If called with the
        userMutator or userStub parameters, the Mutator and/or Stub
        specified by userMutator and/or userStub will be used to mutate
        the payload. If those parameters are not used, a Mutator and
        Stub (if appropriate) will be chosen automatically.

        .. note::
            If not set, the sizePref, timePref, binaryPref, filePref,
            and writeDir parameters will be set to the coresponding
            attributes of the ObfuscationHandler object being called
            from.

        :param payload: input command(s) to obfuscate
        :type payload: str
        :param userMutator: the `longName` attribute of a
            :class:`bashfuscator.common.objects.Mutator`
        :type userMutator: lowercase str
        :param userStub: the `longName` attribute of a
            :class:`bashfuscator.common.objects.Stub`
        :type userStub: lowercase str
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param binaryPref: list of binaries that the chosen Mutator
            should or should not use
        :type binaryPref: tuple containing a list of strs, and a bool
        :param filePref: file write user preference
        :type filePref: bool
        :returns: a str containing the 'payload' argument obfuscated by
            a single Mutator
        """
        if sizePref is None:
            sizePref = self.sizePref
        if timePref is None:
            timePref = self.timePref
        if binaryPref is None:
            binaryPref = self.binaryPref
        if filePref is None:
            filePref = self.filePref
        if writeDir is None:
            writeDir = self.writeDir
        if enableMangling is None:
            enableMangling = self.enableMangling
        if mangleBinaries is None:
            mangleBinaries = self.mangleBinaries
        if binaryManglePercent is None:
            binaryManglePercent = self.binaryManglePercent
        if randWhitespace is None:
            randWhitespace = self.randWhitespace
        if randWhitespaceRange is None:
            randWhitespaceRange = self.randWhitespaceRange
        if insertChars is None:
            insertChars = self.insertChars
        if insertCharsRange is None:
            insertCharsRange = self.insertCharsRange
        if misleadingCmds is None:
            misleadingCmds = self.misleadingCmds
        if misleadingCmdsRange is None:
            misleadingCmdsRange = self.misleadingCmdsRange
        if mangleIntegers is None:
            mangleIntegers = self.mangleIntegers
        if expandIntegers is None:
            expandIntegers = self.expandIntegers
        if randomizeIntegerBases is None:
            randomizeIntegerBases = self.randomizeIntegerBases
        if integerExpansionDepth is None:
            integerExpansionDepth = self.integerExpansionDepth
        if randomizeTerminators is None:
            randomizeTerminators = self.randomizeTerminators
        if debug is None:
            debug = self.debug


        selMutator = self.getMutator(userMutator, userStub, sizePref, timePref, binaryPref, filePref)

        selMutator.writeDir = writeDir
        selMutator.mangler._initialize(sizePref, enableMangling, mangleBinaries, binaryManglePercent, randWhitespace, randWhitespaceRange, insertChars, insertCharsRange, misleadingCmds, misleadingCmdsRange, mangleIntegers, expandIntegers, randomizeIntegerBases, integerExpansionDepth, randomizeTerminators, debug)
        payload = selMutator.mutate(payload)
        selMutator._obfuscatedCmd = payload

        self.randGen.forgetUniqueStrs()
        payload = self.evalWrap(payload, selMutator)

        return payload

    def evalWrap(self, payload, selMutator):
        """
        Wrap the payload in an execution stub, to allow bash to execute
        the string produced by the payload. Will not wrap the payload
        if certain Mutators were used to generate the most recent layer
        of the payload.

        :param payload: input command(s) to wrap
        :type payload: str
        :param selMutator: Mutator used by
            :meth:`~ObfuscationHandler.genObfuscationLayer` to generate
            the most recent layer of obfuscation
        :type selMutator: :class:`bashfuscator.common.objects.Mutator`
        :returns: a str containing the wrapped payload, if appropriate
        """
        if selMutator.evalWrap:
            evalMethodChoice = self.randGen.randChoice(3)

            if evalMethodChoice == 1:
                wrappedPayload = selMutator.mangler._mangleLine('* *:eval:^ ^"$(? ?DATA? ?)"* *', payload)
            else:
                shellChoice = self.randGen.randChoice(3)
                if shellChoice == 0:
                    bashShell = ":bash:"
                elif shellChoice == 1:
                    bashShell = "$BASH"
                else:
                    bashShell = "${!#}"

                if evalMethodChoice == 2:
                    wrappedPayload = selMutator.mangler._mangleLine(f'* *:printf:^ ^%s^ ^"$(? ?DATA? ?)"* *|* *{bashShell}* *', payload)
                else:
                    wrappedPayload = selMutator.mangler._mangleLine(f'* *{bashShell}% %<<<^ ^"$(? ?DATA? ?)"* *', payload)

        # if the Mutator evals itself, wrap it in a subshell so it doesn't pollute the parent shell environment
        else:
            wrappedPayload = selMutator.mangler._mangleLine(f"? ?(? ?DATA? ?)", payload)

        return wrappedPayload

    def choosePrefMutator(self, mutators, sizePref=None, timePref=None, binaryPref=None, filePref=None, prevCmdOb=None, userMutator=None, userStub=None):
        """
        Chooses a Mutator from a list of mutators which is of the
        desired preferences, with a stub that uses desired binaries if
        appropriate. If called with the userMutator or userStub
        parameters, the Mutator and/or Stub specified by userMutator
        and/or userStub will be chosen. If those parameters are not
        used, a Mutator and Stub (if appropriate) will be chosen
        automatically based off of the values of the other parameters.

        :param mutators: list of Mutators to choose a Mutator from
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param binaryPref: list of binaries that the chosen Mutator
            should or should not use
        :type binaryPref: tuple containing a list of strs, and a bool
        :param filePref: file write user preference
        :type filePref: bool
        :param prevCmdOb: the previous CommandObfuscator used. Should
            only be passed if a CommandObfuscator was used to generate
            the most recent obfuscation layer
        :type prevCmdOb:
            :class:`bashfuscator.lib.command_mutators.CommandObfuscator`
        :param userMutator: the specific Mutator the user chose to use
        :type userMutator: lowercase str
        :param userStub: the specific Stub the user chose to use
        :type userStub: lowercase str
        :returns: a :class:`bashfuscator.common.objects.Mutator`
            object
        """
        selMutator = None

        if userMutator:
            if binaryPref:
                binList = binaryPref[0]
                includeBinary = binaryPref[1]

            for mutator in mutators:
                if mutator.longName == userMutator:
                    if filePref is False and mutator.mutatorType != "command" and mutator.fileWrite != filePref:
                        printWarning(f"'{userMutator}' mutator preforms file writes")

                    elif binaryPref and mutator.mutatorType != "command":
                        for binary in mutator.binariesUsed:
                            if (binary in binList) != includeBinary:
                                printWarning(f"'{userMutator}' mutator contains an unwanted binary")

                    selMutator = mutator
                    if selMutator.mutatorType == "command":
                        selMutator.prefStubs = self.getPrefStubs(selMutator.stubs, sizePref, timePref, binaryPref, filePref)

                    break

            if selMutator is None:
                printError(f"Selected mutator '{userMutator}' not found")

        else:
            prefMutators = self.getPrefMutators(mutators, sizePref, timePref, binaryPref, filePref, prevCmdOb)
            selMutator = self.randGen.randSelect(prefMutators)

        if selMutator is not None and selMutator.mutatorType == "command":
            selMutator.deobStub = self.choosePrefStub(selMutator.prefStubs, sizePref, timePref, binaryPref, filePref, userStub)

            if selMutator.deobStub:
                selMutator.deobStub.mangler = selMutator.mangler
                selMutator.deobStub.randGen = selMutator.mangler.randGen
            else:
                printError(f"All of '{selMutator.longName}'s Stubs do not fulfil your requirements")

        return selMutator

    def getPrefMutators(self, mutators, sizePref, timePref, binaryPref=None, filePref=None, prevCmdOb=None):
        """
        Get Mutators from a sequence which are suitable to use based
        off the user's preferences.

        :param seq: list of Mutators of Stubs
        :type seq: list
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param binaryPref: list of binaries that the chosen Mutator
            should or should not use
        :type binaryPref: tuple containing a list of strs, and a bool
        :param filePref: file write user preference
        :type filePref: bool
        :param prevCmdOb: the previous CommandObfuscator used. Should
            only be passed if a CommandObfuscator was used to generate
            the most recent obfuscation layer
        :type prevCmdOb:
            :class:`bashfuscator.lib.command_mutators.CommandObfuscator`
        :returns: list of
            :class:`bashfuscator.common.objects.Mutator`
            objects, or None if there are no preferable Mutators in the
            'mutators' argument
        """
        goodMutators = self.getPrefItems(mutators, sizePref, timePref)

        if binaryPref:
            binList = binaryPref[0]
            includeBinary = binaryPref[1]

        prefMutators = []
        for mutator in goodMutators:
            if mutator.mutatorType == "command":
                if prevCmdOb and prevCmdOb.reversible and prevCmdOb.name == mutator.name:
                    continue

                prefStubs = self.getPrefStubs(mutator.stubs, sizePref, timePref, binaryPref, filePref)

                if prefStubs:
                    mutator.prefStubs = prefStubs
                else:
                    continue

            elif filePref is False and mutator.mutatorType != "command" and mutator.fileWrite != filePref:
                continue

            elif binaryPref:
                badBinary = False
                for binary in mutator.binariesUsed:
                    # don't pick a mutator if it uses unwanted binaries, but allow mutators that aren't using
                    # any binaries when the user is using the '--include-binaries' option
                    if (binary in binList) != includeBinary:
                        if includeBinary:
                            if mutator.binariesUsed:
                                badBinary = True
                                break
                            else:
                                continue

                        else:
                            badBinary = True
                            break

                if badBinary:
                    continue

            prefMutators.append(mutator)

        return prefMutators

    def choosePrefStub(self, stubs, sizePref, timePref, binaryPref, filePref, userStub=None):
        """
        Choose a stub which is of the desired sizeRating, timeRating,
        and uses desired binaries. If the userStub parameter is passed,
        the specific stub defined by userStub is searched for and is
        checked to make sure it aligns with the users preferences for
        used binaries.

        :param stubs: list of Stubs to choose from
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param binaryPref: list of binaries that the chosen Mutator
            should or should not use
        :type binaryPref: tuple containing a list of strs, and a bool
        :param userStub: the specific Stub the user chose to use
        :type userStub: lowercase str
        :returns: a :class:`bashfuscator.common.objects.Stub`
            object
        """
        selStub = None

        if binaryPref is not None:
            binList = binaryPref[0]
            includeBinary = binaryPref[1]

        # attempt to find the specific stub the user wants
        if userStub is not None:
            for stub in stubs:
                if stub.longName == userStub:
                    if binaryPref is not None:
                        for binary in stub.binariesUsed:
                            if (binary in binList) != includeBinary:
                                printWarning(f"'{userStub}' stub contains an unwanted binary")

                    if filePref is False and stub.fileWrite != filePref:
                        printWarning(f"'{userStub}' stub preforms file writes")

                    selStub = stub

            if selStub is None:
                printError(f"'{userStub}' stub not found")

        else:
            selStub = self.randGen.randSelect(stubs)

        return selStub

    def getPrefStubs(self, stubs, sizePref, timePref, binaryPref, filePref):
        """
        Get Stubs from a sequence which are suitable to use based
        off the user's preferences.

        :param seq: list of Mutators of Stubs
        :type seq: list
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param binaryPref: list of binaries that the chosen Mutator
            should or should not use
        :type binaryPref: tuple containing a list of strs, and a bool
        :returns: list of
            :class:`bashfuscator.common.objects.Stub`
            objects, or None if there are no preferable Stubs in the
            'stubs' argument
        """
        prefStubs = self.getPrefItems(stubs, sizePref, timePref)

        if binaryPref is not None:
            binList = binaryPref[0]
            includeBinary = binaryPref[1]

        compatibleStubs = []
        for stub in prefStubs:
            if filePref is False and stub.fileWrite != filePref:
                continue

            if binaryPref:
                badBinary = False
                for binary in stub.binariesUsed:
                    # don't pick a stub if it uses unwanted binaries, but allow stubs that aren't using
                    # any binaries when the user is using the '--include-binaries' option
                    if (binary in binList) != includeBinary:
                        if includeBinary:
                            if stub.binariesUsed:
                                badBinary = True
                                break
                            else:
                                continue

                        else:
                            badBinary = True
                            break

                if badBinary:
                    continue

            compatibleStubs.append(stub)

        return compatibleStubs

    def getPrefItems(self, seq, sizePref, timePref):
        """
        Get Mutators or Stubs from a sequence which
        sizeRatings and timeRatings.

        :param seq: list of Mutators of Stubs
        :type seq: list
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :returns: a list of Mutators or Stubs
        """
        minSize, maxSize = self.getPrefRange(sizePref)
        minTime, maxTime = self.getPrefRange(timePref)

        foundItem = False
        prefItems = []

        while not foundItem:
            for item in seq:
                if minSize <= item.sizeRating <= maxSize:
                    if timePref is None or (minTime <= item.timeRating <= maxTime):
                        prefItems.append(item)
                        foundItem = True

            if not foundItem:
                if not foundItem:
                    if minSize > 1:
                        minSize -= 1
                    elif maxSize < 5:
                        maxSize += 1

                    if timePref is not None:
                        if minTime > 1:
                            minTime -= 1
                        elif maxTime < 5:
                            maxTime += 1

        return prefItems

    def getPrefRange(self, pref):
        """
        Get the minimum and maximum sizeRatings or timeRatings that
        should be used to select obfuscator and stubs

        :param pref: sizePref or timePref options
        :returns: tuple of minimum and maximum ratings
        """
        if pref == 1:
            maxRating = 2
        elif pref == 2:
            maxRating = 3
        elif pref == 3:
            maxRating = 5

        return (1, maxRating)
