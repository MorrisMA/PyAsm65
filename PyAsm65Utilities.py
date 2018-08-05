'''
    Module to open and create Opcode Table
'''

import os

def loadOpcodeTable(fn = 'OpcodeTbl', genOpcodeLst = False):
    '''
        Read Opcodes Table
    '''

    with open(fn+'.txt', 'rt') as finp:
        opcodeTbl = finp.readlines()

    '''
        Create Opcodes Dictionary
    '''

    opcodes = dict()
    maxWidth = 0
    for opcode in opcodeTbl:
        op = opcode.split()
        key = op[0]
        opcodes[key] = [int(op[1]), int(op[2]), op[3]]
        if len(key) > maxWidth:
            maxWidth = len(key)

    '''
        Print Opcode Table Listing
    '''

    if genOpcodeLst:
        with open(fn+'.lst', 'wt') as fout:
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

def numVal(dt):
    if len(dt) == 1:
        val = int(dt)
    elif dt[0] == '0':
        radix = dt[1]
        if radix == 'b':
            val = int(dt, base=2)
        elif radix == 'o':
            val = int(dt, base=8)
        elif radix == 'x':
            val = int(dt, base=16)
        else:
            print('Error. Unknown numeric representation.')
    else:
        val = int(dt)
    return val
    
