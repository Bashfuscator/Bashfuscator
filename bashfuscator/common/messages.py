from sys import exit

from bashfuscator.common.colors import blue, yellow, red, bold

def printInfo(msg):
    print("[{0}] {1}".format(blue("+"), msg))


def printWarning(msg):
    print(yellow("[!] {0}".format(msg)))


def printError(msg):
    print(bold(red("[ERROR] {0}".format(msg))))
    exit(1)