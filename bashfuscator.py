#!/usr/bin/env python3

from argparse import ArgumentTypeError, ArgumentParser, FileType

import argcomplete
import bashlex
import pyperclip

from core.obfuscation_manager import ObfuscationHandler
from lib.common.token_obfuscators import *
from lib.common.command_obfuscators import *

tokenObfuscators = [
    AnsiCQuote()
]

commandObfuscators = [
    Reverse(),
    CaseSwap()
]


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise ArgumentTypeError("{ivalue} is an invalid positive int value".format(ivalue))
    return ivalue


if __name__ == "__main__":
    parser = ArgumentParser()
    progOps = parser.add_argument_group("Program Options")
    inptOps = progOps.add_mutually_exclusive_group(required=True)
    inptOps.add_argument("-c", "--command", type=str, help="Command to obfuscate")
    inptOps.add_argument("-f", "--file", type=FileType(mode="r"), help="Name of the script to obfuscate")
    inptOps.add_argument("--stdin", action="store_true", help="Recieve command to obfuscate from stdin")
    progOps.add_argument("-o", "--outfile", type=FileType(mode="w"), help="File to write payload to")
    progOps.add_argument("-q", "--quiet", action="store_true", help="Print only the payload")

    obOps = parser.add_argument_group("Obfuscation Options")
    sizeOps = obOps.add_mutually_exclusive_group()
    sizeOps.add_argument("-s", "--payload-size", default=2, type=int, choices=range(1, 4), help="Desired size of the payload")
    sizeOps.add_argument("-sm", "--min-payload-size", action="store_true", help="Generate the smallest payload possible")
    sizeOps.add_argument("-sM", "--max-payload-size", action="store_true", help="Generate the largest payload possible")
    timeOps = obOps.add_mutually_exclusive_group()
    timeOps.add_argument("-t", "--execution-time", default=2, type=int, choices=range(1, 4), help="Desired speed of the payload")
    timeOps.add_argument("-tm", "--min-execution-time", action="store_true", help="Generate the fastest payload possible")
    timeOps.add_argument("-tM", "--max-execution-time", action="store_true", help="Generate the slowest payload possible")
    obOps.add_argument("--layers", default=2, type=check_positive, help="Layers of obfuscation to apply")
    binOps = obOps.add_mutually_exclusive_group()
    binOps.add_argument("--exclude-binaries", default="", type=str, help="Binaries you don't want to used in the generated payload")
    binOps.add_argument("--include-binaries", default="", type=str, help="Binaries you exclusively want used in the generated payload")
    obOps.add_argument("--no-minify", action="store_true", help="Don't minify script or command entered before obfuscation")

    misc = parser.add_argument_group("Misc Options")
    misc.add_argument("--clip", action="store_true", help="Copy the payload to clipboard")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.min_payload_size:
        args.payload_size = 0
    elif args.max_payload_size:
        args.payload_size = 4

    if args.min_execution_time:
        args.execution_time = 0
    elif args.max_execution_time:
        args.execution_time = 4

    if args.include_binaries is not "":
        args.binaryPref = (args.include_binaries.split(","), True)
    elif args.exclude_binaries is not "":
        args.binaryPref = (args.exclude_binaries.split(","), False)
    else:
        args.binaryPref = None


    obHandler = ObfuscationHandler(tokenObfuscators, commandObfuscators, args)
    payload = obHandler.generatePayload()

    if args.clip:
        pyperclip.copy(payload)

    print(payload)