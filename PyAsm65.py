import re
import os

from PyAsm65Utilities import *

directives = ('.stack', '.code', '.data', '.proc', '.endp', '.end')
defines    = ('.eq', '.db', '.dw', '.dl', '.ds')
relative   = ('bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq', \
              'bra', \
              'bge', 'bgt', 'ble', 'blt', 'bhs', 'bhi', 'bls', 'blo', \
              'jge', 'jgt', 'jle', 'jlt', 'jhs', 'jhi', 'jls', 'jlo', \
              'jra', \
              'phr', 'csr')

opcodes = dict()

loadOpcodeTable(opcodes) # Load default opcode table

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

fout = open(filename+'.p01', 'wt')

for ln in readSource(filename):
    srcLine = ln[0][0]
    inpLine = ln[0][1]
    srcText = ln[0][2]
    print('%4d %4d' % (srcLine, inpLine), srcText, file=fout)
    source.append(ln)

fout.close()

'''
    Insert Peephole Optimizations here
'''

source = pho_ldaImmPha_to_pshImm(source)

'''
    Assembler Pass 1
'''

for src in source:
    *_, srcLine, srcText = src[0]
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
            if op == directives[0]:     # .stack    size
                stkSize = numVal(dt)
            elif op == directives[1]:   # .code     [address]
                if dt != '':
                    code = numVal(dt)
            elif op == directives[2]:   # .data     [address]
                if dt != '':
                    data = numVal(dt)
            elif op == directives[3]:   # .proc
                pass
            elif op == directives[4]:   # .endp
                pass
            elif op == directives[5]:   # .end
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
                    addrsMode = 'spIY'
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
                    cod.append([code, op, addrsMode, operand, \
                                opLen, dtLen, opDat, ' '*bufLen+' ; '+srcText])
                    code += opLen + dtLen
                else:
                    print('Error. Unknown opcode: %s. Line #%d.' \
                          % (opcode, srcLine))
    else:
        if lbl in labels or lbl in constants or lbl in variables:
            print('Error: Redefinition of %s in %d' % (lbl, srcLine))
        elif op in directives:
            labels[lbl] = code
            if op == directives[0]:     # .stack    size
                stkSize = numVal(dt)
            elif op == directives[1]:   # .code     [address]
                if dt != '':
                    code = numVal(dt)
            elif op == directives[2]:   # .data     [address]
                if dt != '':
                    data = numVal(dt)
            elif op == directives[3]:   # .proc
                pass
            elif op == directives[4]:   # .endp
                pass
            elif op == directives[5]:   # .end
                pass
            else:
                print('Error. Unknown directive: %s. Line #%d.' % (op, srcLine))
        else:
            if op == '':
                labels[lbl] = code
            elif op in defines:
                if op == '.eq':
                    constants[lbl] = numVal(dt)
                elif op == '.db':
                    siz = int(dt)
                    val = '00'*siz
                    variables[lbl] = (data, siz, val)

                    asmText = '%04X %s' % (data, val[:8])
                    bufLen = 15 - len(asmText)
                    dat.append([data, lbl, 'db', dt, siz, 0, val, \
                                ' '*bufLen+' ; '+srcText])
                    data += siz
                elif op == '.ds':
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
                    addrsMode = 'spIY'
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
                    cod.append([code, op, addrsMode, operand, \
                                opLen, dtLen, opDat, ' '*bufLen+' ; '+srcText])
                    code += opLen + dtLen
                else:
                    print('Error. Unknown opcode: %s. Line #%d.' \
                          % (opcode, srcLine))
    line += 1

'''
    Insert Loop(s) to add library functions
'''



'''
    Merge cod[] and dat[]; adjust address of each entry.
'''

for ln in dat:
    data, lbl, op, dt, siz, zerVal, val, srcText = ln
    cod.append([code + data, lbl, op, dt, siz, zerVal, val, srcText])

'''
    Adjust addresses of variables{}
'''

for key in variables.keys():
    addr, siz, dt = variables[key]
    variables[key] = (code + addr, siz, dt)

'''
    Assembler Pass 2
'''

out = {}
for ln in cod:
    addrs = ln[0]
    op = ln[1]
    md = ln[2]
    dt = ln[3]
    opLen = ln[4]
    dtLen = ln[5]
    opStr = ln[6]
    srcTxt = ln[7]

    if md == 'imp' or md == 'a' or md == 'x' or md == 'y':
        out[addrs] = [opLen, opStr, srcTxt]
    elif md == 'imm':
        val = 0
        if '_' in dt:
            if dt in constants:
                val = constants[dt]
            elif dt in labels:
                val = labels[dt]
            elif dt in variables:
                val, siz, strVal = variables[dt]
            else:
                print('Error. Expected number, constant, variable, or label:', \
                      '%s %s %s' %(op, md, dt))
        else:
            val = numVal(dt)

        if dtLen == 1:
            loStr = '%02X' % (val & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), srcTxt]
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), srcTxt]
    elif md == 'rel':
        if dt in labels:
            delta = labels[dt] - (addrs + opLen + dtLen)
            if dtLen == 1:
                if delta < -128 or delta > 127:
                    print('Error. Target address out of range.')
                else:
                    loStr = '%02X' % (delta & 255)
                    out[addrs] = [opLen + dtLen, \
                                  ''.join([opStr, loStr]), srcTxt]
            elif dtLen == 2:
                if delta < -32768 or delta > 32767:
                    print('Error. Target address out of range.')
                else:
                    loStr = '%02X' % (delta & 255)
                    hiStr = '%02X' % ((delta >> 8) & 255)
                    out[addrs] = [opLen + dtLen, \
                                  ''.join([opStr, loStr, hiStr]), srcTxt]
        else:
            print('Error. Destination not found in symbol table.')
    elif md == 'abs':
        if dt in constants or dt in labels or dt in variables:
            if dt in constants:
                val = constants[dt]
            elif dt in labels:
                val = labels[dt]
            else:
                val, siz, strVal = variables[dt]
        else:
            val = -1
            print('\tMissing symbol: 0x%04X, %s' % (addrs, dt))
        if dtLen == 1:
            loStr = '%02X' % (val & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), srcTxt]
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), srcTxt]
    elif md in ('zpS', 'zpSI', 'spIY', 'zpX', 'zpXI'):
        if dt in constants:
            val = constants[dt]
        elif dt.isnumeric():
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
                    print('Error. Unknown numeric representation: 0x%04X, %s' \
                          % (addrs, dt))
            else:
                val = int(dt)
        else:
            val = -1
            print('Error. Missing constant or number: 0x%04X, %s %s %s' \
                  % (addrs, op, md, dt))

        if dtLen == 1:
            loStr = '%02X' % (val & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr]), srcTxt]
        else:
            loStr = '%02X' % (val & 255)
            hiStr = '%02X' % ((val >> 8) & 255)
            out[addrs] = [opLen + dtLen, \
                          ''.join([opStr, loStr, hiStr]), srcTxt]
    elif md in ('db', 'ds'):
        val, siz, strVal = variables[op]
        out[addrs] = [siz, opStr, srcTxt]

'''
    Print results of Pass 2
'''

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
        length, outTxt, srcTxt = tuple(out[i])
        print('%04X' % (i), outTxt[:8], srcTxt, file=fout)
        if len(outTxt) > 8:
            outTxt = outTxt[8:]
            addrs = i + 4
            while True:
                print('%04X' % (addrs), outTxt[:64], file=fout)
                if len(outTxt) > 64:
                    outTxt = outTxt[64:]
                else:
                    break
                addrs += 32


