import re
import os

with open('D:\\Git-Repo\\Mak-Pascal\\PC65\\test\\Sieve.asm', 'rt') as finp:
    lines = finp.readlines()

'''
    Read Opcodes Table
'''

with open('D:\\Git-Repo\\Mak-Pascal\\PC65\\utils\\OpcodeTbl.dat', 'rt') as finp:
    opcodeTbl = finp.readlines()

'''
    Create Opcodes Dictionary
'''

opcodes = dict()
maxWidth = 0
for opcode in opcodeTbl:
    op = opcode.split()
    key = op[0]
    opcodes[key] = [int(op[2]), int(op[3]), op[4]]
    if len(key) > maxWidth:
        maxWidth = len(key)

##'''
##    Print Opcodes Table
##'''
##
##print('-'*80)
##print('\tOpcode Table')
##print('-'*80)
##print()
##for key in opcodes:
##    print('%-*s' % (maxWidth, key),':',opcodes[key])
##print()
##print('-'*80)
##print()

'''
    Strip comments, blank lines, etc.
'''

inLine = 0; srcLine = 0; source = []
with open('D:\\Git-Repo\\Mak-Pascal\\PC65\\test\\Sieve.p01', 'wt') as fout:
    for line in lines:
        m = re.split('\s*;[\s\w]*', line)
        src = m[0].rstrip()
        if src == '' or src == '\n':
            pass
        else:
            source.append([srcLine, inLine, src])
            #print('%4d %4d' % (srcLine, inLine), src, file=fout)
            srcLine += 1
        inLine += 1

'''
    Split source lines
'''

fields = []
for src in source:
    if '"' in src[2]:
        line = src[2].split('"')
        flds = re.split('\s', line[0])[:2]
        flds.append(line[1])
    else:
        flds = re.split('[ \t][\s]*', src[2])
    fields.append([[src[:2]], flds])
    #print('[%4d, %4d]' % (src[0], src[1]), flds)

directives = ('.stack', '.code', '.data', '.proc', '.endp', '.end')
defines = ('.eq', '.db', '.dw', '.dl', '.ds')
relative = ('bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq', 'bra', \
            'bge', 'bgt', 'ble', 'blt', 'bhs', 'bhi', 'bls', 'blo', \
            'jge', 'jgt', 'jle', 'jlt', 'jhs', 'jhi', 'jls', 'jlo', 'jra', \
            'phr', 'csr')

'''
    Assembler Pass 1
'''

labels = {}; constants = {}; variables = {}; library = []

line = 0
code = 0
data = 0
stkSize = 0

mem = []

for field in fields:
    srcLine = source[line][1]
    srcText = source[line][2]
    opcode = ''
    numFields = len(field[1])
    if numFields == 1:
        lbl = field[1][0]
        op  = ''
        dt  = ''
    elif numFields == 2:
        lbl = field[1][0]
        op  = field[1][1].lower()
        dt  = ''
    elif numFields == 3:
        lbl = field[1][0]
        op  = field[1][1].lower()
        dt  = field[1][2]
    else:
        print('Error. Unexpected number of fields: %d' % (numFields) \
              + ' in line #%d' % (srcLine))
    if lbl == '':
        if op in directives:
            if op == directives[0]:
                stkSize = int(dt)
            elif op == directives[1]:
                if dt != '':
                    code = int(dt)
            elif op == directives[2]:
                if dt != '':
                    data = int(dt)
                else:
                    data = code
                # Process list of library calls whenever code generation turns
                # to generating variable definitions
            elif op == directives[3]:
                pass
            elif op == directives[4]:
                pass
            elif op == directives[5]:
                pass
            else:
                print('Error. Unknown directive: %s. Line #%d.' % (op, srcLine))
            print(' '*16,';',srcText)
        else:
            if re.match('^\.\w$', op):
                print('Error. Unexpected opcode: %s. Line #%d.' % (op, srcLine))
            else:
                if dt == '':
                    addrsMode = 'imp'
                    operand = ''
                elif re.match('^[aAxXyY]$', dt):
                    addrsMode = dt
                    operand = dt
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
                elif re.match('^.*,[bB]', dt):
                    addrsMode = 'bp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[bB]\)$', dt):
                    addrsMode = 'bpI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[sS]$', dt):
                    addrsMode = 'sp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[sS]\)$', dt):
                    addrsMode = 'spI'
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
                    asmText = '%04x: %s%s' % (code, opDat, '00'*dtLen)
                    bufLen = 15 - len(asmText)
                    print(asmText, ' '*bufLen, ';', srcText)
                    mem.append([code, op, addrsMode, operand, \
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
            if op == directives[0]:
                stkSize = int(dt)
            elif op == directives[1]:
                if dt != '':
                    code = int(dt)
            elif op == directives[2]:
                if dt != '':
                    data = int(dt)
                else:
                    data = code
                # Process list of library calls whenever code generation turns
                # to generating variable definitions
            elif op == directives[3]:
                pass
            elif op == directives[4]:
                pass
            elif op == directives[5]:
                pass
            else:
                print('Error. Unknown directive: %s. Line #%d.' % (op, srcLine))
            print(' '*16,';',srcText)
        else:
            if op == '':
                labels[lbl] = code
                print(' '*16,';',srcText)
            elif op in defines:
                if op == '.eq':
                    constants[lbl] = int(dt)
                    print(' '*16,';',srcText)
                elif op == '.db':
                    siz = int(dt)
                    val = '00'*siz
                    variables[lbl] = (data, siz, val)

                    asmText = '%04x: %s' % (data, val[:8])
                    bufLen = 15 - len(asmText)
                    print(asmText, ' '*bufLen, ';', srcText)
                    mem.append([data, lbl, 'db', dt, siz, 0, val, \
                                ' '*bufLen+' ; '+srcText])

                    data += siz
                elif op == '.ds':
                    siz = len(dt)
                    variables[lbl] = (data, siz, val)
                    strVal = []

                    for ch in dt:
                        strVal.append('%02x' % (ord(ch)))
                    strVal = ''.join(strVal)

                    asmText = '%04x: %s' % (data, strVal[:8])
                    bufLen = 15 - len(asmText)
                    print(asmText, ' '*bufLen, ';', srcText)
                    mem.append([data, lbl, 'ds', dt, siz, 0, strVal, \
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
                    addrsMode = dt
                    operand = dt
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
                elif re.match('^.*,[bB]', dt):
                    addrsMode = 'bp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[bB]\)$', dt):
                    addrsMode = 'bpI'
                    operand = dt.split(',')[0][1:]
                elif re.match('^.*,[sS]$', dt):
                    addrsMode = 'sp'
                    operand = dt.split(',')[0]
                elif re.match('^\(.*,[sS]\)$', dt):
                    addrsMode = 'spI'
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
                    asmText = '%04x: %s%s' % (code, opDat, '00'*dtLen)
                    bufLen = 15 - len(asmText)
                    print(asmText, ' '*bufLen, ';', srcText)
                    mem.append([code, op, addrsMode, operand, \
                                opLen, dtLen, opDat, ' '*bufLen+' ; '+srcText])
                    code += opLen + dtLen
                else:
                    print('Error. Unknown opcode: %s. Line #%d.' \
                          % (opcode, srcLine))
    line += 1

'''
    Assembler Pass 2
'''

out = {}
for ln in mem:
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
        if dt.isnumeric():
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
        else:
            if dt in constants:
                val = constants[dt]
            elif dt in labels:
                val = labels[dt]
            elif dt in variables:
                val, siz, strVal = variables[dt]
            else:
                print('Error. Expected number, constant, variable, or label.')
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
    elif md in ('sp', 'spI', 'spIY', 'bp', 'bpI'):
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
            print('Error. Missing constant or number: 0x%04X, %s' \
                  % (addrs, dt))
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

start = False
prevAddrs = 0
currAddrs = 0
for i in out:
    if start:
        currAddrs = prevAddrs + prevLen
        if i != currAddrs:
            print('\tMissing conversion(s): 0x%04x-0x%04x' \
                  % (prevAddrs + prevLen, i - 1))
            start = False
        else:
            prevAddrs = i
            prevLen = out[i][0]
    else:
        prevAddrs = i
        prevLen = out[i][0]
        start = True
    length, outTxt, srcTxt = tuple(out[i])
    print('%04X' % (i), outTxt[:8], srcTxt)
    if len(outTxt) > 8:
        outTxt = outTxt[8:]
        addrs = i + 4
        while True:
            print('%04X' % (addrs), outTxt[:64])
            if len(outTxt) > 64:
                outTxt = outTxt[64:]
            else:
                break
            addrs += 32


