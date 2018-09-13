from itertools import product
from subprocess import STDOUT, PIPE, Popen

symbols = [" ", "!", "#", "$", "%", "&", "(", ")", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "^", "_", "{", "|", "}", "~"]

u2 = ["".join(p) for p in product(symbols, repeat=2)]
u3 = ["".join(p) for p in product(symbols, repeat=3)]
symbolVars = symbols + u2 + u3

accessElementStr = "${{___['{0}']}}"
setElementStr = "___['{0}']"

expectedVarContents = "bash: -c: line 0: syntax error near unexpected token `;' bash: -c: line 0: `;'\n"

for var in symbolVars:
    command1 = """declare -A ___; {0}="bash"; {1}="c"; {2}=$(eval '{{ {3} -{4} ";"; }} '2'>&'1); echo {5}""".format(
        setElementStr.format(var),
        setElementStr.format("c"),
        setElementStr.format("testVar"),
        accessElementStr.format(var),
        accessElementStr.format("c"),
        accessElementStr.format("testVar")
    )

    command2 = """declare -A ___; {0}="bash"; {1}="c"; {2}=$(eval '{{ {3} -{4} ";"; }} '2'>&'1); echo {5}""".format(
        setElementStr.format("bash"),
        setElementStr.format(var),
        setElementStr.format("testVar"),
        accessElementStr.format("bash"),
        accessElementStr.format(var),
        accessElementStr.format("testVar")
    )

    proc1 = Popen(command1, executable="/bin/bash", stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    stdout1, stderr1 = proc1.communicate()

    proc2 = Popen(command2, executable="/bin/bash", stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    stdout2, stderr2 = proc2.communicate()

    if stdout1 != expectedVarContents or stdout2 != expectedVarContents or stderr1 or stderr2:
        print('"' + var + '"')
