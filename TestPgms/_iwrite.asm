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
            psh.w #5                ; load digit iteration count
            lda.w _iValOff,X        ; load a with integer value
; 
_iwrite_Lp
            pha.w                   ; push dividend argument to _udiv
            psh.w #10               ; push divisor argument to _udiv
            csr _udiv               ; determine the remainder,
            adj #4                  ; remove arguments passed to _udiv from stk
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
;
            tsa.w                   ; transfer current stk pointer to A
            inc.w a                 ; remove stack pointer write bias
;
            pha.w                   ; push string pointer to stack
            psh.w #0                ; NULL argument
            psh.w #5                ; push max length of integer value string
            csr _swrite             ; write integer value string using _swrite()
            adj #6                  ; remove parameters to _swrite() from stack
;
            txs.w                   ; deallocate stack variables
            plx.w                   ; restore previous base pointer
            rts
;
            .endp _iwrite
            .end
