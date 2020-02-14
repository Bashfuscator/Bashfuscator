Command/Case Swapper
====================

Examples
--------

Without Mangling
****************

.. code-block:: bash

    eval "$(E3LFbgu='CAT /ETC/PASSWD';printf %s "${E3LFbgu~~}")"

With Mangling
*************

.. code-block:: bash

       $@  "${@~~  }"  \p${@,,  }r""i${*,   }n${*%%+Y,B;pv }t${@%%@cil:\}W  }f   %s  "$(    _aWJ5_a='CAT /ETC/PASSWD'  "${@%%B6qv#j@=   }"  ${*/+Re\ew?   }  &&  ${@%^JjcVY:I }  p\r"i"${*}n't'f %s "${_aWJ5_a~~}"  ${@%%Vm\)?X }   $@      ${*//^PNN   }    )"   ${@//6?*G.\)\/LJ\[k3 }  | "${@~~  }"   $* $'\x62''a'sh  ${*/9\[>f   }  ${*~  }

Description
-----------
Case Swapper is an extremely simple Mutator that leverages one of Bash's parameter expansions
to flip the case of any alphabetic characters of it's input. See
https://wiki.bash-hackers.org/syntax/pe#case_modification for more information on the parameter
expansion used.

Side Effects
------------
None.

Detection
---------
Case Swapper can be detected by looking for weird casings of normal commands, such as `ECHO` or
`PRINTF`.

Dependencies
------------
None. Not sure when Bash added support for case modification parameter expansions, but only ancient
versions of Bash might not work with this Mutator.

Runtime Graph
-------------
The runtime graph has a strange shape, but it's still clear that Case Swapper adds very little runtime overhead
to generated payloads.

.. raw:: html

    <iframe src="../../_static/graphs/command_obfuscators/case_swapper/runtime_graph.html" height="750px" width="100%"></iframe>

|

Size Graph
----------
As expected, Case Swapper hardly adds any extra size to generated payloads.

.. raw:: html

    <iframe src="../../_static/graphs/command_obfuscators/case_swapper/size_graph.html" height="750px" width="100%"></iframe>

|
