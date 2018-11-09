; put integer to output
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
            .end
