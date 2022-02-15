import pysmt.smtlib.script

FILE = "debug.txt"

def write_smtlib_no_daggify(formula, fname):
    """Copy from pysmt.shortcuts.write_smtlib, but this one uses daggify. Option not possible on library function.

    :param formula: Specify the SMT formula to be written
    :param fname: Specify the filename
    """
    with open(fname, "w") as fout:
        script = pysmt.smtlib.script.smtlibscript_from_formula(formula)
        script.serialize(fout, False)
