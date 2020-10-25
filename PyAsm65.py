import re
import os
import array

from PyAsm65Utilities import *

opcodes = loadOpcodeTable(genOpcodeLst=True)    # Load default opcode table

filename  = input('Enter base name of file to process: ')
libpath   = input('Enter path to library: ')
enablePho = input('Enable Peephole Optimization: ')
if enablePho == '':
    phoEnable = False
else: phoEnable = True

labels    = {}
constants = {}
variables = {}
library   = []

line    = 0     # line number 
code    = 0     # code space position
data    = 0     # data space position
stkSize = 0 

cod = []        # instructions
dat = []        # data

inpLine = 1
srcLine = 1
source  = []    # fields in the input line

'''
    Output intermediate file #1
'''

with open(filename+'.p01', 'wt') as fout:
    for ln in readSource(filename):
        inpLine = ln[0][0]
        srcText = ln[0][1]
        print('%4d' % (inpLine), srcText, file=fout)
        source.append(ln)

'''
    Insert Peephole Optimizations here
'''

if phoEnable:
    source = pho_ldaImmPha_to_pshImm(source)
    source = pho_ldaImmSta_to_Stz(source)
    source = pho_StackAdd_to_DirectAdd(source)
    source = pho_StackCmp_to_DirectCmp(source)
    source = pho_optimizeBooleanTest(source, False)
    source = pho_ConvertAdc_to_Inc(source)

'''
    Output intermediate file #2
'''

with open(filename+'.p02', 'wt') as fout:
    i = 0
    for ln in source:
        inpLine = ln[0][0]
        srcText = ln[0][1]
        print('[%4d]' % (i), '%4d' % (inpLine), srcText, file=fout)
        i += 1

'''
    Assembler Pass 1
'''

print('\tPass 1')

vlc = {}
curSegment = 'code'

for src in source:
    srcLine, srcText = src[0]
    opcode = ''
    numFields = len(src[1])
    if numFields == 1:
        lbl = src[1][0]
        op  = ''
        dt  = ''
    elif numFields == 2:
        lbl = src[1][0]
        op  = src[1][1].lower()
        dt  = ''
    elif numFields == 3:
        lbl = src[1][0]
        op  = src[1][1].lower()
        dt  = src[1][2]
    else:
        lbl = src[1][0]
        op  = src[1][1].lower()
        dt  = str()
        for i in src[1][2:]:
            dt += i

    vlc['_loc_'] = code
    
    if lbl == '':
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
    else:
        if lbl in labels or lbl in constants or lbl in variables:
            print('Error: Redefinition of %s in %d' % (lbl, srcLine))
        else:
            if curSegment == 'code':
                labels[lbl] = code; vlc[lbl] = labels[lbl]
            else: labels[lbl] = data; vlc[lbl] = labels[lbl]

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
                    if '$' in dt:
                        dt = '_loc_'.join(dt.split('$'))
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
                        dt = dt[1:-1]
                        siz = len(dt); val = str()
                        for ch in dt: val += '%02X' % ord(ch)
                        labels[lbl] = code

                        cod.append([code, '.str', 'ds', val,
                                    0, siz, '', srcLine, ' ; ' + srcText])
                        code += siz
                    else:
                        vlc['_loc_'] = data
                        vlc[lbl] = data
                        dt = dt[1:-1]
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
                    if opcode != '_imp':
                        print('Error. Unknown opcode: %s. Line #%d.' \
                              % (opcode, srcLine))
    line += 1

'''
    Insert Loop(s) to add library functions
'''

# TODO: Recursively read and append runtime library to end of code space

'''
    Merge cod[] and dat[]; adjust address of each entry.
'''

for ln in dat:
    addrs, op, md, operand, opLen, dtLen, opStr, srcText, srcLine = ln
    cod.append([code + addrs, op, md, operand,
                opLen, dtLen, opStr, srcText, srcLine])
    #if addrs < code:
        #cod.append([code + addrs, op, md, operand,
                    #opLen, dtLen, opStr, srcText, srcLine])
    #else:
        #cod.append([addrs, op, md, operand,
                    #opLen, dtLen, opStr, srcText, srcLine])

'''
    Adjust addresses of variables{}
'''

for key in variables.keys():
    addrs, siz, dt = variables[key]
    variables[key] = (code + addrs, siz, dt)
    #if addrs < code:
        #variables[key] = (code + addrs, siz, dt)
    #else: variables[key] = (addrs, siz, dt)

'''
    Create a common dictionary for variables, labels, and constants that will be
    used by the eval() to resolve operand expressions during Pass 2.
'''

vlc = {}
vlc.update(labels)
vlc.update(constants)
for var in variables:
    value, *_ = variables[var]
    vlc[var] = value

# print('-'*80)
# print
# for key in vlc:
    # print('%-18s : %s' % (key, vlc[key]))
# print
# print('-'*80)

# print('-'*80)
# print
# for key in constants:
    # print('%-18s : %8s (0x%04X)' % (key, constants[key], constants[key]))
# print
# print('-'*80)

'''
    Assembler Pass 2
'''

print('\tPass 2')

out = {}
for ln in cod:
    addrs = ln[0]
    op = ln[1]
    md = ln[2]
    dt = ln[3]
    opLen = ln[4]
    dtLen = ln[5]
    opStr = ln[6]
    srcLine = ln[7]
    srcTxt  = ln[8]

    if md == 'imp' or md == 'a' or md == 'x' or md == 'y':
        out[addrs] = [opLen, opStr, srcTxt, srcLine]
    elif md == 'imm':
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError(imm): eval(%s) failed' % dt)
            val = -1

        if dtLen == 1:
            loStr = '%02X' % (val & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), \
                          srcTxt, srcLine]
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
    elif md == 'rel':
        try:
            val = eval(str(dt), vlc)
            delta = val - (addrs + opLen + dtLen)
        except:
            print('\tError(rel): eval(%s) failed' % dt)
            delta = 65536
        if dtLen == 1:
            if delta < -128 or delta > 127:
                print('Error(rel8). Target address out of range.')
            else:
                loStr = '%02X' % (delta & 255)
                out[addrs] = [opLen + dtLen, \
                              ''.join([opStr, loStr]), \
                              srcTxt, srcLine]
        elif dtLen == 2:
            if delta < -32768 or delta > 32767:
                print('Error(rel16). Target address out of range.')
            else:
                loStr = '%02X' % (delta & 255)
                hiStr = '%02X' % ((delta >> 8) & 255)
                out[addrs] = [opLen + dtLen, \
                              ''.join([opStr, loStr, hiStr]), \
                              srcTxt, srcLine]
    elif md in ['zp',    'zpI',    'zpII',
                'zpX',   'zpXI',   'zpXII',
                'zpY',   'zpIY',   'zpIIY',
                'ipp',   'ippI',
                'zpS',   'zpSI',   'zpSIY', 'zpSIIY', 
                'zpA',   'zpAI',   'zpAII', 'zpIIA',
                'zpSIA', 'zpSIIA', ]:
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError(zp): eval(%s) failed' % dt)
            print('\t\t', hex(addrs), op, md, dt, opLen, dtLen, srcLine, srcTxt)
            val = -1

        if dtLen == 1:
            loStr = '%02X' % (val & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), \
                          srcTxt, srcLine]
        else:
            loStr = '%02X' % (-1 & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), \
                          srcTxt, srcLine]
            print('Error(zp). Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
    elif md in ['abs',    'absI',
                'absX',   'absXI', 'absXII',
                'absY',   'absIY', 
                'absS',   'absSI', 'absSIY', 'absSII',
                'absA',   'absAI', 'absAII', 'absIA', 
                'absSIA', ]:
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError(abs): eval(%s) failed' % dt)
            val = -1
        
        if dtLen == 1:
            loStr = '%02X' % (-1 & 255)
            hiStr = '%02X' % (-1 & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
            print('Error(abs). Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
    elif md in ['zprel', 'zpIrel', 'zpSrel',   'zpSIrel', ]:
        flds = dt.split(',')
        try:
            zpAddr = eval(str(flds[0]), vlc)
        except:
            print('\tError(zprel): zpAddr eval(%s) failed' % flds[0])
            zpAddr = -1 & 255

        try:
            relOff = eval(str(flds[1]), vlc)
        except:
            print('\tError(zprel): relOff eval(%s) failed' % flds[1])
            relOff = 0
        
        if dtLen == 1:
            loStr = '%02X' % (-1 & 255)
            hiStr = '%02X' % (-1 & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
            print('Error(abs). Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
        else:
            loStr = '%02X' % (zpAddr & 255)
            hiStr = '%02X' % (relOff & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
    elif md in ('db', 'dw', 'dl', 'df', 'dd', 'ds', ):
        vlc['_loc_'] = addrs
        if md == 'db':
            siz, outStr = evalByt(dt, vlc)
            if siz == dtLen:
                out[addrs] = [siz, outStr, srcTxt, srcLine]
            else: print('=== Error(evalByt) ==>', 
                        'returned siz does not match dtLen')
        elif md == 'dw':
            siz, outStr = evalWrd(dt, vlc)
            if siz == dtLen:
                out[addrs] = [siz, outStr, srcTxt, srcLine]
            else: print('=== Error(evalWrd) ==>', 
                        'returned siz does not match dtLen')
        elif md == 'dl':
            siz, outStr = evalLng(dt, vlc)
            if siz == dtLen:
                out[addrs] = [siz, outStr, srcTxt, srcLine]
            else: print('=== Error(evalLng) ==>',
                        'returned siz does not match dtLen')
        elif md == 'ds':
            siz = dtLen; outStr = dt
            out[addrs] = [siz, outStr, srcTxt, srcLine]

'''
    Print results of Pass 2
'''

pgm = array.array('B', [])

print("Writing Listing File.")

with open(filename+'.lst', 'wt') as fout:
    start = False
    prevAddrs = 0
    currAddrs = 0
    for i in out:
        if start:
            currAddrs = prevAddrs + prevLen
            if i != currAddrs:
                print('\tMissing conversion(s): 0x%04X-0x%04X' \
                      % (prevAddrs + prevLen, i - 1), file=fout)
                start = False
            else:
                prevAddrs = i
                prevLen = out[i][0]
        else:
            prevAddrs = i
            prevLen = out[i][0]
            start = True
        length, outTxt, srcTxt, srcLine = tuple(out[i])
        for j in range(length):
            beg = 2 * j; end = beg + 2
            try:
                binVal = int(outTxt[beg:end], 16)
            except:
                print('\tError: %s' % outTxt[beg:end], 'Line: %d' % srcLine)
                binVal = 255
            pgm.append(binVal)

        srcTxt = srcTxt.lstrip()
        if len(outTxt[:8]) <= 8: bufLen = (8 - len(outTxt[:8])) + 3
        else: bufLen = 0
        print('(%4d) %04X' % (srcLine, i),
              outTxt[:8], ' '*bufLen+srcTxt, file=fout)
        if len(outTxt) > 8:
            outTxt = outTxt[8:]
            addrs = i + 4
            while True:
                print(' '*6, '%04X' % (addrs), outTxt[:64], file=fout)
                if len(outTxt) > 64:
                    outTxt = outTxt[64:]
                else:
                    break
                addrs += 32

'''
    Write Binary Program Image
'''

print("Writing Binary Program Image")

with open(filename+'.bin', 'wb') as fout:
    fout.write(bytes(pgm))
    
'''
    Generate Print File -- Interleave Input File and Output File
'''

print("Writing Print File")

srcLine = 0
with open(filename+'.lst', 'rt') as lst:
    with open(filename+'.asm', 'rt') as asm:
        with open(filename+'.prn', 'wt') as prn:
            asmInp = asm.readline(); srcLine += 1
            lstInp = lst.readline()
            while lstInp != '' and asmInp != '':
                if lstInp[0:1] == '(':
                    lstLine = lstInp.split(';')
                    lstFlds = lstLine[0].split(')')
                    inpLine = int(lstFlds[0][1:])
                    if inpLine == srcLine:
                        print(lstInp[:-1], file=prn)
                        lstInp = lst.readline()
                        if lstInp == '':
                            lstInp = '(0)\n'
                            break
                    else:
                        print('(%4d)' % (srcLine), ' '*16,
                              ';', asmInp[:-1], file=prn)
                else:
                    while True:
                        print(lstInp[:-1], file=prn)
                        lstInp = lst.readline()
                        if lstInp[0:1] == '(':
                            lstLine = lstInp.split(';')
                            lstFlds = lstLine[0].split(')')
                            inpLine = int(lstFlds[0][1:])
                            if inpLine == srcLine:
                                print(lstInp[:-1], file=prn)
                                lstInp = lst.readline()
                                if lstInp == '': lstInp = '(0)\n'
                            else:
                                print('(%4d)' % (srcLine), ' '*16,
                                      ';', asmInp[:-1], file=prn)
                            break
                        elif lstInp == '':
                            print('(%4d)' % (srcLine), ' '*16,
                                  ';', asmInp[:-1], file=prn)
                            break
                asmInp = asm.readline(); srcLine += 1
            while asmInp != '':
                print('(%4d)' % (srcLine), ' '*16, ';', asmInp[:-1], file=prn)
                asmInp = asm.readline(); srcLine += 1
