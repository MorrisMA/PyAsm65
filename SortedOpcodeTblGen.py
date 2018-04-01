'''
    This program sorts the opcode table into two dictionaries. The first sorts
    on the base opcode. The second sorts on the mnemonic instruction name.
'''

with open('OpcodeTbl.txt', 'rt') as finp:
    lines = finp.readlines()

instrByOpcodeTbl = {}

for line in lines:
    flds = line.split()
    instr, addrMd = flds[0].split('_')
    opLen = int(flds[1])
    dtLen = int(flds[2])
    opcode = flds[3][-2:]

    if opcode in instrByOpcodeTbl:
        instrByOpcodeTbl[opcode].append((instr, addrMd, opLen, dtLen, flds[3]))
    else:
        instrByOpcodeTbl[opcode] = [(instr, addrMd, opLen, dtLen, flds[3])]

        
with open('InstrByOpcodeTbl.txt', 'wt') as fout:
    for instr in instrByOpcodeTbl:
        print(instr, ' ', end='')
        print(instr, ' ', file=fout, end='')
        for i in range(len(instrByOpcodeTbl[instr])):
            if i == 0:
                print(instrByOpcodeTbl[instr][i])
                print(instrByOpcodeTbl[instr][i], file=fout)
            else:
                print('   ', instrByOpcodeTbl[instr][i])
                print('   ', instrByOpcodeTbl[instr][i], file=fout)

instrByNameTbl = {}
maxInstrLen = 0

for line in lines:
    flds = line.split()
    instr, addrMd = flds[0].split('_')
    base = instr.split('.')[0]
    opLen = int(flds[1])
    dtLen = int(flds[2])

    if base[-1].isdigit():
        base = base[:-1]

    if maxInstrLen < len(base):
        maxInstrLen = len(base)

    if base in instrByNameTbl:
        instrByNameTbl[base].append((instr, addrMd, opLen, dtLen, flds[3]))
    else:
        instrByNameTbl[base] = [(instr, addrMd, opLen, dtLen, flds[3])]

with open('InstrByNameTbl.txt', 'wt') as fout:
    maxInstrLen += 1
    for instr in instrByNameTbl:
        padLen = maxInstrLen - len(instr)
        print(instr, ' '*padLen, end='')
        print(instr, ' '*padLen, file=fout, end='')
        for i in range(len(instrByNameTbl[instr])):
            if i == 0:
                print(instrByNameTbl[instr][i])
                print(instrByNameTbl[instr][i], file=fout)
            else:
                print(' '*maxInstrLen, instrByNameTbl[instr][i])
                print(' '*maxInstrLen, instrByNameTbl[instr][i], file=fout)

numUniqueMnemonics = len(instrByNameTbl.keys())
print('Number of unique instruction mnemonics: ', numUniqueMnemonics)


