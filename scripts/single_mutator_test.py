#!/usr/bin/env python3
"""
Stress tests a single Mutator
"""
from datetime import datetime
import os
import pytest
from subprocess import STDOUT, PIPE, Popen

from bashfuscator.core.obfuscation_handler import ObfuscationHandler


if __name__ == "__main__":
    mutatorName = "string/xor_non_null"
    
    inputCommand = "echo 'It works!'"
    expectedOutput = "It works!\n"
    
    obHandler = ObfuscationHandler()

    try:
        for i in range(1000):
            payload = obHandler.genObfuscationLayer(inputCommand, userMutator=mutatorName)

            proc = Popen(payload, executable="bash", stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)
            payloadOutput, __ = proc.communicate()

            assert(expectedOutput == payloadOutput)
    except AssertionError:
        if not os.path.exists("failing"):
            os.mkdir("failing")

        date = datetime.now()
        timestamp = str(date.month) + "." + str(date.day) + "." + str(date.year) + "-" + str(date.hour) + "." + str(date.minute) + "." + str(date.second)
        with open("failing/" + mutatorName.replace("/", ".") + "-" + timestamp + ".sh", "w") as errorFile:
            errorFile.write(payload)
        raise
