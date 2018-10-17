Quick Start
===========

Introduction
------------

Bashfuscator is built to be a modular, flexible Bash obfuscation framework. It achieves this by organizing
different obfuscation techniques and methods into modules within the framework, called Mutators. 
Different obfuscation 'recipes' can be created by stacking different Mutators. 

Basic CLI Usage
---------------

Before starting to obfuscate for the first time, it may be useful to have a list of all of the available 
Mutators contained in the Bashfuscator framework. The `-l` option will do just that, and give size and time 
ratings, descriptions, and more. 

When you're ready to start obfuscating, use the `-c` or `-f` options to specify a one-liner or script file to 
obfuscate, and Bashfuscator will take care of the rest, randomly choosing Mutators to obfuscate the input with.
Bashfuscator only requires one of those two options, although many more are available to fine-tune the obfuscation.

The `-s` and `-t` options control the added size and execution time of the obfuscated payload respectively.
They both default to 2, but can be set to 1-3 to control the generated payload more closely. The higher the
`-s` or `-t` options, the greater the variety of the payload, at the expense of added size. When a low setting 
for the `-s` or `-t` options is set, Bashfuscator will limit itself to using Mutators that increase the size and
execution time of the payload slightly. With high values, Bashfuscator has a chance to pick any combination of it's
Mutators!

When you've finally settled on an obfuscation recipe to use, two output options are available: `--clip` and `-o`.
`--clip` will automagically copy the obfuscated payload to your clipboard, and `-o` will write the payload to a
file that you specify.

You should make sure the obfuscated payload works as expected, and the `--test` option will make that easier.
When used, `--test` will invoke the obfuscated payload in memory, and show the output. When `-o` is used to specify
an output file to write to, the output file will be run after the payload is written to it.

Advanced CLI Usage
------------------

The `--layers` option will control the amount of obfuscation layers Bashfuscator will apply to the input. The default
is 2 layers. This is useful to control the amount of obfuscation applied to the input.

The `--full-ascii-strings` option is an interesting one. When used, the full ASCII character set is used when randomly
generating strings to be used within the final payload. This means non-printable characters can possibly exist within
the obfuscated payload, potentially (hopefully) messing with tools and regex used to examine your payload 

You can further fine-tune the obfuscation process by using the `--choose-mutators` option. This option allows
you to manually select which Mutators Bashfuscator will use, and in what order. If used with the `--layer` option,
the obfuscation sequence can be layered upon itself multiple times. Tab-completion is especially helpful when using
this option.