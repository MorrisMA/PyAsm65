;
;   (+LOOP) Test Program: X - RSP, S - PSP. Standard 6502 Stack Pointers
;
        .cod    512
;
PPLOOP  .proc
;
        pla.w               ; Pull increment from PS
;
        clc                 ; Prepare to add increment to loop index
        bpl     PL1         ; if(increment > 0) test = final - index - 1
;
        adc.w   1,X         ; Add increment to loop index
        sta.w   1,X
;
        clc                 ; test = index - final - 1 (negative increment)
        lda.w   1,X
        sbc.w   3,X
        bra     PL2         ; check if loop complete
;
PL1     adc.w   1,X         ; Add increment to loop index
        sta.w   1,X
;
        clc                 ; test = final - index - 1 (positive increment)
        lda.w   3,X
        sbc.w   1,X
;
PL2     bpl     BRANCH      ; Loop if Loop Cntr <= Loop Termination
        adj.s   #4          ; Remove loop variables from RS
;
        ini                 ; Skip branch offset in thread
        ini
;
        brk                 ; NEXT
;
BRANCH  tia
;
        clc
        adc.w   0,I++
;
        tai
;
        brk                 ; NEXT
;
Stack   .equ    36
NewLine .equ    10
;
Byte    .byt    1 | 0x80 [8]
        .byt    [Stack]
        .byt    -1 [8]
        .byt    7, 6, 5, 4, 3, 2, 1, 0 | 0x80
Word    .wrd    PPLOOP, PL1, PL2, BRANCH
Long    .lng    0x78563412
        .byt    10, "ABT, Inc.", NewLine, -1
        .endp
        .end
