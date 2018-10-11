; signed multiplication: 16 x 16 => 32
        .cod 512
_imul   .proc
        ldy #16             ; y = bit count
        lda #0              ; A = { 0,  x,  x} - clear product              
        dup a               ; A = { 0,  0,  x}
        dup a               ; A = { 0,  0,  0}
        lda.w 3,S           ; A = { R,  0,  0} - load multiplier (R)       
        rev                 ; A = {`R,  0,  0} - reverse multiplier (`R)
        ora.w #0            ; set N flag if msb ATOS == 1
        clc                 ; initialize Booth recoding bit
        rot a               ; A = {PH, PL, `R}
;
        bra _imul_TstB
;
_imul_Lp
        asl.w a             ; A = {`R << 1, PH, PL}
        rot a               ; A = {PH, PL, `R}
_imul_TstB
        bcc _imul_SubShft   ; (C, x) ? Add_Shift : Sub_Shift
;
_imul_AddShft
        bmi _imul_ShftP     ; (1, N) ? P >> 1 : (P += M) >> 1
_imul_AddM
        clc
        adc.w 5,S           ; PH += M
        bra _imul_ShftP
;
_imul_SubShft
        bpl _imul_ShftP     ; (0, N) ? (P -= M) >> 1 : P >> 1
_imul_SubM
        sec
        sbc.w 5,S           ; PH -= M
;
_imul_ShftP
        asr.w a             ; A = {PH >> 1, PL, `R}
        rot a               ; A = {PL, `R, PH}
        ror.w a             ; A = {PL >> 2, `R, PH}
        rot a               ; A = {`R, PH, PL}
;
_imul_Dec
        dey
        bne _imul_Lp
;
_imul_Exit
        rot a               ; A = {PH, PL, `R}
        rts
;
        .endp
        .end
