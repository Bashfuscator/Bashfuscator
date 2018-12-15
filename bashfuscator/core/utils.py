import importlib
import os

import bashfuscator.modules as bashfuscator_modules

MODULES_DIR = bashfuscator_modules.__path__[0]

def import_mutators():
    modules = []
    for root, dirs, files in os.walk(MODULES_DIR):
        _, package, root = root.rpartition("bashfuscator/modules/".replace("/", os.sep))
        root = root.replace(os.sep, ".")
        files = filter(lambda x: not x.startswith("_") and x.endswith(".py"), files)
        modules.extend(map(lambda x: ".".join((root, os.path.splitext(x)[0])), files))

    commandObfuscators = []
    stringObfuscators = []
    tokenObfuscators = []
    encoders = []
    compressors = []


    for moduleName in modules:
        module = importlib.import_module("bashfuscator.modules." + moduleName)
        className = moduleName.split(".")[-1]
        className = "".join(s.title() for s in className.split("_"))
        currModule = getattr(module, className)()

        if currModule.mutatorType == "command":
            commandObfuscators.append(currModule)
        elif currModule.mutatorType == "string":
            stringObfuscators.append(currModule)
        elif currModule.mutatorType == "token":
            tokenObfuscators.append(currModule)
        elif currModule.mutatorType == "encode":
            encoders.append(currModule)
        elif currModule.mutatorType == "compress":
            compressors.append(currModule)

    return commandObfuscators, stringObfuscators, tokenObfuscators, encoders, compressors
