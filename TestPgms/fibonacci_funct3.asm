;    1: PROGRAM Fibonacci (output);
	.stk 1024
	.cod 512
STATIC_LINK .equ +5
RETURN_VALUE .equ -3
HIGH_RETURN_VALUE .equ -1
_start
	tsx.w		; Preserve original stack pointer
	lds.w #_stk_top	; Initialize program stack pointer
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
;    4:     max = 23;
;    5: 
;    6: VAR
;    7:     i, j : INTEGER;
;    8:     
;    9: FUNCTION FIB(n : INTEGER) : INTEGER;
;   10:     VAR i, tmp, fn1, fn2 : INTEGER;
;   11:     
;   12:     BEGIN
n_005 .equ +7
i_006 .equ -5
tmp_007 .equ -7
fn1_008 .equ -9
fn2_009 .equ -11
fib_004 .sub
	phx.w
	tsx.w
	adj #-4
	adj #-8
;   13:         fn1 := 1;
	lda #1
	sta.w fn1_008,X
;   14:         fn2 := 0;
	lda #0
	sta.w fn2_009,X
;   15:         
;   16:         IF n < 1 THEN
	lda.w n_005,X
	pha.w
	lda #1
	xma.w 1,S
	cmp.w 1,S
	adj #2
	php
	lda #1
	plp
	blt L_012
	lda #0
L_012
	cmp.w #1
	beq L_010
	jmp L_011
L_010
;   17:             FIB := fn2
;   18:         ELSE BEGIN
	lda.w fn2_009,X
	sta.w RETURN_VALUE,X
	jmp L_013
L_011
;   19:             i := 1;
	lda #1
	sta.w i_006,X
;   20:             REPEAT
L_014
;   21:                 tmp := fn1 + fn2;
	lda.w fn1_008,X
	pha.w
	lda.w fn2_009,X
	clc
	adc.w 1,S
	adj #2
	sta.w tmp_007,X
;   22:                 fn2 := fn1;
	lda.w fn1_008,X
	sta.w fn2_009,X
;   23:                 fn1 := tmp;
	lda.w tmp_007,X
	sta.w fn1_008,X
;   24:                 
;   25:                 i := i + 1
	lda.w i_006,X
	pha.w
	lda #1
;   26:             UNTIL (i >= n);
	clc
	adc.w 1,S
	adj #2
	sta.w i_006,X
	lda.w i_006,X
	pha.w
	lda.w n_005,X
	xma.w 1,S
	cmp.w 1,S
	adj #2
	php
	lda #1
	plp
	bge L_016
	lda #0
L_016
	cmp.w #1
	beq L_015
	jmp L_014
L_015
;   27:             
;   28:             FIB := fn1
;   29:         END
	lda.w fn1_008,X
	sta.w RETURN_VALUE,X
;   30:     END;
L_013
	lda.w RETURN_VALUE,X
	txs.w
	plx.w
	rts
	.end fib_004
;   31:     
;   32: BEGIN
_pc65_main .sub
	phx.w
	tsx.w
;   33: {
;   34:     FOR i := 1 to max DO BEGIN
;   35:         j := FIB(i);
;   36:     END;
;   37: }
;   38:     i := max;
	lda #23
	sta.w i_002
;   39:     j := FIB(i);
	lda.w i_002
	pha.w
	phx.w
	jsr fib_004
	adj #4
	sta.w j_003
;   40:     write('Fib[');
	psh.w #S_017
	psh.w #0
	psh.w #4
	jsr _swrite
	adj #6
;   41:     write(i:2);
	lda.w i_002
	pha.w
	lda #2
	pha.w
	jsr _iwrite
	adj #4
;   42:     write('] = ');
	psh.w #S_018
	psh.w #0
	psh.w #4
	jsr _swrite
	adj #6
;   43:     write(j:5);
	lda.w j_003
	pha.w
	lda #5
	pha.w
	jsr _iwrite
	adj #4
;   44:     writeln
;   45: END.
	jsr _writeln
	plx.w
	rts
	.end _pc65_main
;
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
;
	.dat

S_018 .str "] = "
S_017 .str "Fib["
_bss_start .byt 0
i_002 .wrd 0
j_003 .wrd 0
_bss_end .byt 0
_stk .byt 0[1023]
_stk_top .byt -1

	.end
