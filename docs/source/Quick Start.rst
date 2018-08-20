Quick Start
===========

Use the `-c` or `-f` options to specifiy a one-liner or script file to obfuscate, and Bashfuscator will
take care of the rest. Bashfuscator only requires those two options, although many more are avalible to
fine-tune the obfuscation.

The `-s` and `-t` options control the added size and execution time of the obfuscated payload respectively.
They both default to 2, but can be set to 1-3 to control the generated payload more closely. The higher the
`-s` or `-t` options, the greater the variety of the payload. When a low setting for the `-s` or `-t` options
is set, Bashfuscator will limit itself to using Mutators that increase the size and execution time of the payload
slightly. With high values, Bashfuscator has a chance to pick any combination of it's Mutators!

You can further fine-tune the obfuscation process by using the `--choose-mutators` option. This option allows
you to manually select which Mutators Bashfuscator will use, and in what order. If used with the `--layer` option,
the obfuscation sequence can be layered upon itself multiple times.