'''
    This program sorts the Opcode Table by the primary opcode.
'''

with open('OpcodeTbl.txt', 'rt') as finp:
    lines = finp.readlines()

instrTbl = {}

for line in lines:
    flds = line.split()
    instr = flds[0]
    opLen = int(flds[1])
    dtLen = int(flds[2])
    opcode = flds[3][-2:]
    prefix = flds[3][:-2]
    addrMd = flds[4]

    if opcode in instrTbl:
        instrTbl[opcode].append((instr, opLen, dtLen, opcode, prefix, addrMd))
    else:
        instrTbl[opcode] = [(instr, opLen, dtLen, opcode, prefix, addrMd)]
        
with open('InstrByOpcodeTbl.txt', 'wt') as fout:
    for instr in instrTbl:
        print(instr, ' ', end='')
        print(instr, ' ', file=fout, end='')
        for i in range(len(instrTbl[instr])):
            if i == 0:
                print(instrTbl[instr][i])
                print(instrTbl[instr][i], file=fout)
            else:
                print('   ', instrTbl[instr][i])
                print('   ', instrTbl[instr][i], file=fout)

instrTbl.clear()
instrLen = 0

for line in lines:
    flds = line.split()
    instr = flds[0].split('_')[0]
    base = instr.split('.')[0]
    opLen = int(flds[1])
    dtLen = int(flds[2])
    opcode = flds[3][-2:]
    prefix = flds[3][:-2]
    addrMd = flds[4]

    if instrLen < len(base):
        instrLen = len(base)

    if base in instrTbl:
        instrTbl[base].append((instr, addrMd, opLen, dtLen, opcode, prefix))
    else:
        instrTbl[base] = [(instr, addrMd, opLen, dtLen, opcode, prefix)]

with open('InstrByNameTbl.txt', 'wt') as fout:
    instrLen += 1
    for instr in instrTbl:
        padLen = instrLen - len(instr)
        print(instr, ' '*padLen, end='')
        print(instr, ' '*padLen, file=fout, end='')
        for i in range(len(instrTbl[instr])):
            if i == 0:
                print(instrTbl[instr][i])
                print(instrTbl[instr][i], file=fout)
            else:
                print(' '*instrLen, instrTbl[instr][i])
                print(' '*instrLen, instrTbl[instr][i], file=fout)

numInstructions = len(list(instrTbl.keys())) - 32
print('Number of unique instruction mnemonics: ', numInstructions)


