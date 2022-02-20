import pysmt.smtlib.script

import sys


def print_smtlib(formula):
    script = pysmt.smtlib.script.smtlibscript_from_formula(formula)
    script.serialize(sys.stdout, False)

