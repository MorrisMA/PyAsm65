filename = 'InstrByOpcodeTbl.txt'

with open(filename, 'rt') as finp:
    opcodeTblList = finp.readlines()

with open(filename, 'wt') as fout:
    for line in opcodeTblList:
        fld = line.split('(')
        opcode = fld[0]
        fld = fld[1].split(')')[0].split(',')
        inst = fld[0].rstrip().ljust(8)
        addr = fld[1].rstrip().ljust(10)
        iLen = fld[2].rstrip()
        dLen = fld[3].rstrip()
        oStr = fld[4].rstrip().rjust(11)
        print('%s(%s,%s,%s,%s,%s)' % (opcode, inst, addr, iLen, dLen,oStr), file=fout)
