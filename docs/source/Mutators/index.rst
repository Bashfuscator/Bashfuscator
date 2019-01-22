Mutator Documentation
=====================

Size and Time Ratings
---------------------
Bashfuscator has a size and time rating system to help users find obfuscators that work best with their goals. For sandbox evasion, for example, a runtime increasing obfuscator may be useful. The size and time rating system is also designed to help developers benchmark their obfuscators.  The size and time rating systems use Big O notation to break mutators into categories depending on their size and time increase rates.  The time_measure.py script is used to generate test data and automate statistical analysis of the results.

Size Ratings
************
The size rating system rates mutators based on the number of characters added to the original command once it has been obfuscated.

Size Ratings Table:
###################

+----------------------------------------+----------------------------+
| Size Rating                            | Obfuscator                 | 
+========================================+============================+
| 1: O(1), Little to no size increase    | Case Swapper, Reverse      |
+----------------------------------------+----------------------------+
| 2: O(log(n)), Logarithmic growth rate  | Folder Glob, File Glob     |
+----------------------------------------+----------------------------+
| 3: O(5n), Linnear with constant of 5   | Special Char Only, Base 64 |
+----------------------------------------+----------------------------+
| 4: O(kn), Linnear with constant k > 5  | Hex Hash                   |
+----------------------------------------+----------------------------+
| 5: O(n^2), exponential or worse        |                            |
+----------------------------------------+----------------------------+ 


Example:
########

The String/HexHash mutator adds a constant number of characters for every character in the original command, so it has a linnear growth rate.  Because HexHash adds a relatively large amount of additional characters, it is given the "Large Linnear" growth rate and assigned the size rating of 4.

Time Ratings
************
The time rating system rates mutators based on the runtime increase caused by a mutator.


Time Ratings Table
##################


.. toctree::

   command_obfuscators/index
   string_obfuscators/index
   token_obfuscators/index
   encoders/index
