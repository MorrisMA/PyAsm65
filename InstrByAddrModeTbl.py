filename = 'OpcodeTbl.txt'

addrMdTbl = dict()

maxAddrMdLen = int(0)
maxOpcodeLen = int(0)
maxOpDataLen = int(0)

with open(filename, 'rt') as finp:
    opcodeTbl = finp.readlines()
    
print(len(opcodeTbl))

for line in opcodeTbl:
    fld = line.split()
    opcode = fld[0]
    opLen  = fld[1]
    dtLen  = fld[2]
    opDat  = fld[3]
    
    addrMd = fld[0].split('_')[1]
    entry  = list([fld[0], fld[1], fld[2], fld[3]])
    
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

print(len(addrMdTbl.keys()))

for key in addrMdTbl:
    print('%*s' % (maxAddrMdLen, key), ':', len(addrMdTbl[key]))
    for i in range(len(addrMdTbl[key])):
        print(' '*maxAddrMdLen, ':', '%3d' % i, addrMdTbl[key][i])
