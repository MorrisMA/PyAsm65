'''
    Module to open and create Opcode Table
'''

import os
import re

directives = {'.stack' : '.stack', 
              '.stk'   : '.stk', 
              '.code'  : '.code',
              '.cod'   : '.cod', 
              '.data'  : '.data',
              '.dat'   : '.dat', 
              '.proc'  : '.proc',
              '.endp'  : '.endp',
              '.sub'   : '.sub', 
              '.ends'  : '.ends',
              '.fnc'   : '.fnc', 
              '.endf'  : '.endf',
              '.end'   : '.end', }

defines    = ('.eq', '.equ', 
              '.db', '.byt', 
              '.dw', '.wrd', 
              '.dl', '.lng',
              '.df', '.flt',
              '.dd', '.dbl', 
              '.ds', '.str', )

             # ---    IND    SIZ    ISZ
relative   = ('bpl', 'jpl', 'bgt', 'jgt',   #10
              'bmi', 'jmi', 'ble', 'jle',   #30
              'bvc', 'jvc', 'blt', 'jlt',   #50
              'bvs', 'jvs', 'bge', 'jge',   #70
             # --------------------------
              'bra', 'jra',                 #80
             # --------------------------
              'bcc', 'jcc', 'bls', 'jls',   #90
              'bcs', 'jne', 'bhi', 'jhi',   #B0
              'bne', 'jcs', 'blo', 'jlo',   #D0
              'beq', 'jeq', 'bhs', 'jhs',   #F0
             # --------------------------
              'phr', 'csr', )               #5C

def loadOpcodeTable(fn = 'OpcodeTbl', genOpcodeLst = False):
    opcodes = dict()
    
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
        
        lbl = op = dt = ''
        numFlds = len(newLine[1])
        
        if numFlds > 2:
            lbl, op, dt, *_ = newLine[1]
        elif numFlds > 1:
            lbl, op = newLine[1]
        else: lbl = newLine[1]
        
        if op in ['lda', 'lda.w'] and dt[0] == '#':
            nxtLine = source[i+1]
            
            nxtLbl = nxtOp = nxtDt = ''
            numFlds = len(nxtLine[1])
            
            if numFlds > 2:
                nxtLbl, nxtOp, nxtDt, *_ = nxtLine[1]
            elif numFlds > 1:
                nxtLbl, nxtOp = nxtLine[1]
            else: NxtLbl = nxtLine[1]
            
            if nxtOp in ['pha', 'pha.w', 'pha.s', 'pha.sw'] and nxtLbl == '':
                #print('======> %d, %s, %s' %(i, source[i][1], nxtLine[1]), end='')
                op = 'psh'+'.'+nxtOp.split('.')[1]
                newLine = [[inpLine, lbl+'\t'+op+' '+dt], \
                           [lbl, op, dt]]
                i += 1
                #print(' =>> %d, %s' % (i, newLine[1]))
        
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
            val = 0
            print('Error. Unknown numeric representation.')
    else:
        val = int(dt)
    return val
    
def parseByt(dt, vlc):
    inpList = list()
    strVal = str()
    dtLen = len(dt)
    i = 0
    while i < dtLen:
        ch = dt[i]; i += 1
        if ch == ',':
            inpList.append(strVal)
            strVal = ''
            continue
        elif ch == '"':
            strVal += ch
            while i < dtLen:
                ch = dt[i]; strVal += ch; i += 1
                if ch == '"': break
        else: strVal += ch
    else:
        inpList.append(strVal)
        
    siz = 0
    for i in range(len(inpList)):
        if inpList[i][0] == '"':
            strDat = inpList[i][1:-1]
            siz += len(strDat)
        elif ']' in inpList[i]:
            flds = str(inpList[i]).split('[')
            try:
                siz += eval(str(flds[1][:-1]), vlc)
            except:
                print('\tError(parseByt): eval([%s]) failed' % flds[1][:-1])
                siz = -1
                break
        else: siz += 1

    return (siz, inpList)

def parseWrd(dt, vlc):
    inpList = list()
    strVal = str()
    dtLen = len(dt)
    i = 0
    while i < dtLen:
        ch = dt[i]; i += 1
        if ch == ',':
            inpList.append(strVal)
            strVal = ''
            continue
        else: strVal += ch
    else:
        inpList.append(strVal)
        
    siz = 0
    for i in range(len(inpList)):
        if ']' in inpList[i]:
            flds = str(inpList[i]).split('[')
            try:
                siz += eval(str(flds[1][:-1]), vlc)
            except:
                print('\tError(parseWrd): eval([%s]) failed' % flds[1][:-1])
                siz = -1
                break
        else: siz += 1

    return (2 * siz, inpList)

def parseLng(dt, vlc):
    inpList = list()
    strVal = str()
    dtLen = len(dt)
    i = 0
    while i < dtLen:
        ch = dt[i]; i += 1
        if ch == ',':
            inpList.append(strVal)
            strVal = ''
            continue
        else: strVal += ch
    else:
        inpList.append(strVal)
        
    siz = 0
    for i in range(len(inpList)):
        if ']' in inpList[i]:
            flds = str(inpList[i]).split('[')
            try:
                siz += eval(str(flds[1][:-1]), vlc)
            except:
                print('\tError(parseLng): eval([%s]) failed' % flds[1][:-1])
                siz = -1
                break
        else: siz += 1

    return (4 * siz, inpList)

def evalByt(inpList, vlc):        
    siz = 0; outStr = str(); lenList = len(inpList)
    for i in range(lenList):
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
                val = -1

            try:
                rep = eval(str(cnt), vlc)
            except:
                rep = 1

            val &= 0xFF
                
            for i in range(rep):
                outStr += "%02X" % val
                siz += 1
    return (siz, outStr)

def evalWrd(inpList, vlc):
    siz = 0; outStr = str(); lenList = len(inpList)
    for i in range(lenList):
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
            if '$' in dat:
                flds = dat.split('$')
                dat = '_loc_'.join(flds)
            val = eval(str(dat), vlc)
        except:
            val = -1

        try:
            rep = eval(str(cnt), vlc)
        except:
            rep = 1

        val &= 0xFFFF
            
        for i in range(rep):
            wrdStr = "%04X" % val
            outStr += wrdStr[2:] + wrdStr[:2]
            siz += 1
    return (2*siz, outStr)

def evalLng(inpList, vlc):
    siz = 0; outStr = str(); lenList = len(inpList)
    for i in range(lenList):
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
            if '$' in dat:
                flds = dat.split('$')
                dat = '_loc_'.join(flds)
            val = eval(str(dat), vlc)
        except:
            val = -1

        try:
            rep = eval(str(cnt), vlc)
        except:
            rep = 1

        val &= 0xFFFFFFFF
            
        for i in range(rep):
            wrdStr = "%08X" % val
            outStr += wrdStr[6:] + wrdStr[4:6] + wrdStr[2:4] + wrdStr[:2]
            siz += 1
    return (4*siz, outStr)


