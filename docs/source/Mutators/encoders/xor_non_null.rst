Encode/Xor Non Null
===================

Examples
--------

Without Mangling
****************

.. code-block:: bash

    eval "$(bffiz='_]KLHLZOM';_iG74='<d)';for ((c1cJM8Sf=0;c1cJM8Sf<${#bffiz};c1cJM8Sf++));do ua_sw="${bffiz:$c1cJM8Sf:1}";IqWOmw="$((c1cJM8Sf %${#_iG74}))";IqWOmw="${_iG74:$IqWOmw:1}";[[ "$IqWOmw" == "'" ]]&&IqWOmw="\\'";[[ "$IqWOmw" == "\\" ]]&&IqWOmw='\\';[[ "$ua_sw" == "'" ]]&&ua_sw="\\'";[[ "$ua_sw" == "\\" ]]&&ua_sw='\\';perl -e "print '$ua_sw'^'$IqWOmw'";done;)"

Note: These documented examples may not run due to non printable characters being displayed improperly.

With Mangling
*************

.. code-block:: bash

     ${*} "${@~~}" \eva''l "$(     GG4k7H='DI|' "${@^}"  ;   vtZYF=''"'"'(df0*S4(7>'   ${@//\"TZ:|B}  $*  ;  for ((  ${*,,} i7K6O_=0  "${@~~}"  "${@/^10jJ\(}"  ;  ${@//jZh&sZ/q~vF}   ${*~}  i7K6O_   ${*#\[%AVBt}   ${*%%\}6\[\)k^wf} <  $*   ${@%^^f|}  ${#vtZYF}   "${@%d<ir7v}"   ;   "${@^^}"   i7K6O_   ${*//,W\"em} ++  "${@//Z++AE/aRIKd8}"   "${@~}" ))   ; do  EXpprDuH="${vtZYF:$i7K6O_:7#1  }"   ${@^^}   && _mzUx="$((   ${@//=,X:&,Vy} i7K6O_   ${@,}  ${*//\"S:m^/Nx*\(}   %   ${*^^} ${#GG4k7H}  ${*,}  ))"  ${@%%@twM|z}   && _mzUx="${GG4k7H:$_mzUx:27#1}" "${@,}"   "${@~}"   ;  [[  "$_mzUx" ==   "'" ]]   &&   _mzUx="\\'" ${*,}  ;  [[   "$EXpprDuH"   == "\\"   ]]  && EXpprDuH='\\'  ${*,}  ${*,,}   ;  [[ "$_mzUx"  ==   "\\" ]]  && _mzUx='\\' "${@//OJA^\`T7}"  ${@##Z\(9D5\}}  ;  [[   "$EXpprDuH"   == "'" ]]  &&  EXpprDuH="\\'" ${*}   ; $'\u0070''''e'""$'\u0072l'   -e   "   print   '$EXpprDuH'   ^   '$_mzUx'  "  "${@%%HUk\}\\}"   ${*} ;   done  )" "${@}" 

Note: These documented examples may not run due to non printable characters being displayed improperly.

Description
-----------
This mutator xor's the payload with a key that is generated in such a way as not to cause null bytes in the bash strings produced.

Side Effects
------------
- Even without --full-ascii-strings, it often produces non printable characters.
- When layered with itself and other mutators multiple times, payload sometimes does not execute due to an unexpected null byte, ironically contrary to its intended purpose.

Detection
---------


Dependencies
------------
perl binary

Runtime Graph
-------------

.. raw:: html

    <iframe src="../../_static/graphs/encoders/xor_non_null/runtime_graph.html" height="750px" width="100%"></iframe>

|

Size Graph
----------

.. raw:: html

    <iframe src="../../_static/graphs/encoders/xor_non_null/size_graph.html" height="750px" width="100%"></iframe>

|
