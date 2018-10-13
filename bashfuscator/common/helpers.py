"""
Helper functions used throughout the framework
"""

def escapeQuotes(inCmd):
    return inCmd.replace("'", "'\"'\"'")