    .cod    512
;
;   Setup
;
    psh.w #128
    stz.w 0x80
    stz.w 0x00
    lda.w #512
    ldy.w 0o1000
    sec
;
;   Instruction Under Test
;
    sbc.yw ((1,S)),A
;
    .end
