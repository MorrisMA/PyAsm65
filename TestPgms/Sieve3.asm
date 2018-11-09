;    1: PROGRAM eratosthenes(output);
    .stk 256
    .cod 512
STATIC_LINK .equ +5
RETURN_VALUE .equ -3
HIGH_RETURN_VALUE .equ -1
_start
    tsx.w       ; Preserve original stack pointer
    lds.w #_stk_top ; Initialize program stack pointer
    stz _bss_start
    ldx.w #_bss_start
    ldy.w #_bss_start+1
    lda.w #_stk_top
    sec
    sbc.w #_bss_start
    mov #10
    jmp _pc65_main
;    2:
;    3: CONST
;    4:     max = 1000;
;    5:
;    6: VAR
;    7:     sieve : ARRAY [1..max] OF BOOLEAN;
;    8:     i, j, limit, prime, factor : INTEGER;
;    9:
;   10: BEGIN
_pc65_main .sub
    phx.w
    tsx.w
;   11:     limit := max DIV 2;
    lda.w #500
    sta.w limit_005
;   12:     sieve[1] := FALSE;
    lda #0
    sta sieve_002
;   13:
;   14:     FOR i := 2 TO max DO
L_008
L_009
;   15:         sieve[i] := TRUE;
    lda #0xFF
    sta sieve_002+1
    dup x
    ldx.w #sieve_002+1
    ldy.w #sieve_002+2
    lda.w #1000-1
    mov #10
    rot x
L_010
;   16:
;   17:     prime := 1;
    lda #1
    sta.w prime_006
;   18:
;   19:     REPEAT
L_011
;   20:         prime := prime + 1;
    inc.w prime_006
;   21:         WHILE NOT sieve[prime] DO
L_013
    psh.w #sieve_002
    ldy.w prime_006
    dey.w
    lda (1,S),Y
    adj #2
    beq L_014
    bra L_015
L_014
;   22:             prime := prime + 1;
    inc.w prime_006
    bra L_013
L_015
;   23:
;   24:         factor := 2*prime;
    lda.w prime_006
    asl.w a
    sta.w factor_007
;   25:
;   26:         WHILE factor <= max DO BEGIN
L_016
    lda.w factor_007
    cmp.w #1000
    ble L_017
    bra L_018
L_017
;   27:             sieve[factor] := FALSE;
    psh.w #sieve_002
    ldy.w factor_007
    dey.w
    lda #0
    sta (1,S),Y
    adj #2
;   28:             factor := factor + prime;
    lda.w factor_007
    clc
    adc.w prime_006
    sta.w factor_007
;   29:         END
    bra L_016
;   30:     UNTIL prime > limit;
L_018
    lda.w prime_006
    cmp.w limit_005
    bgt L_012
    jmp L_011
L_012
;   31:
;   32:     writeln('Sieve of Eratosthenes');
    psh.w #S_021
    psh.w #0
    psh.w #21
    jsr _swrite
    adj #6
    jsr _writeln
;   33:     writeln;
    jsr _writeln
;   34:
;   35:     i := 1;
    lda #1
    sta.w i_003
;   36:     REPEAT
L_022
;   37:         FOR j := 0 TO 19 DO BEGIN
    lda #0
    sta.w j_004
L_024
    lda #19
    cmp.w j_004
    bge L_025
    bra L_026
L_025
;   38:             prime := i + j;
    lda.w i_003
    clc
    adc.w j_004
    sta.w prime_006
;   39:             IF sieve[prime] THEN
    psh.w #sieve_002
    ldy.w prime_006
    dey.w
    lda (1,S),Y
    adj #2
    bne L_027
    bra L_028
L_027
;   40:                 write(prime:3)
    lda.w prime_006
    pha.w
    lda #3
    pha.w
    jsr _iwrite
    adj #4
;   41:             ELSE
    bra L_029
L_028
;   42:                 write('   ');
    psh.w #S_030
    psh.w #0
    psh.w #3
    jsr _swrite
    adj #6
L_029
;   43:         END;
    inc.w j_004
    bra L_024
L_026
;   44:         writeln;
    jsr _writeln
;   45:         i := i + 20
    lda.w i_003
    clc
    adc.w #20
    sta.w i_003
;   46:     UNTIL i > max
    cmp.w #1000
    bgt L_023
    bra L_022
;   47: END.
L_023
    plx.w
    rts
    .end _pc65_main
;
;   unsigned division 16 x 16
;
            .cod
;
_Q          .equ    5
_D          .equ    3
;
_idiv       .proc
            lda #0          ; clear remainder (A)
            dup a           ; push
            lda.w _Q,S      ; load dividend (Q)
            ldy #16         ; bit counter
;
_idiv_Lp
            clc
            asl.w a         ; shift AQ left
            swp a
            rol.w a
;
            bcs _idiv_Plus  ; if A < 0 then A = A + D else A = A - D
;
_idiv_Minus
            sec
            sbc.w _D,S      ; subtract divisor (D)
;
            bra _idiv_Next
;
_idiv_Plus
            clc
            adc.w _D,S      ; add divisor (D)
;
_idiv_Next
            swp a           ; restore order of Acc stack {Q, A, -}
            bmi _idiv_Dec   ; if A < 0 then Q[0] = 0 else Q[0] = 1
            inc.w a
;
_idiv_Dec
            dey             ; loop until loop counter == 0
            bne _idiv_Lp
;
_idiv_Exit
            swp a           ; Test remainder
            ora.w #0
            bpl _idiv_Finish
            clc
            adc.w 3,S
_idiv_Finish
            swp a
;
            rts
;
            .endp _idiv
;
; signed multiplication: 16 x 16 => 32
;
            .cod
;
_M          .equ    5
_R          .equ    3
;
_imul       .proc
            ldy #16             ; y = bit count
            lda #0              ; A = { 0,  x,  x} - clear product
            dup a               ; A = { 0,  0,  x}
            dup a               ; A = { 0,  0,  0}
            lda.w _R,S          ; A = { R,  0,  0} - load multiplier (R)
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
            adc.w _M,S          ; PH += M
            bra _imul_ShftP
;
_imul_SubShft
            bpl _imul_ShftP     ; (0, N) ? (P -= M) >> 1 : P >> 1
_imul_SubM
            sec
            sbc.w _M,S          ; PH -= M
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
            swp a               ; A = {PL, PH, `R}
;
            rts
;
            .endp _imul

;
; put <newLine> to output
;
            .cod
;
_newLine    .equ    0x0A
_putChar    .equ    0xF001
;
_writeln    .proc
            lda #_newLine
            sta _putChar
;
            rts
;
            .endp _writeln
;
; put string to output
;
            .cod
;
_sPtrOff    .equ    7
_sLenOff    .equ    3
;
_swrite     .proc
            ldy.w _sLenOff,S        ; load string length
            lda.w _sPtrOff,S        ; load string pointer
            tai                     ; transfer sptr to IP
;
_swrite_Lp
            lda 0,I++               ; load char from strig
            sta _putChar            ; write char to output
;
            dey.w                   ; loop while string length <> 0
            bne _swrite_Lp
;
            rts
;
            .endp _swrite
;
; put integer to output
;
            .cod
;
_iValOff    .equ    7
_fLenOff    .equ    5
_iCntOff    .equ    -1
;
_iwrite     .proc
            phx.w                   ; save current base pointer
            tsx.w                   ; assign new base pointer
;
            lda _fLenOff,X          ; load field width specifier
            cmp #5                  ; compare against max integer digit count
            ble _iwrite_SetCnt
            lda #5
;
_iwrite_SetCnt
            pha.w                   ; set iteration count to fld width
            lda.w _iValOff,X        ; load a with integer value
;
_iwrite_Lp
            pha.w                   ; push dividend argument to _idiv
            psh.w #10               ; push divisor argument to _idiv
            csr _idiv               ; determine the remainder,
            adj #4                  ; remove arguments passed to _idiv from stk
            swp a                   ; put the remainder into ATOS
;
            clc                     ; convert remainder into ASCII character
            adc #48
            pha                     ; push LS digit of integer onto stack
;
            rot a                   ; rotate quotient into ATOS position
;
            dec.w _iCntOff,X        ; decrement digit iteration count
            bne _iwrite_Lp
;-------------------------------------------------------------------------------
            dup a                   ; save integer part of the conversion
;-------------------------------------------------------------------------------
_iwrite_Fill
            lda _fLenOff,X          ; load field width specifier
            cmp #5                  ; compare against max integer digit count
            ble _iwrite_GenPtr
            sec                     ; subtract max integer length from fld len
            sbc #5
            tay                     ; set difference as loop counter
            lda #48                 ; fill remaining field with '0'
;
_iwrite_Fill_Lp                     ; increase string on stack with fill data
            pha
            dey
            bne _iwrite_Fill_Lp
;-------------------------------------------------------------------------------
_iwrite_GenPtr
            tsa.w                   ; transfer current stk pointer to A
            inc.w a                 ; remove stack pointer write bias
            pha.w                   ; push string pointer to stack
;-------------------------------------------------------------------------------
            rot a                   ; restore integer part of the conversion
;-------------------------------------------------------------------------------
            cmp.w #0                ; test for 0. If not 0, int > 10^fld
            beq _iwrite_Sup0
            ldy #0
_iwrite_ErrLp
            lda #0x2A               ; fill integer field with '*'
            sta (1,S),Y
            iny
            cmp.y _fLenOff,X
            bne _iwrite_ErrLp
            bra _iwrite_Exit
;-------------------------------------------------------------------------------
_iwrite_Sup0
            ldy #0                  ; initialize string index
_iwrite_Sup0_Lp
            lda (1,S),Y
            cmp #48                 ; if leading position == 0, replace with ' '
            bne _iwrite_Exit        ; exit loop on first non-0 digit
            lda #32                 ; replace leading 0 with ' '
            sta (1,S),Y
            iny                     ; increment string index and compare to fLen
            cmp.y _fLenOff,X
            bne _iwrite_Sup0_Lp     ; loop until Y == fLen
;-------------------------------------------------------------------------------
_iwrite_Exit
            psh.w #0                ; NULL argument
            lda _fLenOff,X          ; push field width specifier
            pha.w
            csr _swrite             ; write integer value string using _swrite()
            adj #6                  ; remove parameters to _swrite() from stack
;
            txs.w                   ; deallocate stack variables
            plx.w                   ; restore previous base pointer
            rts
;
            .endp _iwrite

    .dat

S_030 .str "   "
S_021 .str "Sieve of Eratosthenes"
_bss_start .byt 2
sieve_002 .byt 1000
i_003 .wrd 1
j_004 .wrd 1
limit_005 .wrd 1
prime_006 .wrd 1
factor_007 .wrd 1
_bss_end .byt 2
_stk .byt 256
_stk_top .byt 1

    .end
