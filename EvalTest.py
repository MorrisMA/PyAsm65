""""
    Test of the eval()
        Expected use is as an expression evaluator for PyAsm65 in order to
        support complex expressions for constants and operands. The expecta-
        tion is that Pass 2 of the assembler can use the symbol tables to
        automatically perform the evaluation of a large number of expressions
        that may be used by the programmer.

        Some preparation of the strings passed to eval() may be required to
        support the various classes of operands that the expressions represent.
        For example, expressions preceeded by '#' that signify immediate values,
        or expressions embedded in one or two parentheses:

            '(' expr ')'   or '((' expr '))'
            '(' expr ',X)' or '((' expr ',X))'
            '(' expr ',S)' or '((' expr ',S))'
            '(' expr ',A)' or '((' expr ',A))'

        In addition, special operations that define operations that return
        elements of the expression, such as the most significant or least
        significant byte of the result, will have to be specifically handled
        by the parser before passing the string to be evaluated to eval().
"""

import math

variables = {'var1':2.5,}
constants = {'const1':22/7,
             'const2':333/106,
             'const3':355/113,
             'pi':math.pi,}

while True:
    evalStr = input('Enter string to evaluate: ')
    if evalStr != '':
        print(evalStr, '=', eval(evalStr, variables, constants))
    else: break
