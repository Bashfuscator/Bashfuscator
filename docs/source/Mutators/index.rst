Mutator Documentation
=====================

Size and Time Ratings
---------------------
Bashfuscator has a size and time rating system to help users find obfuscators that work best with their goals. For sandbox evasion, for example, a runtime increasing obfuscator may be useful. The size and time rating system is also designed to help developers benchmark their obfuscators.  The size and time rating systems use Big O notation to break mutators into categories depending on their size and time increase rates.  The time_measure.py script is used to generate test data and automate statistical analysis of the results.  The script runs obfuscated and unobfuscated versions of the same command and measures differences in size and execution time.

Testing Methodology:
********************
In order to remove as much system dependent execution time as possible, the unobfuscated input command is ":;" repeated to form "commands" of different lengths. (":" is a bash alias for true.)  This command interacts minimally with the testing system.

In order to generate reliable data, several precautions were taken. For formal testing, each mutator was run 10 times at each data point and the average values are plotted to the graph. To get a larger snapshot of how the mutator behaves, commands from length 1 to length 10,000 were tested.  Datapoints are linearly spaced.

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
| 3: O(5n), Linnear with constant of 5   | Base 64                    |
+----------------------------------------+----------------------------+
| 4: O(kn), Linnear with constant k > 5  | Hex Hash, Special Char Only|
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


Index
-----

.. toctree::

   command_obfuscators/index
   string_obfuscators/index
   token_obfuscators/index
   encoders/index
