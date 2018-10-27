from datetime import datetime
import os
import pytest
from subprocess import STDOUT, PIPE, Popen

from bashfuscator.core.mutator_list import commandObfuscators, stringObfuscators, tokenObfuscators, encoders, compressors
from bashfuscator.core.obfuscation_handler import ObfuscationHandler


inputCommand = "echo 'It works!'"
expectedOutput = "It works!\n"

commandObNames = [c.longName + "/" + s.longName for c in commandObfuscators for s in c.stubs]
stringObNames = [s.longName for s in stringObfuscators]
tokenObNames = [t.longName for t in tokenObfuscators]
encoderObNames = [e.longName for e in encoders if not e.postEncoder]
compressorObNames = [c.longName for c in compressors]

mutators = commandObNames = stringObNames + tokenObNames + encoderObNames + compressorObNames

obHandler = ObfuscationHandler()

@pytest.mark.parametrize("mutatorName", mutators)

def test_mutators(mutatorName):
    try:
        for i in range(100):
            payload = obHandler.genObfuscationLayer(inputCommand, userMutator=mutatorName)

            proc = Popen(payload, executable="bash", stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)
            payloadOutput, __ = proc.communicate()

            assert(expectedOutput == payloadOutput)
    except AssertionError:
        if not os.path.exists("failing"):
            os.mkdir("failing")

        date = datetime.now()
        timestamp = str(date.month) + "." + str(date.day) + "." + str(date.year) + "-" + str(date.hour) + "." + str(date.minute) + "." + str(date.second)
        with open("failing/" + mutatorName.replace("/", ".") + "-" + timestamp, "w") as errorFile:
            errorFile.write(payload)
        raise