import re
import os
import array

from PyAsm65Utilities import *

directives = {'.stack' : '.stack', \
              '.stk'   : '.stk', \
              '.code'  : '.code', \
              '.cod'   : '.cod', \
              '.data'  : '.data', \
              '.dat'   : '.dat', \
              '.proc'  : '.proc', \
              '.sub'   : '.sub', \
              '.fnc'   : '.fnc', \
              '.endp'  : '.endp', \
              '.end'   : '.end', }

defines    = ('.eq', '.equ', \
              '.db', '.byt', \
              '.dw', '.wrd', \
              '.dl', '.lng', '.flt', \
              '.ds', '.str', )

relative   = ('bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq', \
              'bra', \
              'bge', 'bgt', 'ble', 'blt', 'bhs', 'bhi', 'bls', 'blo', \
              'jge', 'jgt', 'jle', 'jlt', 'jhs', 'jhi', 'jls', 'jlo', \
              'jra', \
              'phr', 'csr', )

opcodes = dict()

opcodes = loadOpcodeTable(opcodes,genOpcodeLst=True) # Load default opcode table

filename = input('Enter base name of file to process: ')
libpath  = input('Enter path to library: ')

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

source = pho_ldaImmPha_to_pshImm(source)

'''
    Output intermediate file #2
'''

with open(filename+'.p02', 'wt') as fout:
    for ln in source:
        inpLine = ln[0][0]
        srcText = ln[0][1]
        print('%4d' % (inpLine), srcText, file=fout)

'''
    Assembler Pass 1
'''

print('\tPass 1')

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
        print('Error. Unexpected number of fields: %d' % (numFields) \
              + ' in line #%d' % (srcLine))
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
                print('Error. Unknown directive: line #%d, %s, %s.' \
                      % (srcLine, op, srcLine, directives[op]))
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
                elif re.match('^[(]{2}.*,[sS][)]{2},[aA]$', dt):
                    addrsMode = 'zpSIIA'
                    operand = dt.split(',')[0][2:]
                elif re.match('^\w*$', dt):
                    if op in relative:
                        addrsMode = 'rel'
                    else:
                        addrsMode = 'abs'
                        
                    operand = dt
                    if re.match('^_\w*$', dt):
                        if dt not in library:
                            library.append(dt)
                else:
                    addrsMode = 'abs'
                    operand = dt
#                    print('Error. Unknown addressing mode: %s. Line #%d.' \
#                          % (dt, srcLine))

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
                print('Error. Unknown directive: line #%d, %s, %s.' \
                      % (srcLine, op, srcLine, directives[op]))
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
                    dat.append([data, lbl, 'db', dt, siz, 0, val, srcLine, \
                                ' '*bufLen + ' ; ' + srcText])
                    data += siz
                elif op == '.dw' or op == '.wrd':
                    siz = 2*int(dt)
                    val = '00'*siz
                    variables[lbl] = (data, siz, val)

                    asmText = '%04X %s' % (data, val[:8])
                    bufLen = 15 - len(asmText)
                    dat.append([data, lbl, 'db', dt, siz, 0, val, srcLine, \
                                ' '*bufLen + ' ; ' + srcText])
                    data += siz
                elif op == '.dl' or op == '.lng' or op == '.flt':
                    siz = 4
                    val = '00'*siz
                    variables[lbl] = (data, siz, val)

                    asmText = '%04X %s' % (data, val[:8])
                    bufLen = 15 - len(asmText)
                    dat.append([data, lbl, 'db', dt, siz, 0, val, srcLine, \
                                ' '*bufLen + ' ; ' + srcText])
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
                    dat.append([data, lbl, 'ds', dt, siz, 0, strVal, srcLine, \
                                ' '*bufLen + ' ; ' + srcText])
                    data += siz
                else:
                    print('Error. Unknown define: %s.' % (op))
                    pass
            else:
                if dt == '':
                    addrsMode = 'imp'
                    operand = ''
                elif re.match('^[aAxXyY]{1}$', dt):
                    addrsMode = dt.lower()
                    operand = dt.lower()
                elif re.match('^#', dt):
                    addrsMode = 'imm'
                    operand = dt[1:]
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
                elif re.match('^[(]{2}.*,[sS][)]{2},[aA]$', dt):
                    addrsMode = 'zpSIIA'
                    operand = dt.split(',')[0][2:]
                elif re.match('^\w*$', dt):
                    if op in relative:
                        addrsMode = 'rel'
                    else:
                        addrsMode = 'abs'
                    operand = dt
                    if re.match('^_\w*$', dt):
                        if dt not in library:
                            library.append(dt)
                else:
                    addrsMode = 'abs'
                    operand = dt
#                    print('Error. Unknown addressing mode: %s. Line #%d.' \
#                          % (dt, srcLine))

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
    line += 1

'''
    Insert Loop(s) to add library functions
'''

## TODO: Recursively read and append runtime library to end of code space

'''
    Merge cod[] and dat[]; adjust address of each entry.
'''

for ln in dat:
    data, lbl, op, dt, siz, zerVal, val, srcLine, srcText = ln
    cod.append([code + data, lbl, op, dt, siz, zerVal, val, srcLine, srcText])

'''
    Adjust addresses of variables{}
'''

for key in variables.keys():
    addr, siz, dt = variables[key]
    variables[key] = (code + addr, siz, dt)

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

print('-'*80)
print
for key in vlc:
    print('%-18s : %s' % (key, vlc[key]))
print
print('-'*80)

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
            print('\tError: eval(%s) failed' % dt)
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
        if dt in labels:
            try:
                val = eval(str(dt), vlc)
                delta = val - (addrs + opLen + dtLen)
            except:
                print('\tError: eval(%s) failed' % dt)
                delta = 65536
            if dtLen == 1:
                if delta < -128 or delta > 127:
                    print('Error. Target address out of range.')
                else:
                    loStr = '%02X' % (delta & 255)
                    out[addrs] = [opLen + dtLen, \
                                  ''.join([opStr, loStr]), \
                                  srcTxt, srcLine]
            elif dtLen == 2:
                if delta < -32768 or delta > 32767:
                    print('Error. Target address out of range.')
                else:
                    loStr = '%02X' % (delta & 255)
                    hiStr = '%02X' % ((delta >> 8) & 255)
                    out[addrs] = [opLen + dtLen, \
                                  ''.join([opStr, loStr, hiStr]), \
                                  srcTxt, srcLine]
        else:
            print('\tError. Destination not found in symbol table.')
    elif md in ['zpS', 'zpSI', 'zpSIY', 'zpX', 'zpXI', 'ipp', 'ippI',]:
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError: eval(%s) failed' % dt)
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
            print('Error. Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
    elif md in ['abs', 'absI', 'absX', 'absXI', 'absY', 'absIY',]:
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError: eval(%s) failed' % dt)
            val = -1
        
        if dtLen == 1:
            loStr = '%02X' % (-1 & 255)
            hiStr = '%02X' % (-1 & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
            print('Error. Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), \
                          srcTxt, srcLine]
    elif md in ['zpSIIA',]:
        try:
            val = eval(str(dt), vlc)
        except:
            print('\tError: eval(%s) failed' % dt)
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
            print('Error. Invalid Operand Length: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))
    elif md in ('db', 'byt', 'ds', 'str'):
        val, siz, strVal = variables[op]
        out[addrs] = [siz, opStr, srcTxt, srcLine]

'''
    Print results of Pass 2
'''

pgm = array.array('B', [])

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
        print('(%4d) %04X' % (srcLine, i), outTxt[:8], srcTxt, file=fout)
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
    Write Binary Progam Image
'''

with open(filename+'.bin', 'wb') as fout:
    fout.write(bytes(pgm))
    
'''
    Generate Print File -- Interleave Input File and Output File
'''

srcLine = 0
with open(filename+'.lst', 'rt') as lst:
    with open(filename+'.asm', 'rt') as asm:
        with open(filename+'.prn', 'wt') as prn:
            asmInp = asm.readline(); srcLine += 1
            lstInp = lst.readline()
            while True:
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
                asmInp = asm.readline(); srcLine += 1
                if asmInp == '': break
