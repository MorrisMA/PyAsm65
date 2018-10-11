'''
    Opcode Table Generator

        This program generates the OpcodeTbl.txt file needed by the Simple
        M65C02A Assembler. The input to the program is a file the provides
        the base opcode, base addressing mode, and the allowed prefix
        instructions. Opcodes are "decorated" by .w, .s, or .sw to signify
        the size of the operation, a change in the default stack pointer to
        be used for stack operations, or both: pha, pla, phx, plx, phy, ply,
        phs, pls, psh, pul, phr, jsr, csr, rts, rti, phi, pli, phw, plw, and
        ent.

        The white space delimited source file for the Opcode Table Generator
        has the following format:

        code opcode Mode ind siz isz osx osz ois oax oay
'''

import re
import os

preByte = {'osx' : '8B', \
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

relMap = {'bra_relI'      : ('jra_rel',     2, 2, '9B80'), \
          'bpl_relI'      : ('jpl_rel',     2, 2, '9B10'), \
          'bmi_relI'      : ('jmi_rel',     2, 2, '9B30'), \
          'bvc_relI'      : ('jvc_rel',     2, 2, '9B50'), \
          'bvs_relI'      : ('jvs_rel',     2, 2, '9B70'), \
          'bcc_relI'      : ('jcc_rel',     2, 2, '9B90'), \
          'bcs_relI'      : ('jcs_rel',     2, 2, '9BB0'), \
          'bne_relI'      : ('jne_rel',     2, 2, '9BD0'), \
          'beq_relI'      : ('jeq_rel',     2, 2, '9BF0'), \
          'bpl.w_rel'     : ('bgt_rel',     2, 1, 'AB10'), \
          'bmi.w_rel'     : ('ble_rel',     2, 1, 'AB30'), \
          'bvc.w_rel'     : ('bge_rel',     2, 1, 'AB50'), \
          'bvs.w_rel'     : ('blt_rel',     2, 1, 'AB70'), \
          'bcc.w_rel'     : ('bls_rel',     2, 1, 'AB90'), \
          'bcs.w_rel'     : ('bhi_rel',     2, 1, 'ABB0'), \
          'bne.w_rel'     : ('blo_rel',     2, 1, 'ABD0'), \
          'beq.w_rel'     : ('bhs_rel',     2, 1, 'ABF0'), \
          'bpl.w_relI'    : ('jgt_rel',     2, 2, 'BB10'), \
          'bmi.w_relI'    : ('jle_rel',     2, 2, 'BB30'), \
          'bvc.w_relI'    : ('jge_rel',     2, 2, 'BB50'), \
          'bvs.w_relI'    : ('jlt_rel',     2, 2, 'BB70'), \
          'bcc.w_relI'    : ('jls_rel',     2, 2, 'BB90'), \
          'bcs.w_relI'    : ('jhi_rel',     2, 2, 'BBB0'), \
          'bne.w_relI'    : ('jlo_rel',     2, 2, 'BBD0'), \
          'beq.w_relI'    : ('jhs_rel',     2, 2, 'BBF0') }

indMap = {'txs_impI'      : ('txu_imp',     2, 0, '9B9A'), \
          'txs.w_impI'    : ('txu.w_imp',   2, 0, 'BB9A'), \
          'tsx_impI'      : ('tux_imp',     2, 0, '9BBA'), \
          'tsx.w_impI'    : ('tux.w_imp',   2, 0, 'BBBA'), \
          'nxt_impI'      : ('inxt_imp',    2, 0, '9B3B'), \
          'phi_impI'      : ('phw_imp',     2, 0, '9B4B'), \
          'ini_impI'      : ('inw_imp',     2, 0, '9B5B'), \
          'pli_impI'      : ('plw_imp',     2, 0, '9B6B'), \
          'ent_impI'      : ('ient_imp',    2, 0, '9B7B') }
          

accMap = {'asl_acc'       : ('asl_a',       1, 0, '0A'), \
          'asl.w_acc'     : ('asl.w_a',     2, 0, 'AB0A'), \
          'inc_acc'       : ('inc_a',       1, 0, '1A'), \
          'inc.w_acc'     : ('inc.w_a',     2, 0, 'AB1A'), \
          'rol_acc'       : ('rol_a',       1, 0, '2A'), \
          'rol.w_acc'     : ('rol.w_a',     2, 0, 'AB2A'), \
          'dec_acc'       : ('dec_a',       1, 0, '3A'), \
          'dec.w_acc'     : ('dec.w_a',     2, 0, 'AB3A'), \
          'lsr_acc'       : ('lsr_a',       1, 0, '4A'), \
          'lsr_accI'      : ('asr_a',       2, 0, '9B4A'), \
          'lsr.w_accI'    : ('asr.w_a',     2, 0, 'BB4A'), \
          'lsr.w_acc'     : ('lsr.w_a',     2, 0, 'AB4A'), \
          'ror_acc'       : ('ror_a',       1, 0, '6A'), \
          'ror.w_acc'     : ('ror.w_a',     2, 0, 'AB6A'), \
          'dup_acc'       : ('dup_a',       1, 0, '0B'), \
          'dup_accI'      : ('tai_imp',     2, 0, '9B0B'), \
          'dup.w_acc'     : ('tia_imp',     2, 0, 'AB0B'), \
          'dup.w_accI'    : ('xai_imp',     2, 0, 'BB0B'), \
          'swp_acc'       : ('swp_a',       1, 0, '1B'), \
          'swp_accI'      : ('bsw_imp',     2, 0, '9B1B'), \
          'rot_acc'       : ('rot_a',       1, 0, '2B'), \
          'rot_accI'      : ('rev_imp',     2, 0, '9B2B') }

osxMap = {'jsr_absS'      : ('jsr.s_abs',   2, 2, '8B20'), \
          'jsr_absSI'     : ('jsr.s_absI',  2, 2, 'DB20'), \
          'rti.s_imp'     : ('rti.s_imp',   2, 0, '8B40'), \
          'rts.s_imp'     : ('rts.s_imp',   2, 0, '8B60'), \
          'adj.s_imm'     : ('adj.s_imm',   2, 1, '8BC2'), \
          'adj.sw_imm'    : ('adj.sw_imm',  2, 2, 'CBC2'), \
          'phr.s_rel16'   : ('phr.s_rel',   2, 2, '8B5C'), \
          'phr.sw_rel16I' : ('csr.s_rel',   2, 2, 'DB5C'), \
          'phr.s_rel16I'  : ('csr.s_rel',   2, 2, 'DB5C'), \
          'psh.s_imm'     : ('psh.s_imm',   2, 1, '8BE2'), \
          'psh.sw_imm'    : ('psh.sw_imm',  2, 2, 'CBE2'), \
          'psh_zpS'       : ('psh.s_zp',    2, 1, '8BD4'), \
          'psh_absS'      : ('psh.s_abs',   2, 2, '8BDC'), \
          'psh.w_zpS'     : ('psh.sw_zp',   2, 1, 'CBD4'), \
          'psh.w_absS'    : ('psh.sw_abs',  2, 2, 'CBDC'), \
          'psh.w_zpSI'    : ('psh.sw_zpI',  2, 1, 'DBD4'), \
          'psh.w_absSI'   : ('psh.sw_absI', 2, 2, 'DBDC'), \
          'psh_zpSI'      : ('psh.s_zpI',   3, 1, '8B9BD4'), \
          'psh_absSI'     : ('psh.s_absI',  3, 2, '8B9BDC'), \
          'pul_zpS'       : ('pul.s_zp',    2, 1, '8BF4'), \
          'pul_absS'      : ('pul.s_abs',   2, 2, '8BFC'), \
          'pul.w_zpS'     : ('pul.sw_zp',   2, 1, 'CBF4'), \
          'pul.w_absS'    : ('pul.sw_abs',  2, 2, 'CBFC'), \
          'pul.w_zpSI'    : ('pul.sw_zpI',  2, 1, 'DBF4'), \
          'pul.w_absSI'   : ('pul.sw_absI', 2, 2, 'DBFC'), \
          'pul_zpSI'      : ('pul.s_zpI',   3, 1, '8B9BF4'), \
          'pul_absSI'     : ('pul.s_absI',  3, 2, '8B9BFC'), \
          'nxt.s_imp'     : ('nxt.s_imp',   2, 0, '8B3B'), \
          'nxt.s_impI'    : ('inxt.s_imp',  2, 0, 'DB3B'), \
          'phi.s_imp'     : ('phi.s_imp',   2, 0, '8B4B'), \
          'phi.s_impI'    : ('phw.s_imp',   2, 0, 'DB4B'), \
          'pli.s_imp'     : ('pli.s_imp',   2, 0, '8B6B'), \
          'pli.s_impI'    : ('plw.s_imp',   2, 0, 'DB6B'), \
          'ent.s_imp'     : ('ent.s_imp',   2, 0, '8B7B'), \
          'ent.s_impI'    : ('ient.s_imp',  2, 0, 'DB7B'), \
          'ldx.s_imm'     : ('lds_imm',     2, 1, '8BA2'), \
          'ldx.sw_imm'    : ('lds.w_imm',   2, 2, 'CBA2'), \
          'ldx_zpS'       : ('lds_zp',      2, 1, '8BA6'), \
          'ldx_zpSI'      : ('lds_zpI',     3, 1, '8B9BA6'), \
          'ldx.w_zpS'     : ('lds.w_zp',    2, 1, 'CBA6'), \
          'ldx.w_zpSI'    : ('lds.w_zpI',   2, 1, 'DBA6'), \
          'ldx.s_zpY'     : ('lds_zpY',     2, 1, '8BB6'), \
          'ldx.s_zpYI'    : ('lds_zpIY',    3, 1, '8B9BB6'), \
          'ldx.sw_zpY'    : ('lds.w_zpY',   2, 1, 'CBB6'), \
          'ldx.sw_zpYI'   : ('lds.w_zpIY',  2, 1, 'DBB6'), \
          'ldx_absS'      : ('lds_abs',     2, 2, '8BAE'), \
          'ldx_absSI'     : ('lds_absI',    3, 2, '8B9BAE'), \
          'ldx.w_absS'    : ('lds.w_abs',   2, 2, 'CBAE'), \
          'ldx.w_absSI'   : ('lds.w_absI',  2, 2, 'DBAE'), \
          'ldx.s_absY'    : ('lds_absY',    2, 2, '8BBE'), \
          'ldx_absSIY'    : ('lds_absIY',   3, 2, '8B9BBE'), \
          'ldx.sw_absY'   : ('lds.w_absY',  2, 2, 'CBBE'), \
          'ldx.w_absSIY'  : ('lds.w_absIY', 2, 2, 'DBBE'), \
          'stx_zpS'       : ('sts_zp',      2, 1, '8B86'), \
          'stx_zpSI'      : ('sts_zpI',     3, 1, '8B9B86'), \
          'stx.w_zpS'     : ('sts.w_zp',    2, 1, 'CB86'), \
          'stx.w_zpSI'    : ('sts.w_zpI',   2, 1, 'DB86'), \
          'stx.s_zpY'     : ('sts_zpY',     2, 1, '8B96'), \
          'stx.s_zpYI'    : ('sts_zpIY',    3, 1, '8B9B96'), \
          'stx.sw_zpY'    : ('sts.w_zpY',   2, 1, 'CB96'), \
          'stx.sw_zpYI'   : ('sts.w_zpIY',  2, 1, 'DB96'), \
          'stx_absS'      : ('sts_abs',     2, 2, '8B8E'), \
          'stx_absSI'     : ('sts_absI',    3, 2, '8B9B8E'), \
          'stx.w_absS'    : ('sts.w_abs',   2, 2, 'CB8E'), \
          'stx.w_absSI'   : ('sts.w_absI',  2, 2, 'DB8E'), \
          'cpx.s_imm'     : ('cps_imm',     2, 1, '8BE0'), \
          'cpx.sw_imm'    : ('cps.w_imm',   2, 2, 'CBE0'), \
          'cpx_zpS'       : ('cps_zp',      2, 1, '8BE4'), \
          'cpx_zpSI'      : ('cps_zpI',     3, 1, '8B9BE4'), \
          'cpx.w_zpS'     : ('cps.w_zp',    2, 1, 'CBE4'), \
          'cpx.w_zpSI'    : ('cps.w_zpI',   2, 1, 'DBE4'), \
          'cpx_absS'      : ('cps_abs',     2, 2, '8BEC'), \
          'cpx_absSI'     : ('cps_absI',    3, 2, '8B9BEC'), \
          'cpx.w_absS'    : ('cps.w_abs',   2, 2, 'CBEC'), \
          'cpx.w_absSI'   : ('cps.w_absI',  2, 2, 'DBEC'), \
          'inx.s_imp'     : ('ins_imp',     2, 0, '8BE8'), \
          'inx.sw_imp'    : ('ins.w_imp',   2, 0, 'CBE8'), \
          'dex.s_imp'     : ('des_imp',     2, 0, '8BCA'), \
          'dex.sw_imp'    : ('des.w_imp',   2, 0, 'CBCA'), \
          'txa.s_imp'     : ('tsa_imp',     2, 0, '8B8A'), \
          'txa.sw_imp'    : ('tsa.w_imp',   2, 0, 'CB8A'), \
          'tax.s_imp'     : ('tas_imp',     2, 0, '8BAA'), \
          'tax.sw_imp'    : ('tas.w_imp',   2, 0, 'CBAA'), \
          'txa.s_impI'    : ('tua_imp',     3, 0, '8B9B8A'), \
          'txa.sw_impI'   : ('tua.w_imp',   2, 0, 'DB8A'), \
          'tax.s_impI'    : ('tau_imp',     3, 0, '8B9BAA'), \
          'tax.sw_impI'   : ('tau.w_imp',   2, 0, 'DBAA') }

accTuple = ('ora', 'and', 'eor', \
            'adc', 'sbc', \
            'bit', 'trb', 'tsb', )
rmwTuple = ('asl', 'rol', 'lsr', 'asr', 'ror', 'dec', 'inc',)
stkTuple = ('dup', 'swp', 'rot', )
spcTuple = ('jmp', 'ldy', )
ippTuple = ('sta', 'lda', 'cmp', )

indexedByX = {'zpX'    : 'zpA',   \
              'zpXI'   : 'zpAI',  \
              'zpXII'  : 'zpAII', \
              'absX'   : 'absA',  \
              'absXI'  : 'absAI', \
              'absXII' : 'absAII' }
indexedByY = {'zpY'    : 'zpA',    \
              'zpIY'   : 'zpIA',   \
              'zpIIY'  : 'zpIIA',  \
              'absY'   : 'absA',   \
              'absIY'  : 'absIA',  \
              'zpSIY'  : 'zpSIA',  \
              'zpSIIY' : 'zpSIIA', \
              'absSIY' : 'absSIA', }
indexedByS = ('zpS', 'zpSI', 'zpSII',    \
              'zpSIY', 'zpSIIY',         \
              'absS', 'absSI', 'absSII', \
              'absSIY',)

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

    if mode == 'rel16':
        mode = 'rel'
        
    opcode = '_'.join([opcode, mode]); opLen = 1
    if opcode in accMap:
        opcode, opLen, dtLen, code = accMap[opcode]

    print(opcode, opLen, dtLen, code)
    print(opcode, opLen, dtLen, code, file=fout)
    opcodeList.append(opcode)
    opcodeDict[opcode] = [opcode, opLen, dtLen, code]

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

        code = ''.join([preByte['ind'], code]); opLen = 2
        if mode in ('imp', 'acc', 'imm', 'rel', 'rel16', 'zprel'):
            if mode == 'zprel':
                mode = 'zpIrel'
                opcode = '_'.join([opcode, mode])
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'rel16':
                mode = 'rel'
                opcode = '_'.join(['csr', mode])
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'rel':
                mode = mode + 'I'
                opcode = '_'.join([opcode, mode])
                if opcode in relMap:
                    opcode, opLen, dtLen, code = relMap[opcode]
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'acc':
                mode = mode + 'I'
                opcode = '_'.join([opcode, mode])
                if opcode in accMap:
                    opcode, opLen, dtLen, code = accMap[opcode]
                else:
                    continue
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'imp':
                mode = mode + 'I'
                opcode = '_'.join([opcode, mode])
                if opcode in indMap:
                    opcode, opLen, dtLen, code = indMap[opcode]
                else:
                    continue
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
        elif mode in ('zpY', 'zpIY', 'absY'):
            if mode == 'zpY':
                mode = 'zpIY'
            elif mode == 'zpIY':
                mode = 'zpIIY'
            else:
                mode = 'absIY'

            opcode = '_'.join([opcode, mode])
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            mode = mode + 'I'
            opcode = '_'.join([opcode, mode])
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

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

        code = ''.join([preByte['siz'], code]); opLen = 2
        if mode in ('imp', 'acc', 'imm', 'rel'):
            if mode == 'rel':
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in relMap:
                    opcode, opLen, dtLen, code = relMap[opcode]
                else:
                    continue

                if opcode in opcodeDict:
                    continue
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                    print(opcode, opLen, dtLen, code)
                    print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'imm':
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                dtLen += 1
                
                if opcode in opcodeDict:
                    continue
                else:
                    opcodeList.append(opcode)
                    opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                    print(opcode, opLen, dtLen, code)
                    print(opcode, opLen, dtLen, code, file=fout)
            elif mode in ['imp', 'acc']:
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in accMap:
                    opcode, opLen, dtLen, code = accMap[opcode]
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            else:
                dtLen += 1
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
        else:
            opcode = '_'.join([''.join([opcode, '.w']), mode])
            if opcode in opcodeDict:
                continue
            else:
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)

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

        code = ''.join([preByte['isz'], code]); opLen = 2
        if mode in ('imp', 'acc', 'imm', 'rel'):
            if mode == 'rel':
                mode = mode + 'I'
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in relMap:
                    opcode, opLen, dtLen, code = relMap[opcode]
                else:
                    continue
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'acc':
                mode = mode + 'I'
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in accMap:
                    opcode, opLen, dtLen, code = accMap[opcode]
                else:
                    continue
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
            elif mode == 'imp':
                mode = mode + 'I'
                opcode = '_'.join([''.join([opcode, '.w']), mode])
                if opcode in indMap:
                    opcode, opLen, dtLen, code = indMap[opcode]
                else:
                    continue
                if opcode in opcodeDict:
                    continue
                opcodeList.append(opcode)
                opcodeDict[opcode] = [opcode, opLen, dtLen, code]
                print(opcode, opLen, dtLen, code)
                print(opcode, opLen, dtLen, code, file=fout)
        elif mode in ('zpY', 'zpIY', 'absY'):
            if mode == 'zpY':
                mode = 'zpIY'
            elif mode == 'zpIY':
                mode = 'zpIIY'
            else:
                mode = 'absIY'
            opcode = '_'.join([''.join([opcode, '.w']), mode])
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            mode = mode + 'I'
            opcode = '_'.join([''.join([opcode, '.w']), mode])
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

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

        code = preByte['osx'] + code; opLen = 2
        if mode in ('zp',   'zpX',
                    'zpI',  'zpXI',
                    'zpIY', 
                    'abs',  'absX',
                    'absI', 'absXI',
                    'zprel'          ):
            if mode == 'zpX' or mode == 'zp':
                mode = 'zpS'
            elif mode == 'zpXI' or mode == 'zpI':
                mode = 'zpSI'
            elif mode == 'zpIY':
                mode = 'zpSIY'
            elif mode == 'absX' or mode == 'abs':
                mode = 'absS'
            elif mode == 'absXI' or mode == 'absI':
                mode = 'absSI'
            else:
                mode = 'zpSrel'

            opcode = '_'.join([opcode, mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            if mode in ['absY']:
                if opcode in ['ldx', 'stx']:
                    pass
                else:
                    continue
            opcode = '_'.join([''.join([opcode, '.s']), mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in ['phx.s_imp', 'plx.s_imp']:
                continue
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

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

        code = preByte['osz'] + code; opLen = 2
        if mode in ('zp',   'zpX',
                    'zpI',  'zpXI',
                    'zpIY', 
                    'abs',  'absX',
                    'absI', 'absXI',
                    'zprel'          ):
            if mode == 'zpX' or mode == 'zp':
                mode = 'zpS'
            elif mode == 'zpXI' or mode == 'zpI':
                mode = 'zpSI'
            elif mode == 'zpIY':
                mode = 'zpSIY'
            elif mode == 'absX' or mode == 'abs':
                mode = 'absS'
            elif mode == 'absXI' or mode == 'absI':
                mode = 'absSI'
            else:
                mode = 'zpSrel'

            opcode = '_'.join([''.join([opcode, '.w']), mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            opcode = '_'.join([''.join([opcode, '.sw']), mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in ['phx.sw_imp', 'plx.sw_imp']:
                continue
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

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

        code = preByte['ois'] + code; opLen = 2
        if mode in ('zp',   'zpX',
                    'zpI',  'zpXI',
                    'zpIY', 
                    'abs',  'absX',
                    'absI', 'absXI',
                    'absY',
                    'zprel'          ):
            if mode == 'zpX' or mode == 'zp':
                mode = 'zpSI'
            elif mode == 'zpXI' or mode == 'zpI':
                mode = 'zpSII'
            elif mode == 'zpIY':
                mode = 'zpSIIY'
            elif mode == 'absX' or mode == 'abs':
                mode = 'absSI'
            elif mode == 'absXI' or mode == 'absI':
                mode = 'absSII'
            elif mode == 'absY':
                mode = 'absSIY'
            else:
                mode = 'zpSIrel'

            opcode = '_'.join([''.join([opcode, '.w']), mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            opcode = '_'.join([''.join([opcode, '.sw']), mode + 'I'])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

'''
    Add instructions using OSX + IND prefix instruction
        These are stack-relative, or stack pointer instructions using
        indirection for byte-wide operations. These instructions require
        two prefixes to define the addressing mode and the operation/register
        to be used. Since it is more effective to work with a 16-bit stack
        pointer, using these instruction sequences is discouraged.
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

        code = preByte['osx'] + preByte['ind'] + code; opLen = 3
        if mode in ('zp',   'zpX',
                    'zpI',  'zpXI',
                    'zpIY', 
                    'abs',  'absX',
                    'absI', 'absXI',
                    'absY',
                    'zprel'          ):
            if mode == 'zpX' or mode == 'zp':
                mode = 'zpSI'
            elif mode == 'zpXI' or mode == 'zpI':
                mode = 'zpSII'
            elif mode == 'zpIY':
                mode = 'zpSIIY'
            elif mode == 'absX' or mode == 'abs':
                mode = 'absSI'
            elif mode == 'absXI' or mode == 'absI':
                mode = 'absSII'
            elif mode == 'absY':
                mode = 'absSIY'
            else:
                mode = 'zpSIrel'

            opcode = '_'.join([opcode, mode])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)
        else:
            opcode = '_'.join([''.join([opcode, '.s']), mode + 'I'])
            if opcode in osxMap:
                opcode, opLen, dtLen, code = osxMap[opcode]
            if opcode in opcodeDict:
                continue
            opcodeList.append(opcode)
            opcodeDict[opcode] = [opcode, opLen, dtLen, code]
            print(opcode, opLen, dtLen, code)
            print(opcode, opLen, dtLen, code, file=fout)

'''
    Add instructions using the OAX or the OAY prefix instructions.
        These prefixes affect the destination register of an instruction by
        swapping the A with either the X or the Y registers. If the X or Y
        registers are being used as index registers for the memory operand,
        the A register assumes their role, i.e. is used as the index register.

        The OAX prefix instructions is mutually exclusive with the OSX and OAY
        prefix instructions. The OAY prefix instruction can be paired with
        either OSX or OAX. However, pairing OAY indiscriminately with OSX can
        result in instructions that perform the same function as those that are
        native to the 6502/65C02/M65C02A or formed with shorter sequences of
        prefix instructions.

        Therefore, the following two code blocks will not add instructions to
        the Opcode Table that have already been added by the previous seven
        code blocks. To add OAX/OAY instructions, the existing Opcode Table will
        be sorted by its base instruction mnemonic. The OAX/OAY prefix will be
        added to those instructions in the sorted opcode table where its
        addition creates useful, non-duplicate functionality.
'''

instrByNameTbl = {}
maxInstrLen = 0

opcodes = list(opcodeList)

for opcode in opcodes:
    flds = opcodeDict[opcode]
    instr, addrMd = flds[0].split('_')
    base, *options = instr.split('.')
    opLen = int(flds[1])
    dtLen = int(flds[2])

    if base[-1].isdigit():
        base = base[:-1]

    if maxInstrLen < len(base):
        maxInstrLen = len(base)

    if base in instrByNameTbl:
        instrByNameTbl[base].append((base, options, addrMd, \
                                     opLen, dtLen, flds[3]))
    else:
        instrByNameTbl[base] = [(base, options, addrMd, \
                                 opLen, dtLen, flds[3])]
'''
    Add instructions using OAX prefix instruction.

        The instructions must be in the following Tuples:
            accTuple, spcTuple, ippTuple.
        For instructions in accTuple, if the instruction uses X as an index
        register, then the X in the addrMode is changed to A, i.e. A takes
        on the role of the index register. If the instruction is in spcTuple,
        the instruction is an instruction that does not use the ALU, i.e. jmp.
'''

for base in instrByNameTbl.keys():
    if base in accTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            if addrMd in indexedByS:
                continue
            
            if addrMd in indexedByX:
                addrMd = indexedByX[addrMd]

            if len(options) < 1:
                instr = '_'.join(['.'.join([base, 'x']), addrMd])
            else:
                instr = '_'.join(['.'.join([base, 'x' + options[0]]), addrMd])
            code = ''.join([preByte['oax'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in rmwTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            if addrMd in indexedByS:
                continue
            elif addrMd in indexedByX:
                addrMd = indexedByX[addrMd]
            elif addrMd == 'a':
                if base in ['dec', 'inc']:
                    continue
                else:
                    addrMd = 'x'
            else:
                continue

            if len(options) < 1:
                instr = '_'.join([base, addrMd])
            else:
                instr = '_'.join(['.'.join([base, options[0]]), addrMd])
            code = ''.join([preByte['oax'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in stkTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            instr = '_'.join([base, 'x'])
            code = ''.join([preByte['oax'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in spcTuple:
        for i in range(len(instrByNameTbl[base])):
            instr, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            if addrMd in indexedByX:
                if instr == 'ldy':
                    if len(options) == 0:
                        pass
                    else:
                        instr = '.'.join([instr, options[0]])
                    instr = '_'.join([instr, indexedByX[addrMd]])
                else: 
                    instr = '_'.join([instr, indexedByX[addrMd]])
                code = ''.join([preByte['oax'], code])
                opLen += 1
                
                opcodeList.append(instr)
                opcodeDict[opcode] = [instr, opLen, dtLen, code]
                print(instr, opLen, dtLen, code)
                print(instr, opLen, dtLen, code, file=fout)       
    elif base in ippTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]

            if addrMd == 'imm' and base in ['lda', 'cmp',]:
                continue

            if addrMd in indexedByS:
                continue
            
            if addrMd in indexedByX:
                addrMd = indexedByX[addrMd]

            if len(options) < 1:
                instr = '_'.join(['.'.join([base, 'x']), addrMd])
            else:
                instr = '_'.join(['.'.join([base, 'x' + options[0]]), addrMd])
            code = ''.join([preByte['oax'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
'''
    Add instructions using OAY prefix instruction.

        The instructions must be in the tuples:
            accTuple, rmwTuple, stkTuple, ippTuple.
        For instructions in tuples, accTuple and rmwTuple, if the instruction
        uses Y as an index register, then the Y in the addrMode is changed to A,
        i.e. A takes on the role of the index register.
'''

for base in instrByNameTbl.keys():
    if base in accTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            if addrMd in indexedByY:
                addrMd = indexedByY[addrMd]

            if len(options) < 1:
                instr = '_'.join(['.'.join([base, 'y']), addrMd])
            else:
                instr = '_'.join(['.'.join([base, 'y' + options[0]]), addrMd])
            code = ''.join([preByte['oay'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in rmwTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            if addrMd in indexedByY:
                addrMd = indexedByY[addrMd]
            elif addrMd == 'a':
                if base in ['dec', 'inc']:
                    continue
                else:
                    addrMd = 'y'
            else:
                continue
            
            if len(options) < 1:
                instr = '_'.join([base, addrMd])
            else:
                instr = '_'.join(['.'.join([base, options[0]]), addrMd])
            code = ''.join([preByte['oay'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in stkTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]
            
            instr = '_'.join([base, 'y'])
            code = ''.join([preByte['oay'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)
    elif base in ippTuple:
        for i in range(len(instrByNameTbl[base])):
            base, options, addrMd, opLen, dtLen, code = instrByNameTbl[base][i]

            if addrMd == 'imm' and base in ['lda', 'cmp',]:
                continue

            if addrMd in indexedByY:
                addrMd = indexedByY[addrMd]

            if len(options) < 1:
                instr = '_'.join(['.'.join([base, 'y']), addrMd])
            else:
                instr = '_'.join(['.'.join([base, 'y' + options[0]]), addrMd])
            code = ''.join([preByte['oay'], code])
            opLen += 1
            
            opcodeList.append(instr)
            opcodeDict[opcode] = [instr, opLen, dtLen, code]
            print(instr, opLen, dtLen, code)
            print(instr, opLen, dtLen, code, file=fout)

'''
    Add register-register instructions using OAX/OAY prefix instruction.
'''

xfrMap = {'txy'   : ('txy_imp', 2, 0, 'FB8A'), \
          'txy.w' : ('txy.w_imp', 3, 0, 'FBAB8A'), \
          'tyx'   : ('tyx_imp', 2, 0, 'EB98'), \
          'tyx.w' : ('tyx.w_imp', 3, 0, 'EBAB98') }

for i in xfrMap.keys():
    instr, opLen, dtLen, code = xfrMap[i]

    opcodeList.append(instr)
    opcodeDict[opcode] = [instr, opLen, dtLen, code]
    print(instr, opLen, dtLen, code)
    print(instr, opLen, dtLen, code, file=fout)

'''
    Close output file
'''

fout.close()
