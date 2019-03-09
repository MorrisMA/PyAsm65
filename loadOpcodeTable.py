'''
    Module to open and create Opcode Table
'''

import os
import re

def loadOpcodeTable(opcodes, fn = 'OpcodeTbl', genOpcodeLst = False):
    '''
        Read Opcodes Table
    '''

    with open(fn + '.txt', 'rt') as finp:
        opcodeTbl = finp.readlines()

    print('len(OpcodeTbl) = %d' % (len(opcodeTbl)))
    
    '''
        Create Opcodes Dictionary
    '''

    maxWidth = 0
    for opcode in opcodeTbl:
        op = opcode.split()
        key = op[0]
        if key in opcodes:
            print('Error - duplicate key found: %s' % (key))
        else:
            opcodes[key] = [int(op[1]), int(op[2]), op[3]]
        if len(key) > maxWidth:
            maxWidth = len(key)

    '''
        Print Opcode Table Listing
    '''

    if genOpcodeLst:
        with open(fn + '.lst', 'wt') as fout:
            print('-'*80, file=fout)
            print('\tOpcode Table', file=fout)
            print('-'*80, file=fout)
            print(file=fout)
            for key in opcodes:
                print('%-*s' % (maxWidth, key),':',opcodes[key], file=fout)
            print(file=fout)
            print('-'*80, file=fout)
            print(file=fout)

    return opcodes

