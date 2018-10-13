"""
Helper functions used throughout the framework
"""

def escape_quotes(inCmd):
    return inCmd.replace("'", "'\"'\"'")