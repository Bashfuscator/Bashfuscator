Token/ForCode
=============

Examples
--------

Without Mangling
****************

.. code-block:: bash

    eval "$(REF6tN=(t s e p \  c \/ a d w);for A0D4rZkc in 5 7 0 4 6 2 0 5 6 3 7 1 1 9 8;{ printf %s "${REF6tN[$A0D4rZkc]}";};)"

With Mangling
*************

.. code-block:: bash

      ${*^ }   "e"${@,,  }va${@}l "$(     CsOXkBR=(   ${@//~0_=/4@C,j  }   \/  ${*, }   c  ${@^^ } ${@%T*d\"n1=;  } \   ${*^ } ${*#H,P?k  }   p  ${*#\"ffe   }  ${*/0ZDZ1/A0;iuQ9d  }   e  ${@##ig4ejq;J  }  ${@^^  }   d  ${*^^ }  ${*##x6UNp  } s ${*#UWsFZ\`~P   } ${@} a   ${*~~  } w ${!*} ${*%%MxRoe  }  t  ${@%=.n\]NC } "${@,, }"  )  ${*^^  } ${@##+r?\"\!x   } ; for j_7kV3XC   in   13#1  "${@/CN\`K?gb/-k\!yuf:U   }"   3#21 "${@##bJ\"c2 }"  4#21 "${@~   }" 3#2   ${*##P\`$uMGcc   } 27#0   ${!@}   ${*//~*Y~Id6h/tcWP7\]Q   } 2#100   "${@//TA|vl }" ${@~   } 2#1001  "${@^^ }" ${*^  }   31#1 ${*/+2yz\(/\(?GF?#N  } ${!@}   19#0 ${*~   } "${@%+3N;&\{<  }"  2#11   ${*//\bi#@1m5/:aSV<   }   ${@/~Dbmr>X/bb%O   }  3#21 ${@}   ${@}   4#12   ${*#37\[Fsq\}%  } 2#110  ${*/TH\! }  ${*#Zu>8\(7  } 3#22 "${@}" 4#11   ${*~   }  ;   do  $'\x70'r"i"ntf   %s "${CsOXkBR[   ${@#~qKa3|  }  $j_7kV3XC ${@~~   }  ]}"  ${*~~  }  ;   done ;   "${@,   }"  ${*}    )"   ${*^   }   ${@^  }

Description
-----------
ForCode is a Mutator inspired from Daniel Bohannon's `Invoke-DOSfuscation project`_, where this
obfuscation technique was first invented. ForCode first creates a unique list of characters present in the
input, and randomizes the order of that list. A second list is then created that contains the indexes of
where each character of the input is in the first list.

For example, given in input command `echo hi`, if the first list was `["c", "h", " ", "i", "o", "e"]`, the second list would
be `[5, 0, 1, 4, 2, 1, 3]`.

Then, a for loop is generated in Bash that iterates over the contents of the second list, using them to index the first array
and build up the input character by character.

ForCode is a great all-around Mutator, that doesn't add significant runtime overhead, on average only doubles the input size, and
doesn't really have any dependencies.

.. _Invoke-DOSfuscation project: https://github.com/danielbohannon/Invoke-DOSfuscation

Side Effects
------------
None.

Detection
---------
ForCode can be detected by looking for a Bash for loop iterating over a long string of integers. Not very common
in benign scripts or commands.

Dependencies
------------
Arrays in Bash, present since version 2.0.
https://wiki.bash-hackers.org/scripting/bashchanges

Runtime Graph
-------------
ForCode overall doesn't add too much runtime overhead, but can be somewhat expensive with large inputs.

.. raw:: html

    <iframe src="../../_static/graphs/token_obfuscators/for_code/runtime_graph.html" height="750px" width="100%"></iframe>

|

Size Graph
----------
ForCode roughly doubles the input when producing payloads, a modest size increase.

.. raw:: html

    <iframe src="../../_static/graphs/token_obfuscators/for_code/size_graph.html" height="750px" width="100%"></iframe>

|
