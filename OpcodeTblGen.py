'''
    Opcode Table Generator

        This program generates the OpcodeTbl.txt file needed by the Simple
        M65C02A Assembler. The input to the program is a file the provides
        the base opcode, base addressing mode, and the allowed prefix
        instructions. Opcodes are "decorated" by .w, .x, or .xw to signify
        the size of the operation, the stack pointer to be used for stack
        operations, or both: pha, pla, phx, plx, phy, ply, phs, pls, psh,
        pul, phr, jsr, csr, rts, rti, phi, pli, phw, plw, and ent.

        The source white space delimited source file for the Opcode Table
        Generator has the following format:

        code  opcode  Mode osx ind siz isz osz ois oax oay
'''

import re
import os

lines = []
with open('OpcodeTblGen.txt', 'rt') as finp:
    lines = finp.readlines()
lines = lines[1:] # Delete header line


flds = []
for ln in lines:
    fld = ln.split()
    flds.append(tuple(fld))
        

prefix = {'osx' : '8B', \
          'ind' : '9B', \
          'siz' : 'AB', \
          'isz' : 'BB', \
          'osz' : 'CB', \
          'ois' : 'DB', \
          'oax' : 'EB', \
          'oay' : 'FB' }

oneByte = ('imm',  \
           'rel',  \
           'zp',   \
           'zpX',  \
           'zpY',  \
           'zpI',  \
           'zpXI', \
           'zpIY', \
           'ipp' )

twoByte = ('abs',   \
           'absX',  \
           'absY',  \
           'absI',  \
           'absXI', \
           'rel16', \
           'zprel' )

relMap = {'bra_relI'   : ('jra_rel16', 'rel16', 2, 2, '9B80'), \
          'bpl_relI'   : ('jpl_rel16', 'rel16', 2, 2, '9B10'), \
          'bmi_relI'   : ('jmi_rel16', 'rel16', 2, 2, '9B30'), \
          'bvc_relI'   : ('jvc_rel16', 'rel16', 2, 2, '9B50'), \
          'bvs_relI'   : ('jvs_rel16', 'rel16', 2, 2, '9B70'), \
          'bcc_relI'   : ('jcc_rel16', 'rel16', 2, 2, '9B90'), \
          'bcs_relI'   : ('jcs_rel16', 'rel16', 2, 2, '9BB0'), \
          'bne_relI'   : ('jne_rel16', 'rel16', 2, 2, '9BD0'), \
          'beq_relI'   : ('jeq_rel16', 'rel16', 2, 2, '9BF0'), \
          'bpl.w_rel'  : ('bgt_rel',   'rel',   2, 1, 'AB10'), \
          'bmi.w_rel'  : ('ble_rel',   'rel',   2, 1, 'AB30'), \
          'bvc.w_rel'  : ('bge_rel',   'rel',   2, 1, 'AB50'), \
          'bvs.w_rel'  : ('blt_rel',   'rel',   2, 1, 'AB70'), \
          'bcc.w_rel'  : ('bls_rel',   'rel',   2, 1, 'AB90'), \
          'bcs.w_rel'  : ('bhi_rel',   'rel',   2, 1, 'ABB0'), \
          'bne.w_rel'  : ('blo_rel',   'rel',   2, 1, 'ABD0'), \
          'beq.w_rel'  : ('bhs_rel',   'rel',   2, 1, 'ABF0'), \
          'bpl.w_relI' : ('jgt_rel16', 'rel16', 2, 2, 'BB10'), \
          'bmi.w_relI' : ('jle_rel16', 'rel16', 2, 2, 'BB30'), \
          'bvc.w_relI' : ('jge_rel16', 'rel16', 2, 2, 'BB50'), \
          'bvs.w_relI' : ('jlt_rel16', 'rel16', 2, 2, 'BB70'), \
          'bcc.w_relI' : ('jls_rel16', 'rel16', 2, 2, 'BB90'), \
          'bcs.w_relI' : ('jhi_rel16', 'rel16', 2, 2, 'BBB0'), \
          'bne.w_relI' : ('jlo_rel16', 'rel16', 2, 2, 'BBD0'), \
          'beq.w_relI' : ('jhs_rel16', 'rel16', 2, 2, 'BBF0') }

accMap = {'asl_acc'    : ('asl_a',   'a',   1, 0, '0A'), \
          'asl.x_acc'  : ('asl_x',   'x',   2, 0, 'EB0A'), \
          'asl.y_acc'  : ('asl_y',   'y',   2, 0, 'FB0A'), \
          'inc_acc'    : ('inc_a',   'a',   1, 0, '1A'), \
          'rol_acc'    : ('rol_a',   'a',   1, 0, '2A'), \
          'rol.x_acc'  : ('rol_x',   'x',   2, 0, 'EB2A'), \
          'rol.y_acc'  : ('rol_y',   'y',   2, 0, 'FB2A'), \
          'dec_acc'    : ('dec_a',   'a',   1, 0, '3A'), \
          'lsr_acc'    : ('lsr_a',   'a',   1, 0, '4A'), \
          'lsr.x_acc'  : ('lsr_x',   'x',   2, 0, 'EB4A'), \
          'lsr.y_acc'  : ('lsr_y',   'y',   2, 0, 'FB4A'), \
          'ror_acc'    : ('ror_a',   'a',   1, 0, '6A'), \
          'ror.x_acc'  : ('ror_x',   'x',   2, 0, 'EB6A'), \
          'ror.y_acc'  : ('ror_y',   'y',   2, 0, 'FB6A'), \
          'dup_acc'    : ('dup_a',   'a',   1, 0, '0B'), \
          'dup.x_acc'  : ('dup_x',   'x',   2, 0, 'EB0B'), \
          'dup.y_acc'  : ('dup_y',   'y',   2, 0, 'FB0B'), \
          'swp_acc'    : ('swp_a',   'a',   1, 0, '1B'), \
          'swp.x_acc'  : ('swp_x',   'x',   2, 0, 'EB1B'), \
          'swp.y_acc'  : ('swp_y',   'y',   2, 0, 'FB1B'), \
          'rot_acc'    : ('rot_a',   'a',   1, 0, '2B'), \
          'rot.x_acc'  : ('rot_x',   'x',   2, 0, 'EB2B'), \
          'rot.y_acc'  : ('rot_y',   'y',   2, 0, 'FB2B'), \
          'lsr_accI'   : ('asr_a',   'a',   2, 0, '9B4A'), \
          'lsr.x_accI' : ('asr_x',   'y',   3, 0, 'EB9B4A'), \
          'lsr.y_accI' : ('asr_y',   'y',   3, 0, 'FB9B4A'), \
          'dup_accI'   : ('tai_imp', 'imp', 2, 0, '9B0B'), \
          'swp_accI'   : ('bsw_a',   'a',   2, 0, '9B1B'), \
          'rot_accI'   : ('rev_a',   'a',   2, 0, '9B2B'), \
          'asl.w_acc'  : ('asl.w_a', 'a',   2, 0, 'AB0A'), \
          'asl.wx_acc' : ('asl.w_x', 'x',   3, 0, 'EBAB0A'), \
          'asl.wy_acc' : ('asl.w_y', 'y',   3, 0, 'FBAB0A'), \
          'inc.w_acc'  : ('inc.w_a', 'a',   2, 0, 'AB1A'), \
          'rol.w_acc'  : ('rol.w_a', 'a',   2, 0, 'AB2A'), \
          'rol.wx_acc' : ('rol.w_x', 'x',   3, 0, 'EBAB2A'), \
          'rol.wy_acc' : ('rol.w_y', 'y',   3, 0, 'FBAB2A'), \
          'dec.w_acc'  : ('dec.w_a', 'a',   2, 0, 'AB3A'), \
          'lsr.w_acc'  : ('lsr.w_a', 'a',   2, 0, 'AB4A'), \
          'lsr.wx_acc' : ('lsr.w_x', 'x',   3, 0, 'EBAB4A'), \
          'lsr.wy_acc' : ('lsr.w_y', 'y',   3, 0, 'FBAB4A'), \
          'ror.w_acc'  : ('ror.w_a', 'a',   2, 0, 'AB6A'), \
          'ror.wx_acc' : ('ror.w_x', 'x',   3, 0, 'EBAB6A'), \
          'ror.wy_acc' : ('ror.w_y', 'y',   3, 0, 'FBAB6A'), \
          'dup.w_acc'  : ('tia_imp', 'imp', 2, 0, 'AB0B'), \
          'lsr.w_accI' : ('asr.w_a', 'a',   2, 0, 'BB4A'),\
          'lsr.wx_accI': ('asr.w_x', 'x',   3, 0, 'EBBB4A'),\
          'lsr.wy_accI': ('asr.w_y', 'y',   3, 0, 'FBBB4A'),\
          'dup.w_accI' : ('xai_imp', 'imp', 2, 0, 'BB0B') }
          

'''
    Create M65C02A base Opcode Table
'''

fout = open('OpcodeTbl.txt', 'wt')
opcodeList = []; opcodeDict = {}
for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()

    dtLen = int()
    if mode in ('imp', 'acc'):
        dtLen = 0
    elif mode in oneByte:
        dtLen = 1
    elif mode in twoByte:
        dtLen = 2
    else:
        continue

    opcode = '_'.join([opcode, mode]); opLen = 1
    if opcode in accMap:
        opcode, mode, opLen, dtLen, code = accMap[opcode]

    print(opcode, 0, opLen, dtLen, code, mode)
    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
    opcodeList.append(opcode)
    opcodeDict[opcode] = [opLen, dtLen, code, mode]

'''
    Add instructions using IND prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    ind = ind.lower()

    if ind == 'y':
        dtLen = int()
        if mode in ('imp', 'acc'):
            dtLen = 0
        elif mode in oneByte:
            dtLen = 1
        elif mode in twoByte:
            dtLen = 2
        else:
            continue

        if mode in ('imp', 'acc', 'imm', 'rel', 'rel16', 'zprel'):
            if mode == 'zprel':
                mode = 'zpIrel'
                code = ''.join([prefix['ind'], code]); opLen = 2
                opcode = '_'.join([opcode, mode])
                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'rel16':
                code = ''.join([prefix['ind'], code]); opLen = 2
                opcode = '_'.join(['csr', mode])
                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'rel':
                code = ''.join([prefix['ind'], code]); opLen = 2
                mode = mode + 'I'
                opcode = '_'.join([opcode, mode])
                if opcode in relMap:
                    opcode, mode, opLen, dtLen, code = relMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'acc':
                code = ''.join([prefix['ind'], code]); opLen = 2
                mode = mode + 'I'
                opcode = '_'.join([opcode, mode])
                if opcode in accMap:
                    opcode, mode, opLen, dtLen, code = accMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            else:
                pass
        elif mode in ('zpY', 'zpIY', 'absY'):
            if mode == 'zpY':
                mode = 'zpIY'
            elif mode == 'zpIY':
                mode = 'zpIIY'
            else:
                mode = 'absIY'
            code = ''.join([prefix['ind'], code])
            opcode = '_'.join([opcode, mode])
            if opcode in opcodeDict:
                pass
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [2, dtLen, code, mode]
                print(opcode, 0, 2, dtLen, code, mode)
                print(opcode, 0, 2, dtLen, code, mode, file=fout)
        else:
            mode = mode + 'I'
            code = ''.join([prefix['ind'], code])
            opcode = '_'.join([opcode, mode])
            if opcode in opcodeDict:
                pass
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [2, dtLen, code, mode]
                print(opcode, 0, 2, dtLen, code, mode)
                print(opcode, 0, 2, dtLen, code, mode, file=fout)

'''
    Add instructions using SIZ prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    siz = siz.lower()

    if siz == 'y':
        dtLen = int()
        if mode in ('imp', 'acc'):
            dtLen = 0
        elif mode in oneByte:
            dtLen = 1
        elif mode in twoByte:
            dtLen = 2
        else:
            continue

        if mode in ('imp', 'acc', 'imm', 'rel'):
            if mode == 'rel':
                code = ''.join([prefix['siz'], code]); opLen = 2
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in relMap:
                    opcode, mode, opLen, dtLen, code = relMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'imm':
                code = ''.join([prefix['siz'], code]); opLen = 2
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                dtLen += 1
                
                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'acc':
                code = ''.join([prefix['siz'], code]); opLen = 2
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in accMap:
                    opcode, mode, opLen, dtLen, code = accMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            else:
                code = ''.join([prefix['siz'], code]); opLen = 2
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                dtLen += 1

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            code = ''.join([prefix['siz'], code]); opLen = 2
            opcode = '_'.join([''.join([opcode, '.w']), mode])

            if opcode in opcodeDict:
                pass
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)

'''
    Add instructions using ISZ prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    isz = siz.lower()

    if isz == 'y':
        dtLen = int()
        if mode in ('imp', 'acc'):
            dtLen = 0
        elif mode in oneByte:
            dtLen = 1
        elif mode in twoByte:
            dtLen = 2
        else:
            print('Error. Unrecognized Addressing Mode: %s, %s.' \
                  % (opcode, mode))

        if mode in ('imp', 'acc', 'imm', 'rel'):
            if mode == 'rel':
                code = ''.join([prefix['isz'], code]); opLen = 2
                mode = mode + 'I'
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in relMap:
                    opcode, mode, opLen, dtLen, code = relMap[opcode]
                else:
                    continue
                
                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            elif mode == 'acc':
                code = ''.join([prefix['isz'], code]); opLen = 2
                mode = mode + 'I'
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in accMap:
                    opcode, mode, opLen, dtLen, code = accMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    pass
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opLen, dtLen, code, mode]
                    print(opcode, 0, opLen, dtLen, code, mode)
                    print(opcode, 0, opLen, dtLen, code, mode, file=fout)
            else:
                pass
        elif mode in ('zpY', 'zpIY', 'absY'):
            if mode == 'zpY':
                mode = 'zpIY'
            elif mode == 'zpIY':
                mode = 'zpIIY'
            else:
                mode = 'absIY'
            code = ''.join([prefix['isz'], code]); opLen = 2
            opcode = '_'.join([''.join([opcode, '.w']), mode])

            if opcode in opcodeDict:
                pass
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            code = ''.join([prefix['isz'], code]); opLen = 2
            mode = mode + 'I'
            opcode = '_'.join([''.join([opcode, '.w']), mode])

            if opcode in opcodeDict:
                pass
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)

fout.close()

