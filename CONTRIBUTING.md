# Bashfuscator Contribution Guide

## Style Guide

### Bashfuscator conforms to the PEP8 standard except for a few key differences:

1. Class, function and variable names are camelCase, with class names starting with an uppercase letter. Constant variables are named the normal way, all uppercase with an '_' separating words in the name.

2. Tabs are used in favor of spaces for indentation.

### Other miscellaneous style rules to follow:

- Always put whitespace between assignment, binary, comparison and Boolean operators:

```python
self.payload += "cat '" + self.workingDir + "'/" + "?" * cmdLogLen + ";"     #good

self.payload+="cat '"+self.workingDir+"'/"+"?"*cmdLogLen+";"                 #not preferred
```

- Always put a blank line before the return statement of any returning function:

```python
def getPrefRange(self, pref):
        if pref == 0:
            min = max = 1
        elif pref == 1:
            min = 1
            max = 2
        elif pref < 4:
            min = 1
            max = pref + 2
        else:
            min = max = 5

        return (min, max)       #notice the blank line before the return
```

- Always put a space before and after parameters when passing multiple parameters to a function:

```python
prefStubs = self.getPrefItems(prefStubs, sizePref, timePref)    #good
prefStubs = self.getPrefItems(prefStubs,sizePref,timePref)      #not preferred
```

- Use double quotes for string whenever possible. Single quoted strings are acceptable if the string contains double quotes inside of it:

```python
if userOb.split("/")[0] == "command":                           #good
if userOb.split('/')[0] == 'command':                           #not preferred

self.payload += 'printf -- "\\x$(printf \'' + randomString      #ok, string contains double quotes
```

- When adding imports to files, make sure the imports are alphabetical, and when possible import only what functions and classes that are needed.

```python
import binascii
from sys import exit        #good
exit(0)

import sys                  #only needed to import sys.exit
import binascii             #not in alphabetical order
sys.exit(0)
```

---

## Adding Obfuscators

Obfuscators are the bread and butter of Bashfuscator. The more obfuscators Bashfuscator contains, the more the obfuscation possibilities increase. Adding an obfuscator to the Bashfuscator framework is a great way to contribute to the project, and a potentially easy way as well. Bashfuscator has been built from the ground up with modularity and extendability in mind, ease of contribution was and is one of the main goals of the project. Before diving in and start working on your new obfuscator, take a minute and read the guide below. It will make the development process quicker and smoother, and compliance is required before any new obfuscators are submitted.

Before starting work on a new obfuscator, be sure that:

1. What it does is unique, and adds functionality not already present to Bashfuscator.
2. It will be able to be layered on top of any other obfuscator, and be able to handle all valid bash code, not just a subset.

### Common Guidelines and Requirements For All Obfuscators

While the different obfuscator types are different, they share a few things in common. To maintain consistency and to ensure smooth operation of the Bashfuscator framework, several things are required of all obfuscators:

- Must have define the `sizeRating` and depending on the obfuscator type, the `timeRating` attributes found through the measurement process (Right now there isn't a measurement process, just guess until we come up with one).

- If the majority of the code for your obfuscator was borrowed from elsewhere, or if someone else inspired the idea for your obfuscator, put their Github or Twitter username, or whatever you know them by in the `credits` attribute. If you have a link to the Github repo, blog post, whitepaper, ect that inspired you, put that here as well. Otherwise put your Github username in the `credits` attribute.

- Must implement an `obfuscate()` function. The parameters of the `obfuscate()` function will vary between obfuscator types, but every obfuscator must implement one. All obfuscation that the obfuscator is capable of must happen through this function.

- Functions other than `obfuscate()` will be created only if they are necessary to avoid reusing code, or to separate logic if the obfuscation process is sufficiently complex.

- `self.originalCmd = userCmd` is the first line of `obfuscate()`. This is to ensure that the obfuscated and clear command for every layer is kept if need.

- At the very end of `obfuscate()`, the obfuscated command will be assigned to `self.payload`, and `self.payload` will be returned. `self.payload` must not be used anywhere else in the `obfuscate()` function to avoid errors when layering payloads.

---

### Adding Token Obfuscators

#### Token Obfuscator Definition

If an obfuscator is able to be deobfuscated and executed by bash at runtime, without bash having to execute a stub or any code, then it is a Token Obfuscator.

#### Token Obfuscator Layout

```python
class TokExample(TokenObfuscator):
    def __init__(self):
        super().__init__(
            name="Obfuscator Name",
            description="Description of how the obfuscator changes the input",
            sizeRating=3
            credits="Creator of the obfuscator, or who or where inpiration for the obfuscator or code is from"
        )

    # where the magic happens
    def obfuscate(self, sizePref, userCmd):
        self.originalCmd = userCmd              #required first line of obfuscate()

        obCmd = "Obfuscate userCmd here"
        obCmd = ...

        self.payload = obCmd                    #required before returning

        return self.payload
```

---

### Adding Command Obfuscators

#### Command Obfuscator Definition

If an obfuscator requires a deobfuscation stub to execute, then it is a command obfuscator.

#### Command Obfuscator Layout

```python
class CmdExample(CommandObfuscator):
    def __init__(self):
        super().__init__(
            name="Obfuscator Name",
            description="Description of how the obfuscator changes the input",
            sizeRating=2,
            timeRating=1,
            reversible=True,
            credits="Creator of the obfuscator, or who or where inpiration for the obfuscator or code is from"
        )

        #stub will be selected automatically, or manually by user
        self.stubs = [
            Stub(
                name="Stub Name",
                binariesUsed=["List of binaries", "the stub uses"],
                sizeRating=1,
                timeRating=1,
                escapeQuotes=True,
                stub="""Actual stub code"""
            ),
        ]

    def obfuscate(self, sizePref, timePref, userCmd):
        self.originalCmd = userCmd                              #required first line

        obCmd = "Obfuscate userCmd here"
        obCmd = ...

        self.payload = self.deobStub.genStub(sizePref, obCmd)   #required before returning

        return self.payload
```

---

## Git Guidelines

- Commit early and often. More numerous, smaller commits are prefered to few large ones.
- Write meaningful commit messages. 'Misc tweaks' doesn't describe what was changed at all. When someone needs to go back and find that one commit that broke things, meaningful commit names make the process much less painful.
- Try to accomplish one main thing in each commit. Don't try to fix 5 issues in one commit, or add 3 features either.
