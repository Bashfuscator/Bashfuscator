Adding New Mutators to The Framework
====================================

Prerequisites
-------------

So have a great new idea for a new Bash obfuscation technique, and want to
create a new Mutator! Great! Before you start, here's a few things you should make
absolutely sure of:

#. Your obfuscation idea isn't used elsewhere by another Mutator

#. Your obfuscation idea will work with arbitrary Bash code

If you're not sure of either of the above items, just create an issue and discuss it with
the developers. If you are then let's continue!

First Steps
-----------

Creating a Working Proof of Concept
***********************************

Be aware that when writing a Mutator, you are writing code that generates randomized code.
This can be challenging to debug, and although Bashfuscator does come with some options to
make debugging Mutators easier, it's never going to be a trivial task. Therefore, I would
strongly suggest that you come up with a working Proof of Concept in Bash. This step has
helped me a ton, and will give you a reference to refer to when writing your new Mutator.

Take a small Bash input command, such as `echo hi` or `cat /etc/passwd`, and manually obfuscate
it using your proposed obfuscation technique in your terminal or in a script, taking note of the
various steps you need to do to successfully obfuscate your input. This will allow you
to better understand what your Mutator's logic should be.

Once you've created a working PoC, or if you decided to skip that step, you're ready to start creating
your new Mutator.

Deciding on the Type of the New Mutator
***************************************

First, decide what class of Mutators you new Mutator will be in. There is some subjectivity to
this, so just open an issue and discuss this with the developers if you're not sure.

Creating Your Mutator
---------------------

Adding your Mutator to Bashfuscator
***********************************

Next, you'll want to create a new file for your Mutator. Create a new file as the name of your new Mutator under
`bashfuscator/modules/<mutator_type>/`, making sure it is all lowercase and any spaces in the name of your Mutator
are replaced with underscores. This is very important, as deviating from this naming standard will cause Bashfuscator
not to load your Mutator.

For example, if you're creating a String Obfuscator with the name of Test Mutator,
`bashfuscator/modules/string_obfuscators/test_mutator.py` should be created.

Inheriting From the Correct Subclass
************************************

Creating your Mutator is simple; just import the Mutator type you need, ie `from bashfuscator.core.mutators.<mutator_type> import <MutatorType>`,
and create a child class of the imported Mutator type. Only the `name`, `description`, `sizeRating`, and `timeRating` parameters are required,
but you are strongly encouraged to fill out the `author` and `credits` parameters as well. For now, just put a random value from 1-5 in the `sizeRating`
and `timeRating` parameters, we'll come back to them later. There are other optional, advanced parameters you can pass that we'll cover later as well.

As an example, the `Forcode` Mutator is a Token Obfuscator, so this is how it is defined:

.. code-block:: python

    from bashfuscator.core.mutators.token_obfuscator import TokenObfuscator


    class ForCode(TokenObfuscator):
        def __init__(self):
            super().__init__(
                name="ForCode",
                description="Shuffle command and reassemble it in a for loop",
                sizeRating=2,
                timeRating=3,
                author="capnspacehook",
                credits=["danielbohannon, https://github.com/danielbohannon/Invoke-DOSfuscation",
                    "DisectMalare, https://twitter.com/DissectMalware/status/1029629127727431680"]
            )

Defining Necessary Functions
****************************

The `mutate` function the only function that your Mutator is required to implement. `mutate` is the entrypoint of your Mutator, what
Bashfuscator calls when obfuscating input with your Mutator. The `mutate` function must implement this interface:
`mutate(self, userCmd)`. The `userCmd` parameter will contain the input that your Mutator will obfuscate when called.
Your Mutator may contain other supporting functions, so long as they contain code that is used multiple times in `mutate()`, and they
are called from `mutate()`.

Writing The Obfuscation logic
-----------------------------

This is where the fun stuff starts. You are now ready to start writing and testing the logic that will obfuscate Bash code with your new
technique or idea.