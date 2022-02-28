import pysmt.smtlib.script

import sys

import json

debug_file = "debug.dot"
def print_smtlib(formula):
    script = pysmt.smtlib.script.smtlibscript_from_formula(formula)
    script.serialize(sys.stdout, False)

def write_statistics(str):
    with open(debug_file + ".log", 'w') as f:
        f.write(json.dumps(str))