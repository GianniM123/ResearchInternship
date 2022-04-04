'''Debug module for printing SMT formula to terminal'''
import sys

import pysmt.smtlib.script


def print_smtlib(formula):
    '''Function for printing the pysmt formula to readable output in terminal'''
    script = pysmt.smtlib.script.smtlibscript_from_formula(formula)
    script.serialize(sys.stdout, False)
