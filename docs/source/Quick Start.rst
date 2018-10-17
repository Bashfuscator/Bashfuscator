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
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
    proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
    www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
    backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
    list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
    irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
    gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
    nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
    systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
    systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
    systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
    systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
    _apt:x:104:65534::/nonexistent:/bin/false
    rtkit:x:105:110:RealtimeKit,,,:/proc:/bin/false
    dnsmasq:x:106:65534:dnsmasq,,,:/var/lib/misc:/bin/false
    messagebus:x:107:111::/var/run/dbus:/bin/false
    usbmux:x:108:46:usbmux daemon,,,:/var/lib/usbmux:/bin/false
    speech-dispatcher:x:109:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/false
    sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
    lightdm:x:111:114:Light Display Manager:/var/lib/lightdm:/bin/false
    pulse:x:112:115:PulseAudio daemon,,,:/var/run/pulse:/bin/false
    avahi:x:113:118:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/bin/false
    saned:x:114:119::/var/lib/saned:/bin/false
    capnspacehook:x:1000:1000:Andrew LeFevre,,,:/home/capnspacehook:/bin/bash

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

.. code-block:: bash

    $ bashfuscator -c "cat /etc/passwd" --choose-mutators 
    command/case_swapper     compress/bzip2           encode/base64            string/file_glob         string/forcode           token/ansi-c_quote       
    command/reverse          compress/gzip            encode/urlencode         string/folder_glob       string/hex_hash          token/special_char_only  
    $ bashfuscator -c "cat /etc/passwd" --choose-mutators string/
    string/file_glob    string/folder_glob  string/forcode      string/hex_hash     
    $ bashfuscator -c "cat /etc/passwd" --choose-mutators string/
