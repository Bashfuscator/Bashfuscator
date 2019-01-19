Usage
=====

Basic CLI Usage
---------------

Before starting to obfuscate for the first time, it may be useful to have a list of all of the available
Mutators contained in the Bashfuscator framework. The `-l` option will do just that, and give size and time
ratings, descriptions, and more.

.. code-block:: bash

    $ bashfuscator -l
    Command Obfuscators:

    Name: Case Swapper
    Description: Flips the case of all alpha chars
    Size Rating: 1
    Time Rating: 1
    File write: False
    Author: capnspacehook

    Stubs:

        Name: bash case swap expansion
        Binaries Used: None
        Size Rating: 1
        Time Rating: 1
    [snip]

    Token Obfuscators:

    Name: ANSI-C Quote
    Description: ANSI-C quotes a string
    Size Rating: 3
    Time Rating: 1
    Binaries used: None
    File write: False
    Notes: Requires Bash 4.2 or above
    Author: capnspacehook
    Credits: DissectMalware, https://twitter.com/DissectMalware/status/1023682809368653826

    Name: Special Char Only
    Description: Converts commands to only use special characters
    Size Rating: 4
    Time Rating: 2
    Binaries used: cat
    File write: False
    Notes: Will break when run in Bash's debug mode. Also compresses extremely well
    Author: capnspacehook
    Credits: danielbohannon, https://github.com/danielbohannon/Invoke-Obfuscation
            Digital Trauma, https://codegolf.stackexchange.com/questions/22533/weirdest-obfuscated-hello-world
    [snip]

When you're ready to start obfuscating, use the `-c` or `-f` options to specify a one-liner or script file to
obfuscate, and Bashfuscator will take care of the rest, randomly choosing Mutators to obfuscate the input with.
Bashfuscator only requires one of those two options, although many more are available to fine-tune the obfuscation.

.. code-block:: bash

    $ bashfuscator -c "cat /etc/passwd"
    [+] Payload:

    eval "$(printf %s '")enod;"}]Y5DFSN$[A55_NI{$" s% ftnirp od;6 3 2 2 7 5 9 8 1 0 9 4 1 7 8 ni Y5DFSN rof;)/\ c a d p  \ w s t e(=A55_NI($" lave'|rev)"

    [+] Payload size: 149 characters

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

.. code-block:: bash

    $ bashfuscator -c "cat /etc/passwd" --test
    [+] Payload:

    eval "$(ijmduN3D=(\[ r f 5 4 G U \" a i s p 1 t \% \} \  e \) \/ \\ 0 b J k z 7 \] \; \{ \| D \( X 2 h 3 \= 9 V 8 w n \$ B c 6 d o);for s7SQJyu8 in 11 1 9 42 13 2 16 14 10 16 7 43 32 24 44 39 8 6 33 37 32 20 19 16 45 16 10 16 47 16 41 16 13 16 11 16 17 16 8 16 20 16 18 28 2 48 1 16 31 25 35 24 23 36 41 5 16 9 42 16 12 16 40 16 3 16 38 16 21 16 26 16 3 16 12 16 21 16 46 16 40 16 34 16 34 16 4 16 36 28 47 48 16 11 1 9 42 13 2 16 14 10 16 7 43 29 24 44 39 8 6 33 0 43 31 25 35 24 23 36 41 5 27 15 7 28 47 48 42 17 18 7 30 22 8 10 35;do printf %s "${ijmduN3D[$s7SQJyu8]}";done)"

    [+] Payload size: 578 characters
    [+] Testing payload:

    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    [snip]

Advanced CLI Usage
------------------

.. note::
    All options are tab-completable! This makes CLI usage sooo much easier, especially when using long options.

The `--layers` option will control the amount of obfuscation layers Bashfuscator will apply to the input. The default
is 2 layers. This is useful to control the amount of obfuscation applied to the input.

The `--full-ascii-strings` option is an interesting one. When used, the full ASCII character set is used when randomly
generating strings to be used within the final payload. This means non-printable characters can possibly exist within
the obfuscated payload, potentially (hopefully) messing with tools and regex used to examine your payload.

You can further fine-tune the obfuscation process by using the `--choose-mutators` option. This option allows
you to manually select which Mutators Bashfuscator will use, and in what order. You can create some pretty creative
obfuscation recipes using this option. If used with the `--layer` option, the obfuscation recipe can be layered upon
itself multiple times.

.. code-block:: bash

    $ bashfuscator -c "cat /etc/passwd" --choose-mutators token/special_char_only compress/bzip2 command/case_swapper command/reverse --layers 2 --test
    [+] Payload:

    printf %s "$(rev <<<'hsab|")"}~~BiT8Vs5Q{$" s% ftnirp;'"'"'HSAB|")C- 2PIZNUB|D- 46ESAB|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 FTNIRP($" S% FTNIRP'"'"'=BiT8Vs5Q($" s% ftnirp')"|bash

    [+] Payload size: 5810 characters
    [+] Testing payload:

    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    [snip]

Tab-completion is especially helpful when using the `--choose-mutators` option.

.. code-block:: bash

    $ bashfuscator -c "cat /etc/passwd" --choose-mutators
    command/case_swapper     compress/bzip2           encode/base64            string/file_glob         string/forcode           token/ansi-c_quote
    command/reverse          compress/gzip            encode/urlencode         string/folder_glob       string/hex_hash          token/special_char_only
    $ bashfuscator -c "cat /etc/passwd" --choose-mutators string/
    string/file_glob    string/folder_glob  string/forcode      string/hex_hash
    $ bashfuscator -c "cat /etc/passwd" --choose-mutators string/
