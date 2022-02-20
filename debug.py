import pysmt.smtlib.script

import sys


def write_smtlib_no_daggify(formula):
    """Copy from pysmt.shortcuts.write_smtlib, but this one uses daggify. Option not possible on library function.

    :param formula: Specify the SMT formula to be written
    :param fname: Specify the filename
    """
    
    script = pysmt.smtlib.script.smtlibscript_from_formula(formula)
    script.serialize(sys.stdout, False)

