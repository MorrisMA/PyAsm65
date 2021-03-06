;    1: PROGRAM newton (input, output);
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
;    4:     epsilon = 1e-6;
;    5: 
;    6: VAR
;    7:     number, root, sqroot : real;
;    8: 
;    9: BEGIN
_pc65_main .sub
	phx.w
	tsx.w
;   10:     REPEAT
L_005
;   11:     writeln;
	jsr _writeln
;   12:     write('Enter new number (0 to quit): ');
	psh.w #S_007
	psh.w #0
	psh.w #30
	jsr _swrite
	adj #6
;   13:     read(number);
	psh.w #number_002
	jsr _fread
	pli.s
	sta.w 0,I++
	swp a
	sta.w 0,I++
;   14: 
;   15:     IF number = 0 THEN BEGIN
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda #0
	pha.w
	jsr _fconv
	adj #2
	swp a
	pha.w
	swp a
	pha.w
	jsr _fcmp
	adj #8
	cmp.w #0
	php
	lda #1
	plp
	beq L_010
	lda #0
L_010
	cmp.w #1
	beq L_008
	jmp L_009
L_008
;   16:         writeln(number:12:6, 0.0:12:6);
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda #12
	pha.w
	lda #6
	pha.w
	jsr _fwrite
	adj #8
	lda.w F_011+2	;float_literal
	swp a
	lda.w F_011
	swp a
	pha.w
	swp a
	pha.w
	lda #12
	pha.w
	lda #6
	pha.w
	jsr _fwrite
	adj #8
	jsr _writeln
;   17:     END
;   18:     ELSE IF number < 0 THEN BEGIN
	jmp L_012
L_009
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda #0
	pha.w
	jsr _fconv
	adj #2
	swp a
	pha.w
	swp a
	pha.w
	jsr _fcmp
	adj #8
	cmp.w #0
	php
	lda #1
	plp
	blt L_015
	lda #0
L_015
	cmp.w #1
	beq L_013
	jmp L_014
L_013
;   19:         writeln('*** ERROR:  number < 0');
	psh.w #S_016
	psh.w #0
	psh.w #22
	jsr _swrite
	adj #6
	jsr _writeln
;   20:     END
;   21:     ELSE BEGIN
	jmp L_017
L_014
;   22:         sqroot := sqrt(number);
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	jsr _fsqrt
	adj #4
	sta.w sqroot_004
	swp a
	sta.w sqroot_004+2	;assgnment_statement
;   23:         writeln(number:12:6, sqroot:12:6);
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda #12
	pha.w
	lda #6
	pha.w
	jsr _fwrite
	adj #8
	lda.w sqroot_004+2	;emit_load_value
	swp a
	lda.w sqroot_004
	swp a
	pha.w
	swp a
	pha.w
	lda #12
	pha.w
	lda #6
	pha.w
	jsr _fwrite
	adj #8
	jsr _writeln
;   24:         writeln;
	jsr _writeln
;   25: 
;   26:         root := 1;
	lda #1
	pha.w
	jsr _fconv
	adj #2
	sta.w root_003
	swp a
	sta.w root_003+2	;assgnment_statement
;   27:         REPEAT
L_018
;   28:         root := (number/root + root)/2;
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda.w root_003+2	;emit_load_value
	swp a
	lda.w root_003
	swp a
	pha.w
	swp a
	pha.w
	jsr _fdiv
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	lda.w root_003+2	;emit_load_value
	swp a
	lda.w root_003
	swp a
	pha.w
	swp a
	pha.w
	jsr _fadd
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	lda #2
	pha.w
	jsr _fconv
	adj #2
	swp a
	pha.w
	swp a
	pha.w
	jsr _fdiv
	adj #8
	sta.w root_003
	swp a
	sta.w root_003+2	;assgnment_statement
;   29:         writeln(root:24:6,
	lda.w root_003+2	;emit_load_value
	swp a
	lda.w root_003
	swp a
	pha.w
	swp a
	pha.w
	lda #24
	pha.w
	lda #6
	pha.w
	jsr _fwrite
	adj #8
;   30:             100*abs(root - sqroot)/sqroot:12:2,
	lda #100
	pha.w
	lda.w root_003+2	;emit_load_value
	swp a
	lda.w root_003
	swp a
	pha.w
	swp a
	pha.w
	lda.w sqroot_004+2	;emit_load_value
	swp a
	lda.w sqroot_004
	swp a
	pha.w
	swp a
	pha.w
	jsr _fsub
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	jsr _fabs
	adj #4
	swp a
	pha.w
	swp a
	pha.w
	pla.w
	swp a
	pla.w
	ply.w
	pha.w
	swp a
	pha.w
	phy.w
	jsr _fconv
	adj #2
	ply.w
	swp y
	ply.w
	swp a
	pha.w
	swp a
	pha.w
	phy.w
	swp y
	phy.w
	jsr _fmul
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	lda.w sqroot_004+2	;emit_load_value
	swp a
	lda.w sqroot_004
	swp a
	pha.w
	swp a
	pha.w
	jsr _fdiv
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	lda #12
	pha.w
	lda #2
	pha.w
	jsr _fwrite
	adj #8
;   31:             '%')
	lda #37
	pha.w
	psh.w #0
	jsr _cwrite
	adj #4
;   32:         UNTIL abs(number/sqr(root) - 1) < epsilon;
	jsr _writeln
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda.w root_003+2	;emit_load_value
	swp a
	lda.w root_003
	swp a
	pha.w
	swp a
	pha.w
	swp a
	pha.w
	swp a
	pha.w
	jsr _fmul
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	jsr _fdiv
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	lda #1
	pha.w
	jsr _fconv
	adj #2
	swp a
	pha.w
	swp a
	pha.w
	jsr _fsub
	adj #8
	swp a
	pha.w
	swp a
	pha.w
	jsr _fabs
	adj #4
	swp a
	pha.w
	swp a
	pha.w
	lda.w F_020+2	;float_literal
	swp a
	lda.w F_020
	swp a
	pha.w
	swp a
	pha.w
	jsr _fcmp
	adj #8
	cmp.w #0
	php
	lda #1
	plp
	blt L_021
	lda #0
L_021
	cmp.w #1
	beq L_019
	jmp L_018
L_019
;   33:     END
;   34:     UNTIL number = 0
L_017
L_012
	lda.w number_002+2	;emit_load_value
	swp a
	lda.w number_002
	swp a
	pha.w
	swp a
	pha.w
	lda #0
;   35: END.
	pha.w
	jsr _fconv
	adj #2
	swp a
	pha.w
	swp a
	pha.w
	jsr _fcmp
	adj #8
	cmp.w #0
	php
	lda #1
	plp
	beq L_022
	lda #0
L_022
	cmp.w #1
	beq L_006
	jmp L_005
L_006
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

S_016 .str "*** ERROR:  number < 0"
S_007 .str "Enter new number (0 to quit): "
F_020 .flt 1.000000e-06
F_011 .flt 0.000000e+00
_bss_start .byt 0
number_002 .flt 0
root_003 .flt 0
sqroot_004 .flt 0
_bss_end .byt 0
_stk .byt 0[1023]
_stk_top .byt -1

	.end
