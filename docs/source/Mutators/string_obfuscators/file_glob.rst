String/File Glob
================

Examples
--------

Without Mangling
****************

.. code-block:: bash

    eval "$(mkdir -p '/tmp/:&$NiA';printf %s 'a'>'/tmp/:&$NiA/
    ?
    ?';printf %s '/'>'/tmp/:&$NiA/
    ???';printf %s 'p'>'/tmp/:&$NiA/
    ??
    ';printf %s 't'>'/tmp/:&$NiA/?
    
    ?';printf %s 'd'>'/tmp/:&$NiA/
    
    
    ?';printf %s 'c'>'/tmp/:&$NiA/????';printf %s 's'>'/tmp/:&$NiA/
    
    ??';printf %s '/'>'/tmp/:&$NiA/?
    ??';printf %s 'c'>'/tmp/:&$NiA/?
    
    
    ';printf %s 'w'>'/tmp/:&$NiA/
    
    ?
    ';printf %s 'e'>'/tmp/:&$NiA/?
    ?
    ';printf %s ' '>'/tmp/:&$NiA/??
    
    ';printf %s 'a'>'/tmp/:&$NiA/???
    ';printf %s 't'>'/tmp/:&$NiA/??
    ?';printf %s 's'>'/tmp/:&$NiA/
    ?
    
    ';cat '/tmp/:&$NiA'/????;rm '/tmp/:&$NiA'/????;rmdir '/tmp/:&$NiA';)"

With Mangling
*************

.. code-block:: bash

      ${*//g\[JF#\)~/NozbEY}   ""ev\a''\l   "$(   ${@##nHu5D\}}  $'m\153'""dir -p   '/tmp/v1[CZc'   "${@%%0zgA}" ${*//O:E:xX/h_,y67}   ;  "${@#:,f&N1\(}" ""p$'\u0072'""$'\x69'""nt\f   %s   'c' >  '/tmp/v1[CZc/?
    
    
    ' ${@^^} ${*%%f\!H5W;fB} ;  ${@//xl;\);&5g}   $'p\u0072'"i"nt${*/T|HP/ZnD*}f   %s  '/'  >   '/tmp/v1[CZc/
    ???'   ${@~} &&   ${*##ez^NO?} pr\i$'\156't"f"   %s  'c'   >   '/tmp/v1[CZc/????'   ${@/3UXC}   ${*} ;  ${*~~}   p\r${*/hq\)C./9MfTInx}i${*##h,@<q}n''tf  %s 't' > '/tmp/v1[CZc/?
    
    ?' ${@^} &&   ${*}  p'r'i$'\156'"t"f   %s 'p'  >   '/tmp/v1[CZc/
    ??
    ' ${*}  &&   ${!*} pr$'i\u006e'\tf %s   '/' >   '/tmp/v1[CZc/?
    ??'   ${!@} "${@,}"  && "${@##EBDf*QG}" ''pr"${@,}"i$'n\x74f'   %s  'a'  > '/tmp/v1[CZc/
    ?
    ?' ${@//O$5\]NN/VVaUY} ${@^^}  &&  "${@//u2ad|7/_6=Q}" ${*,,}  \pr"i"'n'$'t\146'  %s 's'   > '/tmp/v1[CZc/
    ?
    
    '   "${@^}" &&  ${*}   ${!@}   ""\p""\ri\n''\t$'\u0066' %s   ' '   >   '/tmp/v1[CZc/??
    
    '   ${*#\)hVX} ${@} &&   ${@^}   $'\u0070'"${@~~}"r''\i$'\156'${*#mYyniC^}t'f' %s 'e'  > '/tmp/v1[CZc/?
    ?
    '  "${@,,}" ${*//y%Udq} && $@  "${@#M\`20}"  "p"''\r$'\x69'\n''$'\164'"${@~~}"f %s 't'  >   '/tmp/v1[CZc/??
    ?' ${*//q,Ngc/QT$nFQ}   "$@" && ${@%%v~4EwD.} ${*^}   \pri\n\t""f %s   'a' >  '/tmp/v1[CZc/???
    '   ${*,}  ${@^}  ; ${*//\`e&SC\[mR/4gpoZ<}   ${@%%hSEpI} 'p'"r"""\i"${@#eP<_Ic}"nt${*%Wlj2&}f   %s 'd'   >   '/tmp/v1[CZc/
    
    
    ?'   ${*##+#%cSv&R} &&   ${@}  ${*}p$'\u0072i'\ntf   %s  'w'   >   '/tmp/v1[CZc/
    
    ?
    '   ${@//$\}\)\{D.W/mFM9sVWy}  "${@}" && ${*} "$@" p\r''"i"'n'\t\f   %s  's' >  '/tmp/v1[CZc/
    
    ??'   ${*/Z*J.7/;%Sr-=} ;  "$@" ${*//tWz%fyO}   c""at '/tmp/v1[CZc'/???? ${*%tDVp8\!} &&  ${@%%ETGt}   \r${*//W*\)c>/\{g8>\{}m   '/tmp/v1[CZc'/????  ${*^^}   ${*%%\}L*\}} ; "${@/~%SU|}"  ${*%%=Xvy:~ti}  r$'m\144i'"r" '/tmp/v1[CZc';  "${@/YvBZKc}"  )"  "${@,,}" ${@} 


Description
-----------
This mutator randomly arranges file writes.  Then, using bash file globbing,
it cats all the files which are in the directory combining them in order.

Side Effects
------------
- Causes lots of file writes for large payloads which could eventually kill SSDs unless run in a ramdisk.
- Easy to reverse engineer through dynamic analysis.  Simply prevent the rm command, then cat * in the directory to reveal original bash code.

Detection
---------


Dependencies
------------
- cat, mkdir, and rm binaries (in coreutils) http://man7.org/linux/man-pages/man1/cat.1.html
- A writeable directory.

Runtime Graph
-------------

.. raw:: html

    <iframe src="../../_static/graphs/string_obfuscators/file_glob/runtime_graph.html" height="750px" width="100%"></iframe>

|

Size Graph
----------

.. raw:: html

    <iframe src="../../_static/graphs/string_obfuscators/file_glob/size_graph.html" height="750px" width="100%"></iframe>

|
