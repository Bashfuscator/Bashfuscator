Introduction
============

Bashfuscator is built to be a modular, flexible Bash obfuscation framework. It achieves this by organizing
different obfuscation techniques and methods into modules within the framework, called Mutators.
Different obfuscation 'recipes' can be created by stacking different Mutators, giving the resulting payload
varying characteristics and appearances.

Mutator types
-------------

There are 5 types of Mutators:

#. Command Obfuscators
    * Simple obfuscators that leverage behavior of commands or binaries present in a Linux environment
    * Obfuscates entire input in one chunk

#. String Obfuscators
    * Obfuscators that use more advanced features/binaries
    * Breaks input into chunks, obfuscates those chunks, then builds up input by concatenating standard output of all of the different obfuscated chunks

#. Token Obfuscators
    * Leverages Bash functionality or behavior to obfuscate commands
    * Typically don't use any external binaries
    * Obfuscates entire input in one chunk

#. Encoders
    * Encodes the entire input and decodes it using a stub.

#. Compressors
    * Compresses the input and decompresses it using a stub, using various compressors typically available in a Linux environment
