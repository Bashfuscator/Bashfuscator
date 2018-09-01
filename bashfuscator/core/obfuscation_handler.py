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
        global revObWarn 
        revObWarn = False
        
        for i in range(self.layers):
            if self.userMutators is not None:
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
        global revObWarn

        if userMutator is not None:
            if binaryPref is not None:
                binList = binaryPref[0]
                includeBinary = binaryPref[1]

            for mut in mutators:
                if mut.longName == userMutator:
                    if binaryPref is not None and mut.mutatorType == "string":
                        for binary in mut.binariesUsed:
                            if (binary in binList) != includeBinary:
                                printWarning("'{0}' obfuscator contains an unwanted binary".format(userMutator))
                    
                    selMutator = mut
                    break
            
            if selMutator is None:
                printError("Selected mutator '{0}' not found".format(userMutator))
        
        else:
            prefMutators = self.getPrefItems(mutators, sizePref, timePref, filePref, prevCmdOb)
            selMutator = self.randGen.randSelect(prefMutators)

        if selMutator.mutatorType == "command":
            # make sure we don't choose the same CommandObfuscator twice if it's reversible
            if prevCmdOb is not None and prevCmdOb.reversible and prevCmdOb.name == selMutator.name and not revObWarn:
                revObWarn = True
                printWarning("Reversible obfuscator '{0}' selected twice in a row; part of the payload may be in the clear".format(userMutator))
            
            selMutator.deobStub = self.choosePrefStub(selMutator.stubs, sizePref, timePref, binaryPref, userStub)

        return selMutator

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
                    
                    return stub

            printError("'{0}' stub not found".format(userStub))

        prefStubs = []
        if binaryPref is not None:
            for stub in stubs:
                for binary in stub.binariesUsed:
                    if (binary in binList) == includeBinary:
                        prefStubs.append(stub)
        
        else:
            prefStubs = stubs

        if prefStubs:
            prefStubs = self.getPrefItems(prefStubs, sizePref, timePref)

        selStub = self.randGen.randSelect(prefStubs)

        return selStub

    def getPrefItems(self, seq, sizePref, timePref, filePref=None, prevCmdOb=None):
        """
        Get Mutators or Stubs from a sequence which are suitable to use
        based off the user's preferences.

        :param seq: list of Mutators of Stubs
        :type seq: list
        :param sizePref: payload size user preference
        :type sizePref: int
        :param timePref: execution time user preference
        :type timePref: int
        :param filePref: file write user preference
        :type filePref: bool
        :param prevCmdOb: the previous CommandObfuscator used. Should
            only be passed if a CommandObfuscator was used to generate
            the most recent obfuscation layer
        :type prevCmdOb:
            :class:`bashfuscator.lib.command_mutators.CommandObfuscator`
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
                        if not filePref or item.fileWrite != filePref:
                            if prevCmdOb is not None and prevCmdOb.reversible and prevCmdOb == item:
                                continue
                            else:
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
            min = max = 1
        elif pref == 1:
            min = 1
            max = 2
        elif pref == 2:
            min = 1
            max = 3
        elif pref == 3:
            min = 1
            max = 5
        else:
            min = max = 5

        return (min, max)
