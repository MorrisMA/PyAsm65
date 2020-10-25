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
