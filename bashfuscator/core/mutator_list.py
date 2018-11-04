from bashfuscator.lib.command_obfuscators import *
from bashfuscator.lib.string_obfuscators import *
from bashfuscator.lib.token_obfuscators import *
from bashfuscator.lib.encoders import *
from bashfuscator.lib.compressors import *


commandObfuscators = [
    CaseSwap(),
    Reverse(),
]

stringObfuscators = [
    FileGlob(),
    FolderGlob(),
    ForCode(),
    HexHash(),
    XorNonNull(),
]

tokenObfuscators = [
    AnsiCQuote(),
    SpecialCharOnly(),
]

encoders = [
    Base64(),
    UrlEncode(),
]

compressors = [
    Bzip2(),
    Gzip(),
]
