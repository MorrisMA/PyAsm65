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

def readSource(filename):
    '''
        readSource - generator that reads a file
            removes comments / blank lines
            splits non-blank lines into fields
            associates lines produced with non-blank input lines
    '''
    finp = open(filename+'.asm', 'rt')
    inpLine = 1
    while True:
        ln = finp.readline()
        if ln == '':
            finp.close()
            return
        else:
#            m = re.split('\s*;[\s\w]*', ln)
#            srcText = m[0].rstrip()
            srcText = ln.rstrip()
            if srcText == '' or srcText == '\n':
                pass
            else:
                curSrc = [inpLine, srcText]
                ln = curSrc[1]
                lnLen = len(ln)
                i = 0; flds = list(); fld = str()
                while i < lnLen:
                    if ln[i] == ';':
                        if fld != '':
                            flds.append(fld)
                        elif len(flds) == 1 and flds[0] == '':
                            flds = list()
#                        print('-'*7+'>', curSrc, i, ln[i], flds)
                        break
                    elif ln[i] in [' ', '\t']:
                        while ln[i] in [' ', '\t'] and i < lnLen:
                            i += 1
                        flds.append(fld)
                        fld = str()
                    elif ln[i] == '"':
                        flds.append(fld)
                        fld = ln[i]
                        i += 1
                        while i < lnLen:
                            ch = ln[i]
                            fld += ch
                            i += 1
                            if ch == '"': break
                        flds.append(fld)
                        fld = str()
                    else:
                        ch = ln[i]
                        if ch in [' ', '\t']:
                            flds.append(fld)
                            fld = str()
                            continue
                        else:
                            fld += ch
                        i += 1
                else:
                    flds.append(fld)            
                if flds != []:
                    yield [curSrc, flds]
            inpLine += 1

def pho_ldaImmPha_to_pshImm(source):
    print('ldaImmPha_to_pshImm')
    newSrc = []
    length  = len(source) - 1
    i = 0
    while i < length:
        newLine = source[i]
        inpLine, *_ = newLine[0]
        try:
            lbl, op, dt, *_ = newLine[1]
        except:
            try:
                lbl, op = newLine[1]
                dt = ''
            except:
                print('ERROR: line=%d, %s' % (i, newLine))
        if op in ['lda', 'lda.w'] and dt[0] == '#':
            nxtLine = source[i+1]
            try:
                nxtLbl, nxtOp, *_ = nxtLine[1]
            except:
                nxtLbl, nxtOp = nxtLine[1]
            if nxtOp in ['pha', 'pha.w', 'pha.s', 'pha.sw'] and nxtLbl == '':
                op = 'psh'+'.'+nxtOp.split('.')[1]
                newLine = [[inpLine, lbl+'\t'+op+' '+dt], \
                           [lbl, op, dt]]
                i += 1
        newSrc.append(newLine)
        i += 1
    return newSrc

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
    
def evalByt(dt, vlc):
    inpList = list(); strStrt = False; strVal = str()
    for i in range(len(dt)):
        if dt[i] == '"':
            if strStrt:
                strStrt = False
            else: strStrt = True
        elif dt[i] == ',' and not strStrt:
            inpList.append(strVal)
            strVal = ''
            continue
        strVal += dt[i]
    else:
        inpList.append(strVal)

    if '";"' in dt:
        print('==>>'*8, dt, inpList)
        
    siz = 0; outStr = str()
    for i in range(len(inpList)):
        if inpList[i][0] == '"':
            strDat = inpList[i][1:-1]
            for ch in strDat:
                outStr += "%02X" % ord(ch)
                siz += 1
        else:
            if ']' in inpList[i]:
                flds = str(inpList[i]).split('[')
                dat  = flds[0]
                if '' == dat:
                    dat = '0'
                cnt  = flds[1][:-1]
            else:
                dat = inpList[i]
                cnt = 1

            try:
                val = eval(str(dat), vlc)
            except:
#                print('\tError: eval(%s) failed' % dat)
                val = -1

            try:
                rep = eval(str(cnt), vlc)
            except:
#                print('\tError: eval(%s) failed' % cnt)
                rep = 1

            val &= 0xFF
                
            for i in range(rep):
                outStr += "%02X" % val
                siz += 1
    return (siz, outStr)

def evalWrd(dt, vlc):
    inpList = dt.split(',')
    siz = 2*len(inpList)
    outStr = str()
    for i in range(len(inpList)):
        inpStr = inpList[i]
        if inpStr[0] == '$':
            inpStr = '_loc_' + inpStr[1:]
        try:
            val = eval(str(inpStr), vlc)
        except:
#            print('\tError: eval(%s) failed' % inpList[i])
            val = -1
        wrd = "%04X" % val
        outStr += wrd[2:] + wrd[:2]

    return (siz, outStr)

def evalLng(dt, vlc):
    inpList = dt.split(',')
    siz = 4*len(inpList)
    outStr = str()
    for i in range(len(inpList)):
        try:
            val = eval(str(inpList[i]), vlc)
        except:
#            print('\tError: eval(%s) failed' % inpList[i])
            val = -1
        lng = "%04X" % val
        outStr += lng[6:] + lng[4:6] + lng[2:4] + lng[:2]
    return (siz, outStr)
