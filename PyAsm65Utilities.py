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

              # ---    IND    SIZ    ISZ
conditional = ('bpl', 'jpl', 'bgt', 'jgt',   #10
               'bmi', 'jmi', 'ble', 'jle',   #30
               'bvc', 'jvc', 'blt', 'jlt',   #50
               'bvs', 'jvs', 'bge', 'jge',   #70
              # --------------------------
               'bcc', 'jcc', 'bls', 'jls',   #90
               'bcs', 'jne', 'bhi', 'jhi',   #B0
               'bne', 'jcs', 'blo', 'jlo',   #D0
               'beq', 'jeq', 'bhs', 'jhs', ) #F0

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

def parsePass1():
    if op in directives:
        if op == directives['.stack'] or op == directives['.stk']:
            stkSize = eval(str(dt), vlc)    # .stack    size
        elif op == directives['.code'] or op == directives['.cod']:
            if dt != '':
                code = eval(str(dt), vlc)   # .code     [address]
            curSegment = 'code'
        elif op == directives['.data'] or op == directives['.dat']:
            if dt != '':
                data = eval(str(dt), vlc)   # .data     [address]
            curSegment = 'data'
        elif op == directives['.proc'] \
             or op == directives['.sub'] \
             or op == directives['.fnc']:   # .proc
            pass
        elif op == directives['.endp']:     # .endp
            pass
        elif op == directives['.end']:      # .end
            pass
        else:
            print('Error. Unknown directive: line #%d, %s, %s.' \
                  % (srcLine, op, srcLine, directives[op]))
    elif op in defines:
        if op == '.eq' or op == '.equ':
            if curSegment == 'code':
                vlc['_loc_'] = code
            else: vlc['_loc_'] = data
            constants[lbl] = eval(str(dt), vlc)
            vlc[lbl] = constants[lbl] 
        elif op == '.db' or op == '.byt':
            if curSegment == 'code':
                vlc['_loc_'] = code
                vlc[lbl] = code
                siz, val = parseByt(dt, vlc)
                labels[lbl] = code

                cod.append([code, '.byt', 'db', val, \
                            0, siz, '', srcLine, ' ; ' + srcText])
                code += siz
            else:
                vlc['_loc_'] = data
                vlc[lbl] = data
                siz, val = parseByt(dt, vlc)
                variables[lbl] = (data, siz, val)

                dat.append([data, '.byt', 'db', val, \
                            0, siz, '', srcLine, ' ; ' + srcText])
                data += siz
        elif op == '.dw' or op == '.wrd':
            if curSegment == 'code':
                vlc['_loc_'] = code
                vlc[lbl] = code
                siz, val = parseWrd(dt, vlc)
                labels[lbl] = code

                cod.append([code, '.wrd', 'dw', val, \
                            0, siz, '', srcLine, ' ; ' + srcText])
                code += siz
            else:
                vlc['_loc_'] = data
                vlc[lbl] = data
                siz, val = parseWrd(dt, vlc)
                variables[lbl] = (data, siz, val)

                dat.append([data, '.wrd', 'dw', val,
                            0, siz, '', srcLine, ' ; ' + srcText])
                data += siz
        elif op == '.dl' or op == '.lng':
            if curSegment == 'code':
                vlc['_loc_'] = code
                vlc[lbl] = code
                siz, val = parseLng(dt, vlc)
                labels[lbl] = code

                cod.append([code, '.lng', 'dl', val, \
                            0, siz, '', srcLine, ' ; ' + srcText])
                code += siz
            else:
                vlc['_loc_'] = data
                vlc[lbl] = data
                siz, val = parseLng(dt, vlc)
                variables[lbl] = (data, siz, val)

                dat.append([data, '.lng', 'dl', val,
                            0, siz, '', srcLine, ' ; ' + srcText])
                data += siz
        elif op == '.df' or op == '.flt':
            if curSegment == 'code':
                vlc['_loc_'] = code
                vlc[lbl] = code
                siz, val = parseFlt(dt, vlc)
                labels[lbl] = code

                cod.append([code, '.flt', 'df', val, \
                            0, siz, '', srcLine, ' ; ' + srcText])
                code += siz
            else:
                vlc['_loc_'] = data
                vlc[lbl] = data
                siz, val = parseFlt(dt, vlc)
                variables[lbl] = (data, siz, val)

                dat.append([data, '.flt', 'df', val,
                            0, siz, '', srcLine, ' ; ' + srcText])
                data += siz
        elif op == '.ds' or op == '.str':
            if curSegment == 'code':
                vlc['_loc_'] = code
                vlc[lbl] = code
                siz = len(dt); val = str()
                for ch in dt: val += '%02X' % ord(ch)
                labels[lbl] = code
                
                cod.append([code, '.str', 'ds', val,
                            0, siz, '', srcLine, ' ; ' + srcText])
                code += siz
            else:
                vlc['_loc_'] = data
                vlc[lbl] = data
                siz = len(dt); val = str()
                for ch in dt: val += '%02X' % ord(ch)
                variables[lbl] = (data, siz, val)
                
                dat.append([data, '.str', 'ds', val,
                            0, siz, '', srcLine, ' ; ' + srcText])
                data += siz
        else:
            print('Error. Unknown define: %s.' % (op))
            pass
    else:
        if re.match('^\.\w$', op):
            print('Error. Unexpected opcode: %s. Line #%d.' \
                  % (op, srcLine))
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
            elif re.match('^[(]{2}.*,[sS][)]{2},[aA]$', dt):
                addrsMode = 'zpSIIA'
                operand = dt.split(',')[0][2:]
            elif re.match('^\(.*,[xX]\)$', dt):
                operand = dt.split(',')[0][1:]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val >= -128 or val <= 127:
                        addrsMode = 'zpXI'
                    else: addrsMode = 'absXI'
                except:
                    addrsMode = 'absXI'
            elif re.match('^\(.*,[sS]\)$', dt):
                operand = dt.split(',')[0][1:]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val < 256:
                        addrsMode = 'zpSI'
                    else: addrsMode = 'absSI'
                except:
                    addrsMode = 'absSI'
            elif re.match('^\(.*,[aA]\)$', dt):
                operand = dt.split(',')[0][1:]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val < 256:
                        if op == 'jmp':
                            addrsMode = 'absAI'
                        else: addrsMode = 'zpAI'
                    else: addrsMode = 'absAI'
                except:
                    addrsMode = 'absAI'
            elif re.match('^\(.*,[sS]\),[yY]$', dt):
                operand = dt.split(',')[0][1:]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val < 256:
                        addrsMode = 'zpSIY'
                    else: addrsMode = 'absSIY'
                except:
                    addrsMode = 'absSIY'
            elif re.match('^\(.*\),[yY]$', dt):
                operand = dt.split(')')[0][1:]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val < 256:
                        addrsMode = 'zpIY'
                    else: addrsMode = 'absIY'
                except:
                    addrsMode = 'absIY'
            elif re.match('^\(.*,[iI][+]{2}\)$', dt):
                addrsMode = 'ippI'
                operand = dt.split(',')[0][1:]
            elif re.match('^\(.*\)$', dt):
                addrsMode = 'zpI'
                operand = dt.split(')')[0][1:]
            elif re.match('^.*,[xX]$', dt):
                operand = dt.split(',')[0]
                try:
                    val = eval(str(operand), vlc) & 0xFFFF
                    if val >= -128 or val <= 127:
                        addrsMode = 'zpX'
                    else: addrsMode = 'absX'
                except:
                    if op == 'sty':
                        addrsMode = 'zpX'
                    else: addrsMode = 'absX'
            elif re.match('^.*,[yY]$', dt):
                addrsMode = 'absY'
                operand = dt.split(',')[0]
            elif re.match('^.*,[sS]$', dt):
                addrsMode = 'zpS'
                operand = dt.split(',')[0]
            elif re.match('^.*,[iI][+]{2}$', dt):
                addrsMode = 'ipp'
                operand = dt.split(',')[0]
            elif re.match('^.*$', dt):
                if op in relative:
                    addrsMode = 'rel'
                else:
                    try:
                        val = eval(str(dt), vlc)
                        if val < 256:
                            if op in ['jmp', 'jsr']:
                                addrsMode = 'abs'
                            else: addrsMode = 'zp'
                        else: addrsMode = 'abs'
                    except:
                        addrsMode = 'abs'
                    
                operand = dt
                if re.match('^_\w*$', dt):
                    if dt not in library:
                        library.append(dt)
            else:
                addrsMode = 'abs'
                operand = dt

            opcode = op + '_' + addrsMode
            if opcode in opcodes:
                opLen = opcodes[opcode][0]
                dtLen = opcodes[opcode][1]
                opDat = opcodes[opcode][2]
                asmText = '%04X %s%s' % (code, opDat, '00'*dtLen)
                bufLen = 15 - len(asmText)
                cod.append([code, op, addrsMode, operand, \
                            opLen, dtLen, opDat, srcLine, \
                            ' '*bufLen + ' ; ' + srcText])
                code += opLen + dtLen
            else:
                print('Error. Unknown opcode: %s. Line #%d.' \
                      % (opcode, srcLine))

def processLine(line):
    ln, *_ = line[0]
    
    lbl = op = dt = ''
    numFlds = len(line[1])
    
    if numFlds > 2:
        lbl, op, dt, *_ = line[1]
    elif numFlds > 1:
        lbl, op = line[1]
    else: lbl = line[1]

    return ln, lbl, op, dt
        

def pho_ldaImmPha_to_pshImm(source):
    newSrc = []
    length  = len(source) - 1
    i = j = 0

    while i < length:
        newLine = source[i]
        inpLine, lbl, op, dt = processLine(newLine)
        if op in ['lda', 'lda.w'] \
           and dt[0] == '#':
            nxtLine = source[i+1]
            nxtLn, nxtLbl, nxtOp, nxtDt = processLine(nxtLine)
            if nxtOp in ['pha', 'pha.w', 'pha.s', 'pha.sw'] \
               and nxtLbl == '':
                if '.' in nxtOp:
                    op = 'psh'+'.'+nxtOp.split('.')[1]
                else: op = 'psh'
                newLine = [[nxtLn, lbl+'\t'+op+' '+dt], \
                           [lbl, op, dt]]
                i += 1; j += 1
        newSrc.append(newLine)
        i += 1
    newSrc.append(source[i])
    print('ldaImmPha_to_pshImm   =>', j, len(source), len(newSrc))
    return newSrc

def pho_ldaImmSta_to_Stz(source):
    newSrc = []
    length  = len(source) - 1
    i = j = 0

    while i < length:
        newLine = source[i]
        inpLine, lbl, op, dt = processLine(newLine)
        if op in ['lda', 'lda.w'] and dt == '#0':
            nxtLine = source[i+1]
            nxtLn, nxtLbl, nxtOp, nxtDt = processLine(nxtLine)
            if nxtOp in ['sta', 'sta.w'] and nxtLbl == '':
                if '.' in nxtOp:
                    op = 'stz'+'.'+nxtOp.split('.')[1]
                else: op = 'stz'
                newLine = [[nxtLn, lbl+'\t'+op+' '+nxtDt], \
                           [lbl, op, nxtDt]]
                i += 1; j += 1
        newSrc.append(newLine)
        i += 1
    newSrc.append(source[i])        
    print('ldaImmSta_to_Stz      =>', j, len(source), len(newSrc))
    return newSrc

def pho_StackAdd_to_DirectAdd(source):
    newSrc = []
    length  = len(source) - 5
    i = j = 0
    
    nL = [0 for x in range(6)]
    ln = [0 for x in range(6)]
    lb = [0 for x in range(6)]
    op = [0 for x in range(6)]
    dt = [0 for x in range(6)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['lda', 'lda.w']:
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['pha', 'pha.w'] \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['lda', 'lda.w'] \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in ['clc'] \
                       and lb[3] == '':
                        nL[4] = source[i+4]
                        ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        if op[4] in ['adc', 'adc.w'] \
                           and dt[4] == '1,S' \
                           and lb[4] == '':
                            nL[5] = source[i+5]
                            ln[5], lb[5], op[5], dt[5] = processLine(nL[5])
                            if op[5] in ['adj'] \
                               and dt[5] == '#2' \
                               and lb[5] == '':
                                newSrc.append(nL[0])
                                newSrc.append(nL[3])
                                if '.' in op[4]:
                                    op[4] = 'adc'+'.'+op[4].split('.')[1]
                                else: op[4] = 'adc'
                                nL[4] = [[ln[4], lb[4]+'\t'+op[4]+' '+dt[2]], \
                                         [lb[4], op[4], dt[2]]]
                                newSrc.append(nL[4])
                                i += 5; j += 1
                                found = True
        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('StackAdd_to_DirectAdd =>', j, len(source), len(newSrc))
    return newSrc

# def pho_StackSub_to_DirectSub(source):
    # seqLen = 7
    # newSrc = []
    # length  = len(source) - seqLen + 1
    # i = j = 0
    
    # nL = [0 for x in range(seqLen)]
    # ln = [0 for x in range(seqLen)]
    # lb = [0 for x in range(seqLen)]
    # op = [0 for x in range(seqLen)]
    # dt = [0 for x in range(seqLen)]

    # while i < length:
        # found = False
        # nL[0] = source[i]
        # ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        # if op[0] in ['lda', 'lda.w']:
            # nL[1] = source[i+1]
            # ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            # if op[1] in ['pha', 'pha.w'] \
               # and lb[1] == '':
                # nL[2] = source[i+2]
                # ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                # if op[2] in ['lda', 'lda.w'] \
                   # and lb[2] == '':
                    # nL[3] = source[i+3]
                    # ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    # if op[3] in ['clc'] \
                       # and lb[3] == '':
                        # nL[4] = source[i+4]
                        # ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        # if op[4] in ['adc', 'adc.w'] \
                           # and dt[4] == '1,S' \
                           # and lb[4] == '':
                            # nL[5] = source[i+5]
                            # ln[5], lb[5], op[5], dt[5] = processLine(nL[5])
                            # if op[5] in ['adj'] \
                               # and dt[5] == '#2' \
                               # and lb[5] == '':
                                # newSrc.append(nL[0])
                                # newSrc.append(nL[3])
                                # if '.' in op[4]:
                                    # op[4] = 'adc'+'.'+op[4].split('.')[1]
                                # else: op[4] = 'adc'
                                # nL[4] = [[ln[4], lb[4]+'\t'+op[4]+' '+dt[2]], \
                                         # [lb[4], op[4], dt[2]]]
                                # newSrc.append(nL[4])
                                # i += 5; j += 1
                                # found = True
        # if not found: newSrc.append(nL[0])
        # i += 1
        
    # for nL in source[length:]:
        # newSrc.append(nL)

    # print('StackSub_to_DirectSub =>', j, len(source), len(newSrc))
    # return newSrc

def pho_StackCmp_to_DirectCmp(source):
    newSrc = []
    length  = len(source) - 5
    i = j = 0
    
    nL = [0 for x in range(6)]
    ln = [0 for x in range(6)]
    lb = [0 for x in range(6)]
    op = [0 for x in range(6)]
    dt = [0 for x in range(6)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['lda', 'lda.w']:
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['pha', 'pha.w'] \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['lda', 'lda.w'] \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in ['xma', 'xma.w'] \
                       and dt[3] == '1,S' \
                       and lb[3] == '':
                        nL[4] = source[i+4]
                        ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        if op[4] in ['cmp', 'cmp.w'] \
                           and dt[4] == '1,S' \
                           and lb[4] == '':
                            nL[5] = source[i+5]
                            ln[5], lb[5], op[5], dt[5] = processLine(nL[5])
                            if op[5] in ['adj'] \
                               and dt[5] == '#2' \
                               and lb[5] == '':
                                newSrc.append(nL[0])
                                if '.' in op[4]:
                                    op[4] = 'cmp'+'.'+op[4].split('.')[1]
                                else: op[4] = 'cmp'
                                nL[4] = [[ln[4], lb[4]+'\t'+op[4]+' '+dt[2]], \
                                         [lb[4], op[4], dt[2]]]
                                newSrc.append(nL[4])
                                i += 5; j += 1
                                found = True
        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('StackCmp_to_DirectCmp =>', j, len(source), len(newSrc))
    return newSrc

def pho_ConvertAdc_to_Inc(source):
    newSrc = []
    length  = len(source) - 3
    i = j = 0
    
    nL = [0 for x in range(4)]
    ln = [0 for x in range(4)]
    lb = [0 for x in range(4)]
    op = [0 for x in range(4)]
    dt = [0 for x in range(4)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['lda', 'lda.w']:
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['clc'] \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['adc', 'adc.w'] \
                   and dt[2] == '#1' \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in ['sta', 'sta.w'] \
                       and lb[3] == '':
                        if '.' in op[3]:
                            op[3] = 'inc'+'.'+op[3].split('.')[1]
                        else: op[4] = 'inc'
                        nL[3] = [[ln[3], lb[3]+'\t'+op[3]+' '+dt[3]], \
                                 [lb[3], op[3], dt[3]]]
                        newSrc.append(nL[3])
                        i += 3; j += 1
                        found = True
        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('ConvertAdc#1_to_Inc   =>', j, len(source), len(newSrc))
    return newSrc

def pho_optimizeBooleanTest(source, balanced):
    newSrc = []
    length = len(source) - 4
    i = j = 0
    
    nL = [0 for x in range(5)]
    ln = [0 for x in range(5)]
    lb = [0 for x in range(5)]
    op = [0 for x in range(5)]
    dt = [0 for x in range(5)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['php'] \
           and lb[0] == '':
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['lda'] \
               and dt[1] == '#1' \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['plp'] \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in conditional \
                       and lb[3] == '':
                        nL[4] = source[i+4]
                        ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        if op[4] in ['lda'] \
                           and dt[4] == '#0' \
                           and lb[4] == '':
                            if balanced:
                                nL[0] = [[ln[0], '\t'+op[3]+' '+dt[3]+'T'], \
                                         ['', op[3], dt[3]+'T']]
                            else:
                                nL[0] = [[ln[0], '\t'+op[3]+' '+dt[3]+'T'], \
                                         ['', op[3], dt[3]+'-2']]
                            newSrc.append(nL[0])
                            nL[1] = [[ln[1], '\t'+'lda'+' '+'#0'], \
                                     ['', 'lda', '#0']]
                            newSrc.append(nL[1])
                            nL[2] = [[ln[2], '\t'+'bra'+' '+dt[3]], \
                                     ['', 'bra', dt[3]]]
                            newSrc.append(nL[2])
                            if balanced:
                                nL[3] = [[ln[3], dt[3]+'T'+' '+'.byt'+' '+'234[2]'], \
                                         [dt[3]+'T', '.byt', '234[2]']]
                                newSrc.append(nL[3])
                                nL[4] = [[ln[4], '\t'+'lda'+' '+'#1'], \
                                         [lb[4], 'lda', '#1']]
                                newSrc.append(nL[4])
                            else:
                                nL[3] = [[ln[3], dt[3]+'T'], \
                                         [dt[3]+'T', '', '']]
                                newSrc.append(nL[3])
                                nL[4] = [[ln[4], '\t'+'lda'+' '+'#1'], \
                                         [lb[4], 'lda', '#1']]
                                newSrc.append(nL[4])
                            i += 4; j += 1
                            found = True
        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('optimizeBooleanTest   =>', j, len(source), len(newSrc))
    return newSrc

def pho_optimizeBooleanTest2(source):
    newSrc = []
    length = len(source) - 1
    i = j = 0
    
    nL = [0 for x in range(2)]
    ln = [0 for x in range(2)]
    lb = [0 for x in range(2)]
    op = [0 for x in range(2)]
    dt = [0 for x in range(2)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['cmp.w'] \
           and dt[0] == '#1' \
           and lb[0] == '':
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['beq'] \
               and lb[1] == '':
                nL[1] = [[ln[1], '\t'+'bne'+' '+dt[1]], \
                                     ['', 'bne', dt[1]]]
                newSrc.append(nL[1])
                i += 1; j += 1
                found = True
        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('optimizeBooleanTest2  =>', j, len(source), len(newSrc))
    return newSrc

def pho_optimize1DArrayLoad(source):
    newSrc = []
    length = len(source) - 8
    i = j = 0
    
    nL = [0 for x in range(9)]
    ln = [0 for x in range(9)]
    lb = [0 for x in range(9)]
    op = [0 for x in range(9)]
    dt = [0 for x in range(9)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['psh.w'] \
           and dt[0][0] == '#' \
           and lb[0] == '':
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['lda.w', 'lda'] \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['dec.w'] \
                   and dt[2] == 'a' \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in ['asl.w'] \
                       and dt[3] == 'a' \
                       and lb[3] == '':
                        nL[4] = source[i+4]
                        ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        if op[4] in ['clc'] \
                           and lb[4] == '':
                            nL[5] = source[i+5]
                            ln[5], lb[5], op[5], dt[5] = processLine(nL[5])
                            if op[5] in ['adc.w'] \
                               and dt[5] == '1,S' \
                               and lb[5] == '':
                                nL[6] = source[i+6]
                                ln[6], lb[6], op[6], dt[6] = processLine(nL[6])
                                if op[6] in ['sta.w'] \
                                   and dt[6] == '1,S' \
                                   and lb[6] == '':
                                    nL[7] = source[i+7]
                                    ln[7], lb[7], op[7], dt[7] = processLine(nL[7])
                                    if op[7] in ['pli.s'] \
                                       and lb[7] == '':
                                        nL[8] = source[i+8]
                                        ln[8], lb[8], op[8], dt[8] = processLine(nL[8])
                                        if op[8] in ['lda.w'] \
                                           and dt[8] == '0,I++' \
                                           and lb[8] == '':
                                            newSrc.append(source[i+1])
                                            newSrc.append(source[i+2])
                                            newSrc.append(source[i+3])
                                            
                                            nL[4] = [[ln[4], '\t'+'tay.w'+' '+dt[4]], \
                                                     ['', 'tay.w', dt[4]]]
                                            newSrc.append(nL[4])
                                            nL[8] = [[ln[8], '\t'+op[8]+' '+dt[0][1:]+',Y'], \
                                                     [lb[8], op[8], dt[0][1:]+',Y']]
                                            newSrc.append(nL[8])
                                
                                            i += 8; j += 1
                                            found = True
        if not found: newSrc.append(nL[0])
        i += 1

    for nL in source[length:]:
        newSrc.append(nL)

    print('optimize1DArrayLoad   =>', j, len(source), len(newSrc))
    return newSrc

def pho_optimize1DArrayWrite(source):
    newSrc = []
    length = len(source) - 9
    i = j = 0
    
    nL = [0 for x in range(10)]
    ln = [0 for x in range(10)]
    lb = [0 for x in range(10)]
    op = [0 for x in range(10)]
    dt = [0 for x in range(10)]

    while i < length:
        found = False
        nL[0] = source[i]
        ln[0], lb[0], op[0], dt[0] = processLine(nL[0])
        if op[0] in ['psh.w'] \
           and dt[0][0] == '#' \
           and lb[0] == '':
            nL[1] = source[i+1]
            ln[1], lb[1], op[1], dt[1] = processLine(nL[1])
            if op[1] in ['lda.w', 'lda'] \
               and lb[1] == '':
                nL[2] = source[i+2]
                ln[2], lb[2], op[2], dt[2] = processLine(nL[2])
                if op[2] in ['dec.w'] \
                   and dt[2] == 'a' \
                   and lb[2] == '':
                    nL[3] = source[i+3]
                    ln[3], lb[3], op[3], dt[3] = processLine(nL[3])
                    if op[3] in ['asl.w'] \
                       and dt[3] == 'a' \
                       and lb[3] == '':
                        nL[4] = source[i+4]
                        ln[4], lb[4], op[4], dt[4] = processLine(nL[4])
                        if op[4] in ['clc'] \
                           and lb[4] == '':
                            nL[5] = source[i+5]
                            ln[5], lb[5], op[5], dt[5] = processLine(nL[5])
                            if op[5] in ['adc.w'] \
                               and dt[5] == '1,S' \
                               and lb[5] == '':
                                nL[6] = source[i+6]
                                ln[6], lb[6], op[6], dt[6] = processLine(nL[6])
                                if op[6] in ['sta.w'] \
                                   and dt[6] == '1,S' \
                                   and lb[6] == '':
                                    # ignore line 7 - should load value to write to 1D array
                                    nL[7] = source[i+7]

                                    nL[8] = source[i+8]
                                    ln[8], lb[8], op[8], dt[8] = processLine(nL[8])
                                    if op[8] in ['pli.s'] \
                                       and lb[8] == '':
                                        nL[9] = source[i+9]
                                        ln[9], lb[9], op[9], dt[9] = processLine(nL[9])
                                        if op[9] in ['sta.w'] \
                                           and dt[9] == '0,I++' \
                                           and lb[9] == '':
                                            newSrc.append(source[i+1])
                                            newSrc.append(source[i+2])
                                            newSrc.append(source[i+3])
                                            
                                            nL[4] = [[ln[4], '\t'+'tay.w'+' '+dt[4]], \
                                                     ['', 'tay.w', dt[4]]]
                                            newSrc.append(nL[4])
                                            newSrc.append(source[i+7])
                                            nL[9] = [[ln[9], '\t'+op[9]+' '+dt[0][1:]+',Y'], \
                                                     [lb[9], op[9], dt[0][1:]+',Y']]
                                            newSrc.append(nL[9])
                                
                                            i += 9; j += 1
                                            found = True
        if not found: newSrc.append(nL[0])
        i += 1

    for nL in source[length:]:
        newSrc.append(nL)

    print('optimize1DArrayWrite  =>', j, len(source), len(newSrc))
    return newSrc

def pho_ReduceConstantQuotient(source):
    newSrc = []
    length  = len(source) - 3
    i = j = 0
    
    nL = [0 for x in range(4)]
    ln = [0 for x in range(4)]
    lb = [0 for x in range(4)]
    op = [0 for x in range(4)]
    dt = [0 for x in range(4)]

    while i < length:
        found = False
        for k in range(4):
            nL[k] = source[i+k]
            ln[k], lb[k], op[k], dt[k] = processLine(nL[k])
        if op[0] in ['psh.w'] \
           and dt[0][0] == '#' \
           and op[1] in ['psh.w'] \
           and dt[1][0] == '#' \
           and op[2] in ['jsr'] \
           and dt[2] in ['_idiv']:
            dividend = int(dt[0][1:])
            divisor  = int(dt[1][1:])
            quotient = int(dividend / divisor)
            dt[3] = '#'+str("%d" % (quotient))
            op[3] = 'lda.w'
            nL[3] = [[ln[3], lb[3]+'\t'+op[3]+' '+dt[3]], \
                     [lb[3], op[3], dt[3]]]
            newSrc.append(nL[3])
            i += 3; j += 1
            found = True

        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('ReduceConstantQuotient=>', j, len(source), len(newSrc))
    return newSrc

def pho_ReduceVarImmProduct(source):
    newSrc = []
    length  = len(source) - 4
    i = j = 0
    
    nL = [0 for x in range(5)]
    ln = [0 for x in range(5)]
    lb = [0 for x in range(5)]
    op = [0 for x in range(5)]
    dt = [0 for x in range(5)]

    while i < length:
        found = False
        for k in range(5):
            nL[k] = source[i+k]
            ln[k], lb[k], op[k], dt[k] = processLine(nL[k])
        if op[1] in ['pha.w'] \
           and op[2] in ['psh.w'] \
           and dt[2][0] == '#' \
           and op[3] in ['jsr'] \
           and dt[3] in ['_imul']:
            newSrc.append(nL[0])
            multiplier  = int(dt[2][1:])
            if multiplier == 2:
                dt[4] = 'a'
                op[4] = 'asl.w'
                nL[4] = [[ln[4], lb[4]+'\t'+op[4]+' '+dt[4]], \
                         [lb[4], op[4], dt[4]]]
                newSrc.append(nL[4])
                i += 4; j += 1
                found = True

        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('reduceVarImmProduct   =>', j, len(source), len(newSrc))
    return newSrc

def pho_ReduceImmVarProduct(source):
    newSrc = []
    length  = len(source) - 4
    i = j = 0
    
    nL = [0 for x in range(5)]
    ln = [0 for x in range(5)]
    lb = [0 for x in range(5)]
    op = [0 for x in range(5)]
    dt = [0 for x in range(5)]

    while i < length:
        found = False
        for k in range(5):
            nL[k] = source[i+k]
            ln[k], lb[k], op[k], dt[k] = processLine(nL[k])
        if op[0] in ['psh.w'] \
           and dt[0][0] == '#' \
           and op[2] in ['pha.w'] \
           and op[3] in ['jsr'] \
           and dt[3] in ['_imul']:
            newSrc.append(nL[1])
            multiplier  = int(dt[0][1:])
            if multiplier == 2:
                dt[4] = 'a'
                op[4] = 'asl.w'
                nL[4] = [[ln[4], lb[4]+'\t'+op[4]+' '+dt[4]], \
                         [lb[4], op[4], dt[4]]]
                newSrc.append(nL[4])
                i += 4; j += 1
                found = True

        if not found: newSrc.append(nL[0])
        i += 1
        
    for nL in source[length:]:
        newSrc.append(nL)

    print('reduceImmVarProduct   =>', j, len(source), len(newSrc))
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


