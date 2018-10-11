;   unsigned division 16 x 16
        .cod 512
_idiv   .proc
        lda #0          ; clear remainder (A)
        dup a           ; push 
        lda.w 5,S       ; load dividend (Q)
        ldy #16         ; bit counter
_idiv_Lp    
        clc
        asl.w a         ; shift AQ left
        swp a
        rol.w a
        bcs _idiv_Plus  ; if A < 0 then A = A + M else A = A - M
_idiv_Minus
        sec
        sbc.w 3,S       ; subtract divisor (M)
        bra _idiv_Next
_idiv_Plus
        clc
        adc.w 3,S       ; add divisor (M)
_idiv_Next    
        swp a           ; restore order of Acc stack {Q, A, -}
        bmi _idiv_Dec   ; if A < 0 then Q[0] = 0 else Q[0] = 1
        inc.w a
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
        rts
        .endp
        .end
