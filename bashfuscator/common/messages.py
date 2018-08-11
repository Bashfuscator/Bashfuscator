from sys import exit


def info(msg):
    print("[+] {0}".format(msg))


def warning(msg):
    print("[!] {0}".format(msg))


def error(msg):
    print("[ERROR] {0}".format(msg))
    exit(1)