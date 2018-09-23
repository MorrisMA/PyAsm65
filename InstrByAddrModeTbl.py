filename = 'OpcodeTbl.txt'

addrMdTbl = dict()

maxAddrMdLen = int(0)
maxOpcodeLen = int(0)
maxOpDataLen = int(0)

with open(filename, 'rt') as finp:
    opcodeTbl = finp.readlines()
    
for line in opcodeTbl:
    fld = line.split()
    opcode = fld[0]
    opLen  = fld[1]
    dtLen  = fld[2]
    opDat  = fld[3]
    
    addrMd = fld[0].split('_')[1]
    entry  = list([opcode, opLen, dtLen, opDat])
    
    if addrMd in addrMdTbl:
        addrMdTbl[addrMd].append(entry)
    else:
        addrMdTbl[addrMd] = []
        addrMdTbl[addrMd].append(entry)
    
    lenAddrMd = len(addrMd)
    if maxAddrMdLen < len(addrMd): maxAddrMdLen = lenAddrMd
    lenOpcode = len(opcode)
    if maxOpcodeLen < lenOpcode: maxOpcodeLen = lenOpcode
    lenOpData = len(opDat)
    if maxOpDataLen < lenOpData: maxOpDataLen = lenOpData

#with open('OpcodeTblByAddrModeKeys.txt', 'wt') as fout:
#    for key in addrMdTbl.keys():
#        print(key, file=fout)

keys = list()
with open('SortedAddrModeKeys.txt', 'rt') as finp:
    while True:
        line = finp.readline()
        if line == '':
            break
        else: keys.append(line[:-1])

print('-'*80)
print(len(addrMdTbl.keys()), len(opcodeTbl), len(keys))
print('-'*80)

numInstructions = int()
for key in keys:
    print('%-*s' % (maxAddrMdLen, key), ':', '%-3d' % len(addrMdTbl[key]))
    addrsModeListLen = len(addrMdTbl[key])
    numInstructions += addrsModeListLen
    for i in range(addrsModeListLen):
        opcode, opLen, dtLen, opDat = addrMdTbl[key][i]
        print(' '*maxAddrMdLen, ':', 
              '%-3d' % i, 
              '[%-*s, %d, %d, %*s]' % (maxOpcodeLen, opcode,
                                       int(opLen),
                                       int(dtLen),
                                       maxOpDataLen, opDat))
    print('-'*80)
print(numInstructions)
