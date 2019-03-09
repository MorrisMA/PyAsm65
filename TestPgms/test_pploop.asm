;
;   (+LOOP) Test Program: X - RSP, S - PSP. Standard 6502 Stack Pointers
;
        .cod    512
;
PPLOOP  .proc
;
        pla.w               ; Pull increment from PS
        tay.w               ; Save value for test
;
        clc                 ; Increment loop index on PS
        adc.w   1,X
        sta.w   1,X
;
        tya.w               ; Check polarity increment
        bpl     PL1         ; if(increment > 0) test = final - index - 1
;
        clc                 ; else test = index - final - 1
        lda.w   1,X
        sbc.w   3,X
        bra     PL2         ; check if loop complete
;
PL1     
        clc                 ; Compare Loop Termination with Counter
        lda.w   3,X
        sbc.w   1,X
;
PL2     
        bpl     BRANCH      ; Loop if Loop Cntr <= Loop Termination
        adj.s   #4          ; Remove loop variables from RS
;
        ini                 ; Skip branch offset in thread
        ini
;
        brk                 ; NEXT
;
BRANCH
        tia
;
        clc
        adc.w   0,I++
;
        tai
;
        brk                 ; NEXT
;
        .endp
        .end
