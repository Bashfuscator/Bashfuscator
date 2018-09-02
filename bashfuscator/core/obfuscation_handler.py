"""
Defines ObufscationHandler, which manages the obfuscation process.
"""
from bashfuscator.common.messages import printError, printWarning
from bashfuscator.common.random import RandomGen


class ObfuscationHandler(object):
    """
    Manages command and script obfuscation, taking into account all
    user options and preferences. This class is the heart of the
    framework.

    :param cmdObfuscators: all CommandObfuscators contained by the
        framework
    :type cmdObfuscators: list of
        :class:`bashfuscator.lib.command_mutators.CommandObfuscator`
    :param strObfuscators: all StringObfuscators contained by the
        framework
    :type strObfuscators: list of
        :class:`bashfuscator.lib.string_mutators.StringObfuscator`
    :param tokObfuscators: all TokenObfuscators contained by the
        framework
    :type tokObfuscators: list of
        :class:`bashfuscator.lib.token_mutators.TokenObfuscator`
    :param encoders: all Encoders contained by the
        framework
    :type encoders: list of
        :class:`bashfuscator.lib.encoders.Encoder`
    :param compressors: all Compressors contained by the
        framework
    :type compressors: list of
        :class:`bashfuscator.lib.compressors.Compressor`
    :param args: arguments specified on the command line
    :type args: arguments parsed from
        :py:meth:`argparse.ArgumentParser.parse_args`
    """

    def __init__(self, cmdObfuscators, strObfuscators, tokObfuscators, encoders, compressors, args):
        self.cmdObfuscators = cmdObfuscators
        self.strObfuscators = strObfuscators
        self.tokObfuscators = tokObfuscators
        self.encoders = encoders
        self.compressors = compressors
        
        self.layers = args.layers
        self.sizePref = args.payload_size
        self.timePref = args.execution_time
        self.binaryPref = args.binaryPref
        self.filePref = args.no_file_write
        self.originalCmd = args.command
        self.prevCmdOb = None
        self.randGen = RandomGen()

        if args.choose_mutators:
            self.userMutators = args.choose_mutators
        elif args.choose_all:
            self.userMutators = args.choose_all
        else:
            self.userMutators = None

        if args.full_ascii_strings:
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
                    if userMutator.count("/") == 2:
                        if userMutator[-1] == "/":
                            userMutator = userMutator[:-1]
                            payload = self.genObfuscationLayer(payload, userMutator)
                        else:
                            userStub = userMutator.split("/")[2]
                            userMutator = userMutator[:-int(len(userStub) + 1)]
                            payload = self.genObfuscationLayer(payload, userMutator, userStub)
                    else:
                        payload = self.genObfuscationLayer(payload, userMutator)
                    
            else:
                payload = self.genObfuscationLayer(payload)

        return payload

    def genObfuscationLayer(self, payload, userMutator=None, userStub=None):
        """
        Generate one layer of obfuscation. If called with the
        userMutator or userStub parameters, the Mutator and/or Stub
        specified by userMutator and/or userStub will be used to mutate
        the payload. If those parameters are not used, a Mutator and
        Stub (if appropriate) will be chosen automatically.

        :param payload: input command(s) to obfuscate
        :type payload: str
        :param userMutator: the `longName` attribute of a
            :class:`bashfuscator.common.objects.Mutator`
        :type userMutator: lowercase str
        :param userStub: the `longName` attribute of a
            :class:`bashfuscator.common.objects.Stub`
        :type userStub: lowercase str
        :returns: a str containing the 'payload' argument obfuscated by
            a single Mutator
        """
        selMutator = None

        if userMutator is not None:
            mutatorType = userMutator.split("/")[0]

            if mutatorType == "command":
                selMutator = self.choosePrefMutator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, self.prevCmdOb, userMutator, userStub)
                self.prevCmdOb = selMutator

                payload = selMutator.obfuscate(self.sizePref, self.timePref, payload)

            elif mutatorType == "string":
                selMutator = self.choosePrefMutator(self.strObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, userMutator=userMutator)
                    
                payload = selMutator.obfuscate(self.sizePref, self.timePref, payload)

            elif mutatorType == "token":
                selMutator = self.choosePrefMutator(self.tokObfuscators, self.sizePref, userMutator=userMutator)
                payload = selMutator.obfuscate(self.sizePref, payload)

            elif mutatorType == "encode":
                selMutator = self.choosePrefMutator(self.encoders, userMutator=userMutator)
                payload = selMutator.encode(self.sizePref, self.timePref, payload)

            elif mutatorType == "compress":
                selMutator = self.choosePrefMutator(self.compressors, userMutator=userMutator)
                payload = selMutator.compress(self.sizePref, self.timePref, payload)
        else:
            # TODO: handle case when no mutators of chosen type are compatible with user's preferences
            obChoice = self.randGen.randChoice(3)

            if obChoice == 0:
                selMutator = self.choosePrefMutator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, self.prevCmdOb)
                self.prevCmdOb = selMutator

                payload = selMutator.obfuscate(self.sizePref, self.timePref, payload)

            elif obChoice == 1:
                selMutator = self.choosePrefMutator(self.strObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref)

                payload = selMutator.obfuscate(self.sizePref, self.timePref, payload)

            else:
                selMutator = self.choosePrefMutator(self.tokObfuscators, self.sizePref)
                payload = selMutator.obfuscate(self.sizePref, payload)
           
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
        if selMutator.longName != "encode/urlencode":
            if self.randGen.probibility(50):
                wrappedPayload = '''eval "$({0})"'''.format(payload)
            else:
                wrappedPayload = '''printf -- "$({0})"|bash'''.format(payload)
        else:
            wrappedPayload = payload
        
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

        if userMutator is not None:
            if binaryPref is not None:
                binList = binaryPref[0]
                includeBinary = binaryPref[1]

            for mutator in mutators:
                if mutator.longName == userMutator:
                    if filePref is not None and mutator.fileWrite != filePref:
                        printWarning("'{0}' mutator preforms file writes".format(userMutator))

                    elif binaryPref is not None and mutator.mutatorType == "string":
                        for binary in mutator.binariesUsed:
                            if (binary in binList) != includeBinary:
                                printWarning("'{0}' mutator contains an unwanted binary".format(userMutator))
                    
                    selMutator = mutator
                    if selMutator.mutatorType == "command":
                        selMutator.prefStubs = selMutator.stubs

                    break
            
            if selMutator is None:
                printError("Selected mutator '{0}' not found".format(userMutator))
        
        else:
            prefMutators = self.getPrefMutators(mutators, sizePref, timePref, binaryPref, filePref, prevCmdOb)
            selMutator = self.randGen.randSelect(prefMutators)

        if selMutator is not None and selMutator.mutatorType == "command":
            selMutator.deobStub = self.choosePrefStub(selMutator.prefStubs, sizePref, timePref, binaryPref, userStub)

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
            if filePref and mutator.fileWrite == filePref:
                continue

            elif mutator.mutatorType == "command":
                if prevCmdOb and prevCmdOb.reversible and prevCmdOb.name == mutator.name:
                    continue

                prefStubs = self.getPrefStubs(mutator.stubs, sizePref, timePref, binaryPref)
                
                if prefStubs:
                    mutator.prefStubs = prefStubs
                else:
                    continue

            # TODO: decide if TokenObfuscators should be allowed if the user chooses to only use certain binaries,
            # TokenObfuscators don't use any binaries 
            elif mutator.mutatorType == "string" and binaryPref:
                badBinary = False
                for binary in mutator.binariesUsed:
                    if (binary in binList) != includeBinary:
                        badBinary = True
                        break
                
                if badBinary:
                    continue
            
            prefMutators.append(mutator)

        return prefMutators

    def getPrefStubs(self, stubs, sizePref, timePref, binaryPref=None):
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
        
        # weed out the stubs that don't use preferred binaries
        stubsWithPrefBinaries = []
        if binaryPref:
            for stub in prefStubs:
                for binary in stub.binariesUsed:
                    if (binary in binList) == includeBinary:
                       stubsWithPrefBinaries.append(stub)
        else:
            stubsWithPrefBinaries = prefStubs

        return stubsWithPrefBinaries

    def choosePrefStub(self, stubs, sizePref, timePref, binaryPref, userStub=None):
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
                                printWarning("'{0}' stub contains an unwanted binary".format(userStub))
                    
                    selStub = stub

            if selStub is None:     
                printError("'{0}' stub not found".format(userStub))

        else:
            selStub = self.randGen.randSelect(stubs)

        return selStub

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
        
        if timePref is not None:
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
        if pref == 0:
            minRating = maxRating = 1
        elif pref == 1:
            minRating = 1
            maxRating = 2
        elif pref == 2:
            minRating = 1
            maxRating = 3
        elif pref == 3:
            minRating = 1
            maxRating = 5
        else:
            minRating = maxRating = 5

        return (minRating, maxRating)
