from sys import exit

from bashfuscator.common.colors import blue, yellow, red, bold


quietOutput = False
def activateQuietMode():
    global quietOutput
    quietOutput = True


def printInfo(msg):
    if not quietOutput:
        print("[{0}] {1}".format(blue("+"), msg))


def printWarning(msg):
    if not quietOutput:
        print(yellow("[!] {0}".format(msg)))


def printError(msg):
    print(bold(red("[ERROR] {0}".format(msg))))
    exit(1)