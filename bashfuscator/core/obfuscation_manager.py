from bashfuscator.common.obfuscator import choosePrefObfuscator


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
        self.prevCmdOb = None

        if args.command:
            self.originalCmd = args.command
        else:
            self.originalCmd = args.file.read()

    def generatePayload(self):
        payload = self.originalCmd
        
        for i in range(self.layers):
            if self.userMutators is not None:
                for userOb in self.userMutators:
                    payload = self.genObfuscationLayer(payload, userOb)
            
            else:
                payload = self.genObfuscationLayer(payload)

        return payload

    def genObfuscationLayer(self, payload, userOb=None):
        cmdObfuscator = strObfuscator = tokObfuscator = None

        if userOb is not None:
            if userOb.split("/")[0] == "command":
                cmdObfuscator = choosePrefObfuscator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.prevCmdOb, userOb)
                self.prevCmdOb = cmdObfuscator
                payload = cmdObfuscator.obfuscate(self.sizePref, self.timePref, self.binaryPref, payload)
            elif userOb.split("/")[0] == "string":
                strObfuscator = choosePrefObfuscator(self.strObfuscators, self.sizePref, userOb=userOb)
                payload = strObfuscator.obfuscate(self.sizePref, payload)
            elif userOb.split("/")[0] == "token":
                tokObfuscator = choosePrefObfuscator(self.tokObfuscators, self.sizePref, userOb=userOb)
                payload = tokObfuscator.obfuscate(self.sizePref, payload)

            payload = self.evalWrap(payload)

        else:
            cmdObfuscator = choosePrefObfuscator(self.cmdObfuscators, self.sizePref, self.timePref, 
                    self.binaryPref, self.prevCmdOb, userOb)
            self.prevCmdOb = cmdObfuscator
            strObfuscator = choosePrefObfuscator(self.strObfuscators, self.sizePref, userOb=userOb)
            tokObfuscator = choosePrefObfuscator(self.tokObfuscators, self.sizePref, userOb=userOb)
           
            payload = cmdObfuscator.obfuscate(self.sizePref, self.timePref, self.binaryPref, payload)
            payload = self.evalWrap(payload)
            payload = strObfuscator.obfuscate(self.sizePref, payload)
            payload = self.evalWrap(payload)
            #payload = tokObfuscator.obfuscate(self.sizePref, payload)

        return payload

    def evalWrap(self, payload):
        return '''eval "$({0})"'''.format(payload)
