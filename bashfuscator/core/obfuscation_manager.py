from bashfuscator.common.messages import printError, printWarning
from bashfuscator.common.random import RandomGen


class ObfuscationHandler(object):
    """
    Manages command and script obfuscation. Obfuscates based off of 
    the user's set options
    """
    def __init__(self, cmdObfuscators, strObfuscators, tokObfuscators, args):
        self.cmdObfuscators = cmdObfuscators
        self.strObfuscators = strObfuscators
        self.tokObfuscators = tokObfuscators
        self.userMutators = args.choose_mutators
        self.layers = args.layers
        self.sizePref = args.payload_size
        self.timePref = args.execution_time
        self.binaryPref = args.binaryPref
        self.filePref = args.no_file_write
        self.originalCmd = args.command
        self.prevCmdOb = None
        self.randGen = RandomGen()

        if args.full_ascii_strings:
            self.randGen.setFullAsciiStrings()

    def generatePayload(self):
        """
        Generates the final payload based off of the user's options
        """
        payload = self.originalCmd
        global revObWarn 
        revObWarn = False
        
        for i in range(self.layers):
            if self.userMutators is not None:
                for userOb in self.userMutators:
                    if userOb.count("/") == 2:
                        if userOb[-1] == "/":
                            userOb = userOb[:-1]
                            payload = self.genObfuscationLayer(payload, userOb)
                        else:
                            userStub = userOb.split("/")[2]
                            userOb = userOb[:-int(len(userStub) + 1)]
                            payload = self.genObfuscationLayer(payload, userOb, userStub)
                    
                    payload = self.genObfuscationLayer(payload, userOb)
            
            else:
                payload = self.genObfuscationLayer(payload)

        return payload

    def genObfuscationLayer(self, payload, userOb=None, userStub=None):
        """
        Generates one layer of obfuscation
        """
        tokObfuscator = strObfuscator = cmdObfuscator = None

        if userOb is not None:
            if userOb.split("/")[0] == "command":
                cmdObfuscator = self.choosePrefObfuscator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, self.prevCmdOb, userOb, userStub)
                self.prevCmdOb = cmdObfuscator
                payload = cmdObfuscator.obfuscate(self.sizePref, self.timePref, payload)

            elif userOb.split("/")[0] == "string":
                strObfuscator = self.choosePrefObfuscator(self.strObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, userOb=userOb)
                payload = strObfuscator.obfuscate(self.sizePref, payload)

            elif userOb.split("/")[0] == "token":
                tokObfuscator = self.choosePrefObfuscator(self.tokObfuscators, self.sizePref, userOb=userOb)
                payload = tokObfuscator.obfuscate(self.sizePref, payload)

        else:
            obChoice = self.randGen.randChoice(3)

            if obChoice == 0:
                cmdObfuscator = self.choosePrefObfuscator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref, self.prevCmdOb)
                self.prevCmdOb = cmdObfuscator

                payload = cmdObfuscator.obfuscate(self.sizePref, self.timePref, payload)

            elif obChoice == 1:
                strObfuscator = self.choosePrefObfuscator(self.strObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.filePref)

                payload = strObfuscator.obfuscate(self.sizePref, payload)

            else:
                tokObfuscator = self.choosePrefObfuscator(self.tokObfuscators, self.sizePref)
                payload = tokObfuscator.obfuscate(self.sizePref, payload)
           
        self.randGen.forgetUniqueStrs()
        payload = self.evalWrap(payload)

        return payload

    def evalWrap(self, payload):
        return '''eval "$({0})"'''.format(payload)

    def choosePrefObfuscator(self, obfuscators, sizePref, timePref=None, binaryPref=None, filePref=None, prevOb=None, userOb=None, userStub=None):
        """
        Returns an obfuscator from a list of obfuscators which is of the 
        desired preferences, with a stub that uses desired binaries
        """
        selObfuscator = None
        global revObWarn

        if binaryPref is not None:
            binList = binaryPref[0]
            includeBinary = binaryPref[1]

        if userOb is not None:
            for ob in obfuscators:
                if ob.longName == userOb:
                    if binaryPref is not None and ob.mutatorType == "string":
                        for binary in ob.binariesUsed:
                            if (binary in binList) != includeBinary:
                                printWarning("'{0}' obfuscator contains an unwanted binary".format(userOb))
                    
                    selObfuscator = ob
                    break
            
            if selObfuscator is None:
                printError("Selected obfuscator '{0}' not found".format(userOb))
        
        else:
            prefObfuscators = self.getPrefItems(obfuscators, sizePref, timePref, filePref, prevOb)

        validChoice = False
        while not validChoice:
            if userOb is None:
                selObfuscator = self.randGen.randSelect(prefObfuscators)

            # make sure we don't choose the same CommandObfuscator twice if it's reversable
            if prevOb is not None and prevOb.reversible and prevOb.name == selObfuscator.name:
                if userOb is not None:
                    if not revObWarn:
                        revObWarn = True
                        printWarning("Reversible obfuscator '{0}' selected twice in a row; part of the payload may be in the clear".format(userOb))
                else:
                    continue
            
            if selObfuscator.mutatorType == "command":
                selStub = self.choosePrefStub(selObfuscator.stubs, sizePref, timePref, binaryPref, userStub)

                if selStub is not None:
                    selObfuscator.deobStub = selStub
                    validChoice = True

            # we aren't selecting a CommandObfuscator, only they have stubs
            else:
                validChoice = True

        return selObfuscator

    def choosePrefStub(self, stubs, sizePref, timePref, binaryPref, userStub=None):
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


        if len(prefStubs):
            prefStubs = self.getPrefItems(prefStubs, sizePref, timePref)

        selStub = self.randGen.randSelect(prefStubs)

        return selStub

    def getPrefItems(self, seq, sizePref, timePref, filePref=None, prevOb=None):
        """
        Returns items from seq which are preferable to the user based
        off of the options they chose
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
                            if prevOb is not None and prevOb.reversible and prevOb == item:
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
