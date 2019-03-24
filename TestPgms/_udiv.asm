;
;   unsigned division 16 x 16
;
            .cod
;
_Q          .equ    5
_D          .equ    3
;
_udiv       .proc
            lda #0          ; clear remainder (A)
            dup a           ; push 
            lda.w _Q,S      ; load dividend (Q)
            ldy #16         ; bit counter
;
_udiv_Lp    
            clc
            asl.w a         ; shift AQ left
            swp a
            rol.w a
;
            bcs _udiv_Plus  ; if A < 0 then A = A + D else A = A - D
;
_udiv_Minus
            sec
            sbc.w _D,S      ; subtract divisor (D)
;
            bra _udiv_Next
;
_udiv_Plus
            clc
            adc.w _D,S      ; add divisor (D)
;
_udiv_Next    
            swp a           ; restore order of Acc stack {Q, A, -}
            bmi _udiv_Dec   ; if A < 0 then Q[0] = 0 else Q[0] = 1
            inc.w a
;
_udiv_Dec
            dey             ; loop until loop counter == 0
            bne _udiv_Lp
;
_udiv_Exit
            swp a           ; Test remainder
            ora.w #0
            bpl _udiv_Finish
            clc
            adc.w _D,S
;
_udiv_Finish
            swp a
;
            rts
;
            .endp _udiv
            .end
