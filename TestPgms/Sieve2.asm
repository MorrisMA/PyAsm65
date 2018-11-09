;    1: PROGRAM eratosthenes(output);
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
	lda.w #1000
	pha.w
	lda #2
	pha.w
	jsr _idiv
	adj #4
	sta.w limit_005
;   12:     sieve[1] := FALSE;
	psh.w #sieve_002
	lda #1
	dec.w a
	asl.w a
	clc
	adc.w 1,S
	sta.w 1,S
	lda #0
	pli.s
	sta.w 0,I++
;   13: 
;   14:     FOR i := 2 TO max DO
	lda #2
	sta.w i_003
L_008
	lda.w #1000
	cmp.w i_003
	bge L_009
	jmp L_010
L_009
;   15:         sieve[i] := TRUE;
	psh.w #sieve_002
	lda.w i_003
	dec.w a
	asl.w a
	clc
	adc.w 1,S
	sta.w 1,S
	lda #1
	pli.s
	sta.w 0,I++
	inc.w i_003
	jmp L_008
L_010
	dec.w i_003
;   16: 
;   17:     prime := 1;
	lda #1
	sta.w prime_006
;   18: 
;   19:     REPEAT
L_011
;   20:         prime := prime + 1;
	lda.w prime_006
	pha.w
	lda #1
	clc
	adc.w 1,S
	adj #2
	sta.w prime_006
;   21:         WHILE NOT sieve[prime] DO
L_013
	psh.w #sieve_002
	lda.w prime_006
	dec.w a
	asl.w a
	clc
	adc.w 1,S
	sta.w 1,S
	pli.s
	lda.w 0,I++
	eor #1
	cmp.w #1
	beq L_014
	jmp L_015
L_014
;   22:             prime := prime + 1;
	lda.w prime_006
	pha.w
	lda #1
	clc
	adc.w 1,S
	adj #2
	sta.w prime_006
	jmp L_013
L_015
;   23: 
;   24:         factor := 2*prime;
	lda #2
	pha.w
	lda.w prime_006
	pha.w
	jsr _imul
	adj #4
	sta.w factor_007
;   25: 
;   26:         WHILE factor <= max DO BEGIN
L_016
	lda.w factor_007
	pha.w
	lda.w #1000
	xma.w 1,S
	cmp.w 1,S
	adj #2
	php
	lda #1
	plp
	ble L_019
	lda #0
L_019
	cmp.w #1
	beq L_017
	jmp L_018
L_017
;   27:             sieve[factor] := FALSE;
	psh.w #sieve_002
	lda.w factor_007
	dec.w a
	asl.w a
	clc
	adc.w 1,S
	sta.w 1,S
	lda #0
	pli.s
	sta.w 0,I++
;   28:             factor := factor + prime;
	lda.w factor_007
	pha.w
	lda.w prime_006
	clc
	adc.w 1,S
	adj #2
	sta.w factor_007
;   29:         END
;   30:     UNTIL prime > limit;
	jmp L_016
L_018
	lda.w prime_006
	pha.w
	lda.w limit_005
	xma.w 1,S
	cmp.w 1,S
	adj #2
	php
	lda #1
	plp
	bgt L_020
	lda #0
L_020
	cmp.w #1
	beq L_012
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
	jmp L_026
L_025
;   38:             prime := i + j;
	lda.w i_003
	pha.w
	lda.w j_004
	clc
	adc.w 1,S
	adj #2
	sta.w prime_006
;   39:             IF sieve[prime] THEN
	psh.w #sieve_002
	lda.w prime_006
	dec.w a
	asl.w a
	clc
	adc.w 1,S
	sta.w 1,S
	pli.s
	lda.w 0,I++
	cmp.w #1
	beq L_027
	jmp L_028
L_027
;   40:                 write(prime:3)
	lda.w prime_006
	pha.w
	lda #3
	pha.w
	jsr _iwrite
	adj #4
;   41:             ELSE
	jmp L_029
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
	jmp L_024
L_026
	dec.w j_004
;   44:         writeln;
	jsr _writeln
;   45:         i := i + 20
	lda.w i_003
	pha.w
	lda #20
;   46:     UNTIL i > max
	clc
	adc.w 1,S
	adj #2
	sta.w i_003
	lda.w i_003
	pha.w
;   47: END.
	lda.w #1000
	xma.w 1,S
	cmp.w 1,S
	adj #2
	php
	lda #1
	plp
	bgt L_031
	lda #0
L_031
	cmp.w #1
	beq L_023
	jmp L_022
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
_bss_start .byt 1
sieve_002 .byt 2000
i_003 .wrd 1
j_004 .wrd 1
limit_005 .wrd 1
prime_006 .wrd 1
factor_007 .wrd 1
_bss_end .byt 1
_stk .byt 1023
_stk_top .byt 1

	.end
