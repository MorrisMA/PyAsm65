'''
    Opcode Table Generator

        This program generates the OpcodeTbl.txt file needed by the Simple
        M65C02A Assembler. The input to the program is a file the provides
        the base opcode, base addressing mode, and the allowed prefix
        instructions. Opcodes are "decorated" by .w, .x, or .xw to signify
        the size of the operation, the stack pointer to be used for stack
        operations, or both: pha, pla, phx, plx, phy, ply, phs, pls, psh,
        pul, phr, jsr, csr, rts, rti, phi, pli, phw, plw, and ent.

        The white space delimited source file for the Opcode Table Generator
        has the following format:

        code  opcode  Mode ind siz isz osx osz ois oax oay
'''

import re
import os

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

relMap = {'bra_relI'    : ('jra_rel16',   'rel16', 2, 2, '9B80'), \
          'bpl_relI'    : ('jpl_rel16',   'rel16', 2, 2, '9B10'), \
          'bmi_relI'    : ('jmi_rel16',   'rel16', 2, 2, '9B30'), \
          'bvc_relI'    : ('jvc_rel16',   'rel16', 2, 2, '9B50'), \
          'bvs_relI'    : ('jvs_rel16',   'rel16', 2, 2, '9B70'), \
          'bcc_relI'    : ('jcc_rel16',   'rel16', 2, 2, '9B90'), \
          'bcs_relI'    : ('jcs_rel16',   'rel16', 2, 2, '9BB0'), \
          'bne_relI'    : ('jne_rel16',   'rel16', 2, 2, '9BD0'), \
          'beq_relI'    : ('jeq_rel16',   'rel16', 2, 2, '9BF0'), \
          'bpl.w_rel'   : ('bgt_rel',     'rel',   2, 1, 'AB10'), \
          'bmi.w_rel'   : ('ble_rel',     'rel',   2, 1, 'AB30'), \
          'bvc.w_rel'   : ('bge_rel',     'rel',   2, 1, 'AB50'), \
          'bvs.w_rel'   : ('blt_rel',     'rel',   2, 1, 'AB70'), \
          'bcc.w_rel'   : ('bls_rel',     'rel',   2, 1, 'AB90'), \
          'bcs.w_rel'   : ('bhi_rel',     'rel',   2, 1, 'ABB0'), \
          'bne.w_rel'   : ('blo_rel',     'rel',   2, 1, 'ABD0'), \
          'beq.w_rel'   : ('bhs_rel',     'rel',   2, 1, 'ABF0'), \
          'bpl.w_relI'  : ('jgt_rel16',   'rel16', 2, 2, 'BB10'), \
          'bmi.w_relI'  : ('jle_rel16',   'rel16', 2, 2, 'BB30'), \
          'bvc.w_relI'  : ('jge_rel16',   'rel16', 2, 2, 'BB50'), \
          'bvs.w_relI'  : ('jlt_rel16',   'rel16', 2, 2, 'BB70'), \
          'bcc.w_relI'  : ('jls_rel16',   'rel16', 2, 2, 'BB90'), \
          'bcs.w_relI'  : ('jhi_rel16',   'rel16', 2, 2, 'BBB0'), \
          'bne.w_relI'  : ('jlo_rel16',   'rel16', 2, 2, 'BBD0'), \
          'beq.w_relI'  : ('jhs_rel16',   'rel16', 2, 2, 'BBF0') }

accMap = {'asl_acc'     : ('asl_a',       'a',     1, 0, '0A'), \
          'asl.x_acc'   : ('asl_x',       'x',     2, 0, 'EB0A'), \
          'asl.y_acc'   : ('asl_y',       'y',     2, 0, 'FB0A'), \
          'inc_acc'     : ('inc_a',       'a',     1, 0, '1A'), \
          'rol_acc'     : ('rol_a',       'a',     1, 0, '2A'), \
          'rol.x_acc'   : ('rol_x',       'x',     2, 0, 'EB2A'), \
          'rol.y_acc'   : ('rol_y',       'y',     2, 0, 'FB2A'), \
          'dec_acc'     : ('dec_a',       'a',     1, 0, '3A'), \
          'lsr_acc'     : ('lsr_a',       'a',     1, 0, '4A'), \
          'lsr.x_acc'   : ('lsr_x',       'x',     2, 0, 'EB4A'), \
          'lsr.y_acc'   : ('lsr_y',       'y',     2, 0, 'FB4A'), \
          'ror_acc'     : ('ror_a',       'a',     1, 0, '6A'), \
          'ror.x_acc'   : ('ror_x',       'x',     2, 0, 'EB6A'), \
          'ror.y_acc'   : ('ror_y',       'y',     2, 0, 'FB6A'), \
          'dup_acc'     : ('dup_a',       'a',     1, 0, '0B'), \
          'dup.x_acc'   : ('dup_x',       'x',     2, 0, 'EB0B'), \
          'dup.y_acc'   : ('dup_y',       'y',     2, 0, 'FB0B'), \
          'swp_acc'     : ('swp_a',       'a',     1, 0, '1B'), \
          'swp.x_acc'   : ('swp_x',       'x',     2, 0, 'EB1B'), \
          'swp.y_acc'   : ('swp_y',       'y',     2, 0, 'FB1B'), \
          'rot_acc'     : ('rot_a',       'a',     1, 0, '2B'), \
          'rot.x_acc'   : ('rot_x',       'x',     2, 0, 'EB2B'), \
          'rot.y_acc'   : ('rot_y',       'y',     2, 0, 'FB2B'), \
          'lsr_accI'    : ('asr_a',       'a',     2, 0, '9B4A'), \
          'lsr.x_accI'  : ('asr_x',       'y',     3, 0, 'EB9B4A'), \
          'lsr.y_accI'  : ('asr_y',       'y',     3, 0, 'FB9B4A'), \
          'dup_accI'    : ('tai_imp',     'imp',   2, 0, '9B0B'), \
          'swp_accI'    : ('bsw_a',       'a',     2, 0, '9B1B'), \
          'rot_accI'    : ('rev_a',       'a',     2, 0, '9B2B'), \
          'asl.w_acc'   : ('asl.w_a',     'a',     2, 0, 'AB0A'), \
          'asl.wx_acc'  : ('asl.w_x',     'x',     3, 0, 'EBAB0A'), \
          'asl.wy_acc'  : ('asl.w_y',     'y',     3, 0, 'FBAB0A'), \
          'inc.w_acc'   : ('inc.w_a',     'a',     2, 0, 'AB1A'), \
          'rol.w_acc'   : ('rol.w_a',     'a',     2, 0, 'AB2A'), \
          'rol.wx_acc'  : ('rol.w_x',     'x',     3, 0, 'EBAB2A'), \
          'rol.wy_acc'  : ('rol.w_y',     'y',     3, 0, 'FBAB2A'), \
          'dec.w_acc'   : ('dec.w_a',     'a',     2, 0, 'AB3A'), \
          'lsr.w_acc'   : ('lsr.w_a',     'a',     2, 0, 'AB4A'), \
          'lsr.wx_acc'  : ('lsr.w_x',     'x',     3, 0, 'EBAB4A'), \
          'lsr.wy_acc'  : ('lsr.w_y',     'y',     3, 0, 'FBAB4A'), \
          'ror.w_acc'   : ('ror.w_a',     'a',     2, 0, 'AB6A'), \
          'ror.wx_acc'  : ('ror.w_x',     'x',     3, 0, 'EBAB6A'), \
          'ror.wy_acc'  : ('ror.w_y',     'y',     3, 0, 'FBAB6A'), \
          'dup.w_acc'   : ('tia_imp',     'imp',   2, 0, 'AB0B'), \
          'lsr.w_accI'  : ('asr.w_a',     'a',     2, 0, 'BB4A'),\
          'lsr.wx_accI' : ('asr.w_x',     'x',     3, 0, 'EBBB4A'),\
          'lsr.wy_accI' : ('asr.w_y',     'y',     3, 0, 'FBBB4A'),\
          'dup.w_accI'  : ('xai_imp',     'imp',   2, 0, 'BB0B') }

osxMap = {'jsr.s_abs'   : ('jsr.s_abs',   'abs',   2, 2, '8B20'), \
          'jsr.s_absI'  : ('jsr.s_absI',  'absI',  2, 2, 'DB20'), \
          'rti.s_imp'   : ('rti.s',       'imp',   2, 0, '8B40'), \
          'rts.s_imp'   : ('rts.s',       'imp',   2, 0, '8B60'), \
          'adj.s_imm'   : ('adj.s_imm',   'imm',   2, 1, '8BC2'), \
          'adj.sw_imm'  : ('adj.sw_imm',  'imm',   2, 2, 'CBC2'), \
          'psh.s_imm'   : ('psh.s_imm',   'imm',   2, 1, '8BE2'), \
          'psh.s_zp'    : ('psh.s_zp',    'zp',    2, 0, '8BD4'), \
          'psh.sw_zp'   : ('psh.sw_zp',   'zp',    2, 1, 'CBD4'), \
          'psh.sw_zpI'  : ('psh.sw_zpI',  'zpI',   2, 1, 'DBD4'), \
          'pul.s_zp'    : ('pul.s_zp',    'zp',    2, 0, '8BF4'), \
          'pul.sw_zp'   : ('pul.sw_zp',   'zp',    2, 1, 'CBF4'), \
          'pul.sw_zpI'  : ('pul.sw_zpI',  'zpI',   2, 1, 'DBF4'), \
          'php.s_imp'   : ('php.s_imp',   'imp',   2, 0, '8B08'), \
          'plp.s_imp'   : ('plp.s_imp',   'imp',   2, 0, '8B28'), \
          'pha.s_imp'   : ('pha.s_imp',   'imp',   2, 0, '8B48'), \
          'pha.sw_imp'  : ('pha.sw_imp',  'imp',   2, 0, 'CB48'), \
          'pla.s_imp'   : ('pla.s_imp',   'imp',   2, 0, '8B68'), \
          'pla.sw_imp'  : ('pla.sw_imp',  'imp',   2, 0, 'CB68'), \
          'phx.s_imp'   : ('phx.s_imp',   'imp',   2, 0, '8BDA'), \
          'phx.sw_imp'  : ('phx.sw_imp',  'imp',   2, 0, 'CBDA'), \
          'plx.s_imp'   : ('plx.s_imp',   'imp',   2, 0, '8BFA'), \
          'plx.sw_imp'  : ('plx.sw_imp',  'imp',   2, 0, 'CBFA'), \
          'phy.s_imp'   : ('phy.s_imp',   'imp',   2, 0, '8B5A'), \
          'phy.sw_imp'  : ('phy.sw_imp',  'imp',   2, 0, 'CB5A'), \
          'ply.s_imp'   : ('ply.s_imp',   'imp',   2, 0, '8B7A'), \
          'ply.sw_imp'  : ('ply.sw_imp',  'imp',   2, 0, 'CB7A'), \
          'nxt.s_imp'   : ('nxt.s_imp',   'imp',   2, 0, '8B3B'), \
          'nxt.s_impI'  : ('inxt.s_imp',  'imp',   2, 0, 'DB3B'), \
          'phi.s_imp'   : ('phi.s_imp',   'imp',   2, 0, '8B4B'), \
          'phi.s_impI'  : ('phw.s_imp',   'imp',   2, 0, 'DB4B'), \
          'pli.s_imp'   : ('pli.s_imp',   'imp',   2, 0, '8B6B'), \
          'pli.s_impI'  : ('plw.s_imp',   'imp',   2, 0, 'DB6B'), \
          'ent.s_imp'   : ('ent.s_imp',   'imp',   2, 0, '8B7B'), \
          'ent.s_impI'  : ('ient.s_imp',  'imp',   2, 0, 'DB7B'), \
          'ldx.s_imm'   : ('lds_imm',     'imm',   2, 1, '8BA2'), \
          'ldx.sw_imm'  : ('lds.w_imm',   'imm',   2, 2, 'CBA2'), \
          'ldx.s_zp'    : ('lds_zp',      'zp',    2, 1, '8BA6'), \
          'ldx.s_zpI'   : ('lds_zpI',     'zpI',   3, 1, '8B9BA6'), \
          'ldx.sw_zp'   : ('lds.w_zp',    'zp',    2, 1, 'CBA6'), \
          'ldx.sw_zpI'  : ('lds.w_zpI',   'zpI',   2, 1, 'DBA6'), \
          'ldx.s_zpY'   : ('lds_zpY',     'zpY',   2, 1, '8BB6'), \
          'ldx.s_zpIY'  : ('lds_zpIY',    'zpIY',  3, 1, '8B9BB6'), \
          'ldx.sw_zpY'  : ('lds.w_zpY',   'zpY',   2, 1, 'CBB6'), \
          'ldx.sw_zpIY' : ('lds.w_zpIY',  'zpIY',  2, 1, 'DBB6'), \
          'ldx.s_abs'   : ('lds_abs',     'abs',   2, 2, '8BAE'), \
          'ldx.s_absI'  : ('lds_absI',    'absI',  3, 2, '8B9BAE'), \
          'ldx.sw_abs'  : ('lds.w_abs',   'abs',   2, 2, 'CBAE'), \
          'ldx.sw_absI' : ('lds.w_absI',  'absI',  2, 2, 'DBAE'), \
          'ldx.s_absY'  : ('lds_absY',    'absY',  2, 2, '8BBE'), \
          'ldx.s_absIY' : ('lds_absIY',   'absIY', 3, 2, '8B9BBE'), \
          'ldx.sw_absY' : ('lds.w_absY',  'absY',  2, 2, 'CBBE'), \
          'ldx.sw_absIY': ('lds.w_absIY', 'absIY', 2, 2, 'DBBE'), \
          'stx.s_zp'    : ('sts_zp',      'zp',    2, 1, '8B86'), \
          'stx.s_zpI'   : ('sts_zpI',     'zpI',   3, 1, '8B9B86'), \
          'stx.sw_zp'   : ('sts.w_zp',    'zp',    2, 1, 'CB86'), \
          'stx.sw_zpI'  : ('sts.w_zpI',   'zpI',   2, 1, 'DB86'), \
          'stx.s_zpY'   : ('sts_zpY',     'zpY',   2, 1, '8B96'), \
          'stx.s_zpIY'  : ('sts_zpIY',    'zpIY',  3, 1, '8B9B96'), \
          'stx.sw_zpY'  : ('sts.w_zpY',   'zpY',   2, 1, 'CB96'), \
          'stx.sw_zpIY' : ('sts.w_zpIY',  'zpIY',  2, 1, 'DB96'), \
          'stx.s_abs'   : ('sts_abs',     'abs',   2, 2, '8B8E'), \
          'stx.s_absI'  : ('sts_absI',    'absI',  3, 2, '8B9B8E'), \
          'stx.sw_abs'  : ('sts.w_abs',   'abs',   2, 2, 'CB8E'), \
          'stx.sw_absI' : ('sts.w_absI',  'absI',  2, 2, 'DB8E'), \
          'cpx.s_imm'   : ('cps_imm',     'imm',   2, 1, '8BE0'), \
          'cpx.sw_imm'  : ('cps.w_imm',   'imm',   2, 2, 'DBE0'), \
          'cpx.s_zp'    : ('cps_zp',      'zp',    2, 1, '8BE4'), \
          'cpx.sw_zp'   : ('cps.w_zp',    'zp',    2, 1, 'CBE4'), \
          'cpx.s_zpI'   : ('cps_zpI',     'zpI',   3, 1, '8B9BE4'), \
          'cpx.sw_zpI'  : ('cps.w_zpI',   'zpI',   2, 1, 'DBE4'), \
          'cpx.s_abs'   : ('cps_abs',     'abs',   2, 2, '8BEC'), \
          'cpx.sw_abs'  : ('cps.w_abs',   'abs',   2, 2, 'CBEC'), \
          'cpx.s_absI'  : ('cps_absI',    'absI',  3, 2, '8B9BEC'), \
          'cpx.sw_absI' : ('cps.w_absI',  'absI',  2, 2, 'DBEC'), \
          'inx.s_imp'   : ('ins_imp',     'imp',   2, 0, '8BE8'), \
          'inx.sw_imp'  : ('ins.w_imp',   'imp',   2, 0, 'CBE8'), \
          'dex.s_imp'   : ('des_imp',     'imp',   2, 0, '8BCA'), \
          'dex.sw_imp'  : ('des.w_imp',   'imp',   2, 0, 'CBCA') }

lines = []
with open('OpcodeTblGen.txt', 'rt') as finp:
    lines = finp.readlines()
lines = lines[1:] # Delete header line

flds = []
for ln in lines:
    fld = ln.split()
    flds.append(tuple(fld))
        
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

'''
    Add instructions using OSX prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    osx = osx.lower()

    if osx == 'y':
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

        opcode = '_'.join([''.join([opcode, '.s']), mode])
        if opcode in osxMap:
            opcode, mode, opLen, dtLen, code = osxMap[opcode]

            if opcode in opcodeDict:
                continue
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            continue

'''
    Add instructions using OSZ prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    osz = osz.lower()

    if osz == 'y':
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

        opcode = '_'.join([''.join([opcode, '.sw']), mode])
        if opcode in osxMap:
            opcode, mode, opLen, dtLen, code = osxMap[opcode]

            if opcode in opcodeDict:
                continue
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            continue

'''
    Add instructions using OIS prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    ois = ois.lower()

    if ois == 'y':
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

        opcode = '_'.join([''.join([opcode, '.s']), mode + 'I'])
        if opcode in osxMap:
            opcode, mode, opLen, dtLen, code = osxMap[opcode]

            if opcode in opcodeDict:
                continue
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            continue

'''
    Add instructions using OSX + IND prefix instruction
'''

for fld in flds:
    code, opcode, mode, ind, siz, isz, osx, osz, ois, oax, oay = fld

    opcode = opcode.lower()
    ind = ind.lower()
    osx = osx.lower()

    if osx == 'y' and ind == 'y':
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

        opcode = '_'.join([''.join([opcode, '.s']), mode + 'I'])
        if opcode in osxMap:
            opcode, mode, opLen, dtLen, code = osxMap[opcode]

            if opcode in opcodeDict:
                continue
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opLen, dtLen, code, mode]
                print(opcode, 0, opLen, dtLen, code, mode)
                print(opcode, 0, opLen, dtLen, code, mode, file=fout)
        else:
            continue

fout.close()

