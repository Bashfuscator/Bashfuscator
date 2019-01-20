Command/Reverse
===============

Examples
--------

Without Mangling
****************

.. code-block:: bash

    eval "$(rev <<<'dwssap/cte/ tac')"

With Mangling
*************

.. code-block:: bash

     ${*,  } ${*%%$<\(5 } e${*##\)@gLH\[@\)  }val  "$(    ${@^ }  "$@"  \p\r\intf   %s 'dwssap/cte/ tac'   ${@%lk_z|?   }   | ${@##V8x2rVp  }   ''r'e'""'v'  ${*#O<-.   }   "${@^^ }"   ;  ${*,,   } ${!@}    )"   "${@/LLN\}<~ }"

Description
-----------
Reverse is another simple Mutator. Quite simply, it reverses it's input. That's it.

Side Effects
------------
None.

Detection
---------
Look for common commands or strings reversed, such as `ftnirp` or `lave`.

Dependencies
------------
The `rev` command, available in the `util-linux` package which is installed by default on both Debian and Fedora based systems.
http://man7.org/linux/man-pages/man1/rev.1.html

Runtime Graph
-------------
Similar to Case Swapper. Adds almost no overhead to generated payloads.

.. raw:: html

    <iframe src="../../_static/graphs/command_obfuscators/reverse/runtime_graph.html" height="750px" width="100%"></iframe>

|

Size Graph
----------
Adds on average 30 characters to the input payload. Very minimal size increase.

.. raw:: html

    <iframe src="../../_static/graphs/command_obfuscators/reverse/size_graph.html" height="750px" width="100%"></iframe>

|
