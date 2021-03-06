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
            m = re.split('\s*;[\s\w]*', ln)
            srcText = m[0].rstrip()
            if srcText == '' or srcText == '\n':
                pass
            else:
                curSrc = [inpLine, srcText]
                if '"' in curSrc[1]:
                    ln   = curSrc[1].split('"')
                    flds = re.split('\s', ln[0])[:2]
                    flds.append(ln[1])
                else:
                    flds = re.split('[ \t][\s]*', curSrc[1])
                    if len(flds) < 2:
                        flds.append(str())
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
            lbl, op, dt = newLine[1]
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

def asmPass1(code, data, lbl, op, dt, srcLine,
             opcodes, directives, defines, relative):
    if lbl == '':
        if op in directives:
            if op == directives['.stack'] or op == directives['.stk']:
                stkSize = numVal(dt)            # .stack    size
            elif op == directives['.code'] or op == directives['.cod']:
                if dt != '':
                    code = numVal(dt)           # .code     [address]
            elif op == directives['.data'] or op == directives['.dat']:
                if dt != '':
                    data = numVal(dt)           # .data     [address]
            elif op == directives['.proc'] \
                 or op == directives['.sub'] \
                 or op == directives['.fnc']:   # .proc
                pass
            elif op == directives['.endp']:     # .endp
                pass
            elif op == directives['.end']:      # .end
                pass
            else:
                print('Error. Unknown directive: %s. Line #%d.' % (op, srcLine))
        else:
            if re.match('^\.\w$', op):
                print('Error. Unexpected opcode: %s. Line #%d.' % (op, srcLine))
            else:
                if dt == '':
                    addrsMode = 'imp'
                    operand = ''
                elif re.match('^[aAxXyY]$', dt):
                    addrsMode = dt.lower()
                    operand = dt.lower()
                elif re.match('^#', dt):
                    addrsMode = 'imm'
                    operand = dt[1:]
                elif re.match('^\w*$', dt):
                    if op in relative:
                        addrsMode = 'rel'
                    else:
                        addrsMode = 'abs'
                    operand = dt
                    if re.match('^_\w*$', dt):
                        if dt not in library:
                            library.append(dt)
                elif re.match('^.*,[xX]$', dt):
                    addrsMode = 'zpX'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[xX]\)$', dt):
                    addrsMode = 'zpXI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[sS]$', dt):
                    addrsMode = 'zpS'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[sS]\)$', dt):
                    addrsMode = 'zpSI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^\(.*,[sS]\),[yY]$', dt):
                    addrsMode = 'zpSIY'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[iI][+]{2}$', dt):
                    addrsMode = 'ipp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[iI][+]{2}\)$', dt):
                    addrsMode = 'ippI'
                    operand = dt.split(',')[0][1:]
                else:
                    addrsMode = '???'
                    print('Error. Unknown addressing mode: %s. Line #%d.' \
                          % (dt, srcLine))

                opcode = op + '_' + addrsMode
                if opcode in opcodes:
                    opLen = opcodes[opcode][0]
                    dtLen = opcodes[opcode][1]
                    opDat = opcodes[opcode][2]
                    asmText = '%04X %s%s' % (code, opDat, '00'*dtLen)
                    bufLen = 15 - len(asmText)

                    entry = [code, op, addrsMode, operand, \
                              opLen, dtLen, opDat, ' '*bufLen+' ; '+srcText]
                    code += opLen + dtLen
                    return (True, entry)
                else:
                    print('Error. Unknown opcode: %s. Line #%d.' \
                          % (opcode, srcLine))
    else:
        if lbl in labels or lbl in constants or lbl in variables:
            print('Error: Redefinition of %s in %d' % (lbl, srcLine))
        elif op in directives:
            labels[lbl] = code
            if op == directives['.stack'] or op == directives['.stk']:
                stkSize = numVal(dt)            # .stack    size
            elif op == directives['.code'] or op == directives['.cod']:
                if dt != '':
                    code = numVal(dt)           # .code     [address]
            elif op == directives['.data'] or op == directives['.dat']:
                if dt != '':
                    data = numVal(dt)           # .data     [address]
            elif op == directives['.proc'] \
                 or op == directives['.sub'] \
                 or op == directives['.fnc']:   # .proc
                pass
            elif op == directives['.endp']:     # .endp
                pass
            elif op == directives['.end']:      # .end
                pass
            else:
                print('Error. Unknown directive: %s. Line #%d.' % (op, srcLine))
        else:
            if op == '':
                labels[lbl] = code
            elif op in defines:
                if op == '.eq' or op == '.equ':
                    constants[lbl] = numVal(dt)
                elif op == '.db' or op == '.byt':
                    siz = int(dt)
                    val = '00'*siz
                    variables[lbl] = (data, siz, val)

                    asmText = '%04X %s' % (data, val[:8])
                    bufLen = 15 - len(asmText)
                    dat.append([data, lbl, 'db', dt, siz, 0, val, \
                                ' '*bufLen+' ; '+srcText])
                    data += siz
                elif op == '.ds' or op == '.str':
                    siz = len(dt)
                    variables[lbl] = (data, siz, dt)
                    strVal = []

                    for ch in dt:
                        strVal.append('%02X' % (ord(ch)))
                    strVal = ''.join(strVal)

                    asmText = '%04X %s' % (data, strVal[:8])
                    bufLen = 15 - len(asmText)
                    dat.append([data, lbl, 'ds', dt, siz, 0, strVal, \
                                ' '*bufLen+' ; '+srcText])
                    data += siz
                else:
                    print('Error. Unknown define: %s.' % (op))
                    pass
            else:
                if dt == '':
                    addrsMode = 'imp'
                    operand = ''
                elif re.match('^[aAxXyY]$', dt):
                    addrsMode = dt.lower()
                    operand = dt.lower()
                elif re.match('^#', dt):
                    addrsMode = 'imm'
                    operand = dt[1:]
                elif re.match('^\w*$', dt):
                    if op in relative:
                        addrsMode = 'rel'
                    else:
                        addrsMode = 'abs'
                    operand = dt
                    if re.match('^_\w*$', dt):
                        if dt not in library:
                            library.append(dt)
                elif re.match('^.*,[xX]$', dt):
                    addrsMode = 'zpX'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[xX]\)$', dt):
                    addrsMode = 'zpXI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[sS]$', dt):
                    addrsMode = 'zpS'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[sS]\)$', dt):
                    addrsMode = 'zpSI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^\(.*,[sS]\),[yY]$', dt):
                    addrsMode = 'zpSIY'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[iI][+]{2}$', dt):
                    addrsMode = 'ipp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[iI][+]{2}\)$', dt):
                    addrsMode = 'ippI'
                    operand = dt.split(',')[0][1:]
                else:
                    addrsMode = '???'
                    print('Error. Unknown addressing mode: %s. Line #%d.' \
                          % (dt, srcLine))

                opcode = op + '_' + addrsMode

                if opcode in opcodes:
                    opLen = opcodes[opcode][0]
                    dtLen = opcodes[opcode][1]
                    asmText = '%04X %s%s' % (code, opDat, '00'*dtLen)
                    bufLen = 15 - len(asmText)

                    entry  = [code, op, addrsMode, operand, \
                              opLen, dtLen, opDat, ' '*bufLen+' ; '+srcText]
                    code += opLen + dtLen
                    return (True, entry)
                else:
                    print('Error. Unknown opcode: %s. Line #%d.' \
                          % (opcode, srcLine))
    return (None, None)


