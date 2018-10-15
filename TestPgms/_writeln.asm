; put <newLine> to output
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
            .end
