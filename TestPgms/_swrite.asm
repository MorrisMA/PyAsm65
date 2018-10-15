; put string to output
            .cod
;
_sPtrOff    .equ    7
_sLenOff    .equ    3
_putChar    .equ    0xF001
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
            .end
