;
;                        Through the courtesy of
;
;                         FORTH INTEREST GROUP
;                            P.O. BOX  2154
;                         OAKLAND, CALIFORNIA
;                                94621
;
;
;                             Release 1.k0010
;
;                        with compiler security
;                                  and
;                        variable length names
;
;    Further distribution need not include this notice.
;    The FIG installation Manual is required as it contains
;    the model of FORTH and glossary of the system.
;    Might be available from FIG at the above address for 0x95.00 postpaid.
;
;    Translated from the FIG model by W.F. Ragsdale with input-
;    output given for the Rockwell System-65. Transportation to
;    other systems requires only the alteration of :
;                 XEMIT, XKEY, XQTER, XCR, AND RSLW
;
;    Equates giving memory assignments, machine
;    registers, and disk parameters.
;
SSIZE           .equ     128               ;sector size in bytes
NBUF            .equ     8                 ;number of buffers desired in RAM
;                             (SSIZE*NBUF >.equ 1024 bytes)
SECTR           .equ     800               ;sector per drive
;                              forcing high drive to zero
SECTL           .equ     1600              ;sector limit for two drives
;                              of 800 per drive.
BMAG            .equ     1056              ;total buffer magnitude, in bytes
;                              expressed by SSIZE+4*NBUF
;
BOS             .equ     0x20              ;bottom of data stack, in zero-page.
TOS             .equ     0xA0              ;top of data stack, in zero-page.
N               .equ     TOS+8             ;scratch workspace.
IP              .equ     N+8               ;interpretive pointer.
W               .equ     IP+3              ;code field pointer.
UP              .equ     W+2               ;user area pointer.
XSAVE           .equ     UP+2              ;temporary for X register.
;
TIBX            .equ     0x0100             ;terminal input buffer of 84 bytes.
ORIG            .equ     0x0400             ;origin of FORTH's Dictionary.
MEM             .equ     0x4000             ;top of assigned memory+1 byte.
UAREA           .equ     MEM-128           ;128 bytes of user area
DAREA           .equ     UAREA-BMAG        ;disk buffer space.
;
;         Monitor calls for terminal support
;
;cin             .equ    0xf818          ; input one ascii char. to term.
;cout            .equ    0xf82d          ; output one ascii char. to term.
;crout           .equ    0xf8a2          ; terminal return and line feed.
;
;    From DAREA downward to the top of the dictionary is free
;    space where the user's applications are compiled.
;
;    Boot up parameters. This area provides jump vectors
;    to Boot up  code, and parameters describing the system.
;
                .code  ORIG             ; User cold entry point
ENTER           nop                     ; Vector to COLD entry
                jmp   COLD+2            ;
REENTR          nop                     ; User Warm entry point
                jmp   WARM              ; Vector to WARM entry
                .wrd  0x0004            ; 6502 in radix-36
                .wrd  0x5ED2            ;
                .wrd  NTOP              ; Name address of MON
;                .wrd  0x7F               ;Backspace Character
                .wrd  0x08              ; Backspace Character
                .wrd  UAREA             ; Initial User Area
                .wrd  TOS-1             ; Initial Top of Stack
                .wrd  0x1FF             ; Initial Top of Return Stack
                .wrd  TIBX              ; Initial terminal input buffer
;
;
                .wrd  31                ; Initial name field width
                .wrd  1                 ; 0.equnod disk, 1.equdisk
                .wrd  TOP               ; Initial fence address
                .wrd  TOP               ; Initial top of dictionary
                .wrd  VL0               ; Initial Vocabulary link ptr.
;
;
;    The following offset adjusts all code fields to avoid an
;    address ending 0xXXFF. This must be checked and altered on
;    any alteration , for the indirect jump at W-1 to operate !
;
                nop
                nop
;
;   Utility routines to send and receive char from console
;
cin             lda     0xF004          ; input one ascii char. to term.
                beq     cin
                rts
cout            and     #0x7F           ; output one ascii char. to term.
                sta     0xF001
                rts
crout           lda     #0x0A           ; terminal return and line feed.
                sta     0xF001
                rts
;
;                                       LIT
;                                       SCREEN 13 LINE 1
;
L22             .byt  0x83,"LI",0xD4      ; <--- name field
                .wrd  00                ; <----- link field, last marked by zero
LIT             .wrd  $+2               ; <----- code address field
                lda   (IP),y            ; <----- start of parameter field
                pha
                inc   IP
                bne   L30
                inc   IP+1
L30             lda   (IP),y
L31             inc   IP
                bne   PUSH
                inc   IP+1
;
PUSH            dex
                dex
;
PUT             sta   1,x
                pla
                sta   0,x
;
;    NEXT is the address interpreter that moves from machine
;    level word to word.
;
NEXT            ldy   #1
                lda   (IP),y            ;Fetch code field address pointed
                sta   W+1               ;to by IP.
                dey
                lda   (IP),y
                sta   W
;
                clc                     ;Increment IP by two.
                lda   IP
                adc   #2
                sta   IP
                bcc   L54
                inc   IP+1
L54             jmp   W-1               ;Jump to an indirect jump (W) which
;                        vectors to code pointed to by a code
;                        field.
;
;    CLIT pushes the next inline byte to data stack
;
L35             .byt  0x84,"CLI",0xD4
                .wrd  L22               ;Link to LIT
CLIT            .wrd  $+2
                lda   (IP),y
                pha
                tya
                beq   L31               ;a forced branch into LIT

;
;
SETUP           asl   a
                sta   N-1
L63             lda   0,x
                sta   N,y
                inx
                iny
                cpy   N-1
                bne   L63
                ldy   #0
                rts
;
;                                       EXCECUTE
;                                       SCREEN 14 LINE 11
;
L75             .byt  0x87,"EXECUT",0xC5
                .wrd  L35               ;link to CLIT
EXEC            .wrd  $+2
                lda   0,x
                sta   W
                lda   1,x
                sta   W+1
                inx
                inx
                jmp   W-1               ;to JMP (W) in z-page
;
;                                       BRANCH
;                                       SCREEN 15 LINE 11
;
L89             .byt  0x86,"BRANC",0xC8
                .wrd  L75               ;link to EXCECUTE
BRAN            .wrd  $+2
                clc
                lda   (IP),y
                adc   IP
                pha
                iny
                lda   (IP),y
                adc   IP+1
                sta   IP+1
                pla
                sta   IP
                jmp   NEXT+2
;
;                                       0BRANCH
;                                       SCREEN 15 LINE 6
;
L107            .byt  0x87,"0BRANC",0xC8
                .wrd  L89               ;link to BRANCH
ZBRAN           .wrd  $+2
                inx
                inx
                lda   0xFE,x
                ora   0xFF,x
                beq   BRAN+2
;
BUMP            clc
                lda   IP
                adc   #2
                sta   IP
                bcc   L122
                inc   IP+1
L122            jmp   NEXT
;
;                                       (LOOP)
;                                       SCREEN 16 LINE 1
;
L127            .byt  0x86,"(LOOP",0xA9
                .wrd  L107              ;link to 0BRANCH
PLOOP           .wrd  L130
L130            stx   XSAVE
                tsx
                inc   0x101,x
                bne   PL1
                inc   0x102,x
;
PL1             clc
                lda   0x103,x
                sbc   0x101,x
                lda   0x104,x
                sbc   0x102,x
;
PL2             ldx   XSAVE
                asl   a
                bcc   BRAN+2
                pla
                pla
                pla
                pla
                jmp   BUMP
;
;                                       (+LOOP)
;                                       SCREEN 16 LINE 8
;
L154            .byt  0x87,"(+LOOP",0xA9
                .wrd  L127              ;link to (loop)
PPLOO           .wrd  $+2
                inx
                inx
                stx   XSAVE
                lda   0xFF,x
                pha
                pha
                lda   0xFE,x
                tsx
                inx
                inx
                clc
                adc   0x101,x
                sta   0x101,x
                pla
                adc   0x102,x
                sta   0x102,x
                pla
                bpl   PL1
                clc
                lda   0x101,x
                sbc   0x103,x
                lda   0x102,x
                sbc   0x104,x
                jmp   PL2
;
;                                       (DO)
;                                       SCREEN 17 LINE 2
;
L185            .byt  0x84,"(DO",0xA9
                .wrd  L154              ;link to (+LOOP)
PDO             .wrd  $+2
                lda   3,x
                pha
                lda   2,x
                pha
                lda   1,x
                pha
                lda   0,x
                pha
;
POPTWO          inx
                inx
;
;
;
POP             inx
                inx
                jmp   NEXT
;
;                                       I
;                                       SCREEN 17 LINE 9
;
L207            .byt  0x81,0xC9
                .wrd  L185              ;link to (DO)
I               .wrd  R+2               ;share the code for R
;
;                                       DIGIT
;                                       SCREEN 18 LINE 1
;
L214            .byt  0x85,"DIGI",0xD4
                .wrd  L207              ;link to I
DIGIT           .wrd  $+2
                sec
                lda   2,x
                sbc   #0x30
                bmi   L234
                cmp   #0xA
                bmi   L227
                sec
                sbc   #7
                cmp   #0xA
                bmi   L234
L227            cmp   0,x
                bpl   L234
                sta   2,x
                lda   #1
                pha
                tya
                jmp   PUT               ;exit true with converted value
L234            tya
                pha
                inx
                inx
                jmp   PUT               ;exit false with bad conversion
;
;                                       (FIND)
;                                       SCREEN 19 LINE 1
;
L243            .byt  0x86,"(FIND",0xA9
                .wrd  L214              ;Link to DIGIT
PFIND           .wrd  $+2
                lda   #2
                jsr   SETUP
                stx   XSAVE
L249            ldy   #0
                lda   (N),y
                eor   (N+2),y
;
;
                and   #0x3F
                bne   L281
L254            iny
                lda   (N),y
                eor   (N+2),y
                asl   a
                bne   L280
                bcc   L254
                ldx   XSAVE
                dex
                dex
                dex
                dex
                clc
                tya
                adc   #5
                adc   N
                sta   2,x
                ldy   #0
                tya
                adc   N+1
                sta   3,x
                sty   1,x
                lda   (N),y
                sta   0,x
                lda   #1
                pha
                jmp   PUSH
L280            bcs   L284
L281            iny
                lda   (N),y
                bpl   L281
L284            iny
                lda   (N),y
                tax
                iny
                lda   (N),y
                sta   N+1
                stx   N
                ora   N
                bne   L249
                ldx   XSAVE
                lda   #0
                pha
                jmp   PUSH              ;exit false upon reading null link
;
;                                       ENCLOSE
;                                       SCREEN 20 LINE 1
;
L301            .byt  0x87,"ENCLOS",0xC5
                .wrd  L243              ;link to (FIND)
ENCL            .wrd  $+2
                lda   #2
                jsr   SETUP
                txa
                sec
                sbc   #8
                tax
                sty   3,x
                sty   1,x
                dey
L313            iny
                lda   (N+2),y
                cmp   N
                beq   L313
                sty   4,x
L318            lda   (N+2),y
                bne   L327
                sty   2,x
                sty   0,x
                tya
                cmp   4,x
                bne   L326
                inc   2,x
L326            jmp   NEXT
L327            sty   2,x
                iny
                cmp   N
                bne   L318
                sty   0,x
                jmp   NEXT
;
;                                       EMIT
;                                       SCREEN 21 LINE 5
;
L337            .byt  0x84,"EMI",0xD4
                .wrd  L301              ;link to ENCLOSE
EMIT            .wrd  XEMIT             ;Vector to code for KEY
;
;                                       KEY
;                                       SCREEN 21 LINE 7
;
L344            .byt  0x83,"KE",0xD9
                .wrd  L337              ;link to EMIT
KEY             .wrd  XKEY              ;Vector to code for KEY
;
;                                       ?TERMINAL
;                                       SCREEN 21 LINE 9
;
L351            .byt  0x89,"?TERMINA",0xCC
                .wrd  L344              ;link to KEY
QTERM           .wrd  XQTER             ;Vector to code for ?TERMINAL
;
;
;
;
;
;                                       CR
;                                       SCREEN 21 LINE 11
;
L358            .byt  0x82,"C",0xD2
                .wrd  L351              ;link to ?TERMINAL
CR              .wrd  XCR               ;Vector to code for CR
;
;                                       CMOVE
;                                       SCREEN 22 LINE 1
;
L365            .byt  0x85,"CMOV",0xC5
                .wrd  L358              ;link to CR
CMOVE           .wrd  $+2
                lda   #3
                jsr   SETUP
L370            cpy   N
                bne   L375
                dec   N+1
                bpl   L375
                jmp   NEXT
L375            lda   (N+4),y
                sta   (N+2),y
                iny
                bne   L370
                inc   N+5
                inc   N+3
                jmp   L370
;
;                                       U*
;                                       SCREEN 23 LINE 1
;
L386            .byt  0x82,"U",0xAA
                .wrd  L365              ;link to CMOVE
USTAR           .wrd  $+2
;          LDA 2,X
;          STA N
;          STY 2,X
;          LDA 3,X
;          STA N+1
;          STY 3,X
;          LDY #16        ; for 16 bits
;L396      ASL 2,X
;          ROL 3,X
;          ROL 0,X
;          ROL 1,X
;          BCC L411
;          CLC
;          LDA N
;          ADC 2,X
;          STA 2,X
;          LDA N+1
;          ADC 3,X
;          STA 3,X
;          LDA #0        ; bug here as high byte of this high word does not
;          ADC 0,X       ; get incremented when 0,x rolls over to 0x00
;          STA 0,X
;
;L411      DEY
;          BNE L396
;          JMP NEXT

;
; replacement code from 6502.org - http://forum.6502.org/viewtopic.php?t.equ689
;
                lda   #0                ;in some implementations TYA can be used since NEXT leaves Y.equ0x00
                sta   N
                ldy   #16
                lsr   3,x
                ror   2,x
L1              bcc   L2
                clc
                sta   N+1               ;PHA
                lda   N
                adc   0,x
                sta   N
                lda   N+1               ;PLA
                adc   1,x
L2              ror   a
                ror   N
                ror   3,x
                ror   2,x
                dey
                bne   L1
                sta   1,x
                lda   N
                sta   0,x
                jmp   NEXT

;
;                                       U/
;                                       SCREEN 24 LINE 1
;
L418            .byt  0x82,"U",0xAF
                .wrd  L386              ;link to U*
USLAS           .wrd  $+2
;          LDA 4,X   ; bugged code replaced - dr
;          LDY 2,X
;          STY 4,X
;          ASL
;          STA 2,X
;          LDA 5,X
;          LDY 3,X
;          STY 5,X
;          ROL
;          STA 3,X
;          LDA #16
;          STA N
;L433      ROL 4,X
;          ROL 5,X
;          SEC
;          LDA 4,X
;          SBC 0,X
;          TAY
;          LDA 5,X
;          SBC 1,X
;          BCC L444
;          STY 4,X
;          STA 5,X
;L444      ROL 2,X
;          ROL 3,X
;          DEC N
;          BNE L433
;          JMP POP

;
; updated code from 6502.org  - source code repository 32bit division
;
                sec                     ;Modified code - dr
                lda   2,x               ;Subtract hi cell of dividend by
                sbc   0,x               ;divisor to see if there's an overflow condition.
                lda   3,x
                sbc   1,x
                bcs   oflow             ;Branch if /0 or overflow.
                lda   #0x11              ;Loop 17x.
                sta   N                 ;Use N for loop counter.
loopp           rol   4,x               ;Rotate dividend lo cell left one bit.
                rol   5,x
                dec   N                 ;Decrement loop counter.
                beq   endd              ;If we're done, then branch to end.
                rol   2,x               ;Otherwise rotate dividend hi cell left one bit.
                rol   3,x
;                stz   N+1
                pha
                lda #0
                sta N+1
                pla
;
                rol   N+1               ;Rotate the bit carried out of above into N+1.
                sec
                lda   2,x               ;Subtract dividend hi cell minus divisor.
                sbc   0,x
                sta   N+2               ;Put result temporarily in N+2 (lo byte)
                lda   3,x
                sbc   1,x
                tay                     ;and Y (hi byte).
                lda   N+1               ;Remember now to bring in the bit carried out above.
                sbc   #0x00
                bcc   loopp
                lda   N+2               ;If that didn't cause a borrow,
                sta   2,x               ;make the result from above to
                sty   3,x               ;be the new dividend hi cell
                bcs   loopp             ;and then brach up.  (NMOS 6502 can use BCS here.)
oflow           lda   #0xFF              ;If overflow or /0 condition found,
                sta   2,x               ;just put FFFF in both the remainder
                sta   3,x
                sta   4,x               ;and the quotient.
                sta   5,x
endd            inx                     ;When you're done, show one less cell on data stack,
                inx                     ;(INX INX is exactly what the Forth word DROP does)
                jmp   SWAP+2            ;and swap the two top cells to put quotient on top.

;
;                                       AND
;                                       SCREEN 25 LINE 2
;
L453            .byt  0x83,"AN",0xC4
                .wrd  L418              ;link to U/
ANDD            .wrd  $+2
                lda   0,x
                and   2,x
                pha
                lda   1,x
                and   3,x
;
BINARY          inx
                inx
                jmp   PUT
;
;                                       OR
;                                       SCREEN 25 LINE 7
;
L469            .byt  0x82,"O",0xD2
                .wrd  L453              ;link to AND
OR              .wrd  $+2
                lda   0,x
                ora   2,x
                pha
                lda   1,x
                ora   3,x
                inx
                inx
                jmp   PUT
;
;                                       XOR
;                                       SCREEN 25 LINE 11
;
L484            .byt  0x83,"XO",0xD2
                .wrd  L469              ;link to OR
XOR             .wrd  $+2
                lda   0,x
                eor   2,x
                pha
                lda   1,x
                eor   3,x
                inx
                inx
                jmp   PUT
;
;                                       SP@
;                                       SCREEN 26 LINE 1
;
L499            .byt  0x83,"SP",0xC0
                .wrd  L484              ;link  to XOR
SPAT            .wrd  $+2
                txa
;
PUSHOA          pha
                lda   #0
                jmp   PUSH
;
;                                       SP!
;                                       SCREEN 26 LINE 5
;
;
L511            .byt  0x83,"SP",0xA1
                .wrd  L499              ;link to SP@
SPSTO           .wrd  $+2
                ldy   #6
                lda   (UP),y            ;load data stack pointer (X reg) from
                tax                     ;silent user variable S0.
                jmp   NEXT
;
;                                       RP!
;                                       SCREEN 26 LINE 8
;
L522            .byt  0x83,"RP",0xA1
                .wrd  L511              ;link to SP!
RPSTO           .wrd  $+2
                stx   XSAVE             ;load return stack pointer (machine
                ldy   #8                ;stack pointer) from silent user
                lda   (UP),y            ;VARIABLE R0
                tax
                txs
                ldx   XSAVE
                jmp   NEXT
;
;                                       ;S
;                                       SCREEN 26 LINE 12
;
L536            .byt  0x82,";",0xD3
                .wrd  L522              ;link to RP!
SEMIS           .wrd  $+2
                pla
                sta   IP
                pla
                sta   IP+1
                jmp   NEXT
;
;                                       LEAVE
;                                       SCREEN 27 LINE  1
;
L548            .byt  0x85,"LEAV",0xC5
                .wrd  L536              ;link to ;S
LEAVE           .wrd  $+2
                stx   XSAVE
                tsx
                lda   0x101,x
                sta   0x103,x
                lda   0x102,x
                sta   0x104,x
                ldx   XSAVE
                jmp   NEXT
;
;                                       >R
;                                       SCREEN 27 LINE 5
;
L563            .byt  0x82,">",0xD2
                .wrd  L548              ;link to LEAVE
TOR             .wrd  $+2
                lda   1,x               ;move high byte
                pha
                lda   0,x               ;then low byte
                pha                     ;to return stack
                inx
                inx                     ;popping off data stack
                jmp   NEXT
;
;                                       R>
;                                       SCREEN 27 LINE 8
;
L577            .byt  0x82,"R",0xBE
                .wrd  L563              ;link to >R
RFROM           .wrd  $+2
                dex                     ;make room on data stack
                dex
                pla                     ;high byte
                sta   0,x
                pla                     ;then low byte
                sta   1,x               ;restored to data stack
                jmp   NEXT
;
;                                       R
;                                       SCREEN 27 LINE 11
;
L591            .byt  0x81,0xD2
                .wrd  L577              ;link to R>
R               .wrd  $+2
                stx   XSAVE
                tsx                     ;address return stack
                lda   0x101,x            ;copy bottom value
                pha                     ;to data stack
                lda   0x102,x
                ldx   XSAVE
                jmp   PUSH
;
;                                       0.equ
;                                       SCREEN 28 LINE 2
;
L605            .byt  0x82,"0",0xBD
                .wrd  L591              ;link to R
ZEQU            .wrd  $+2
                lda   1,x               ;Corrected from FD3/2 p69
                sty   1,x
                ora   0,x
                bne   L613
                iny
L613            sty   0,x
                jmp   NEXT
;
;                                       0<
;                                       SCREEN 28 LINE 6
;
L619            .byt  0x82,"0",0xBC
                .wrd  L605              ;link to 0.equ
ZLESS           .wrd  $+2
                asl   1,x
                tya
                rol   a
                sty   1,x
                sta   0,x
                jmp   NEXT
;
;                                       +
;                                       SCREEN 29 LINE 1
;
L632            .byt  0x81,0xAB
                .wrd  L619              ;link to V-ADJ
PLUS            .wrd  $+2
                clc
                lda   0,x
                adc   2,x
                sta   2,x
                lda   1,x
                adc   3,x
                sta   3,x
                inx
                inx
                jmp   NEXT
;
;                                       D+
;                                       SCREEN 29 LINE 4
;
L649            .byt  0x82,"D",0xAB
                .wrd  L632              ;LINK TO +
DPLUS           .wrd  $+2
                clc
                lda   2,x
                adc   6,x
                sta   6,x
                lda   3,x
                adc   7,x
                sta   7,x
                lda   0,x
                adc   4,x
                sta   4,x
                lda   1,x
                adc   5,x
                sta   5,x
                jmp   POPTWO
;
;                                       MINUS
;                                       SCREEN 29 LINE 9
;
L670            .byt  0x85,"MINU",0xD3
                .wrd  L649              ;link to D+
MINUS           .wrd  $+2
                sec
                tya
                sbc   0,x
                sta   0,x
                tya
                sbc   1,x
                sta   1,x
                jmp   NEXT
;
;                                       DMINUS
;                                       SCREEN 29 LINE 12
;
L685            .byt  0x86,"DMINU",0xD3
                .wrd  L670              ;link to  MINUS
DMINU           .wrd  $+2
                sec
                tya
                sbc   2,x
                sta   2,x
                tya
                sbc   3,x
                sta   3,x
                jmp   MINUS+3
;
;                                       OVER
;                                       SCREEN 30 LINE 1
;
L700            .byt  0x84,"OVE",0xD2
                .wrd  L685              ;link to DMINUS
OVER            .wrd  $+2
                lda   2,x
                pha
                lda   3,x
                jmp   PUSH
;
;                                       DROP
;                                       SCREEN 30 LINE 4
;
L711            .byt  0x84,"DRO",0xD0
                .wrd  L700              ;link to OVER
DROP            .wrd  POP
;
;                                       SWAP
;                                       SCREEN 30 LINE 8
;
L718            .byt  0x84,"SWA",0xD0
                .wrd  L711              ;link to DROP
SWAP            .wrd  $+2
                lda   2,x
                pha
                lda   0,x
                sta   2,x
                lda   3,x
                ldy   1,x
                sty   3,x
                jmp   PUT
;
;                                       DUP
;                                       SCREEN 30 LINE 21
;
L733            .byt  0x83,"DU",0xD0
                .wrd  L718              ;link to SWAP
DUP             .wrd  $+2
                lda   0,x
                pha
                lda   1,x
                jmp   PUSH
;
;                                       +!
;                                       SCREEN 31 LINE 2
;
L744            .byt  0x82,"+",0xA1
                .wrd  L733              ;link to DUP
PSTOR           .wrd  $+2
                clc
                lda   (0,x)             ;fetch 16 bit value addressed by
                adc   2,x               ;bottom of  stack, adding to
                sta   (0,x)             ;second item on stack, and return
                inc   0,x               ;to memory
                bne   L754
                inc   1,x
L754            lda   (0,x)
                adc   3,x
                sta   (0,x)
                jmp   POPTWO
;
;                                       TOGGLE
;                                       SCREEN 31 LINE 7
;
L762            .byt  0x81,"TOGGL",0xC5
                .wrd  L744              ;link to +!
TOGGL           .wrd  $+2
                lda   (2,x)             ;complement bits in memory address
                eor   0,x               ;second on stack, by pattern on
                sta   (2,x)             ;bottom of stack.
                jmp   POPTWO
;
;                                       @
;                                       SCREEN 32 LINE 1
;
L773            .byt  0x81,0xC0
                .wrd  L762              ;link to TOGGLE
AT              .wrd  $+2
                lda   (0,x)
                pha
                inc   0,x
                bne   L781
                inc   1,x
L781            lda   (0,x)
                jmp   PUT
;
;                                       C@
;                                       SCREEN 32 LINE 5
;
L787            .byt  0x82,"C",0xC0
                .wrd  L773              ;link to @
CAT             .wrd  $+2
                lda   (0,x)             ;fetch byte addressed by bottom of
                sta   0,x               ;stack to stack, zeroing the high
                sty   1,x               ;byte
                jmp   NEXT
;
;                                       !
;                                       SCREEN 32 LINE 8
;
L798            .byt  0x81,0xA1
                .wrd  L787              ;link to C@
STORE           .wrd  $+2
                lda   2,x
                sta   (0,x)             ;store second 16bit value on stack
                inc   0,x               ;to memory as addressed by bottom
                bne   L806              ;of stack.
                inc   1,x
L806            lda   3,x
                sta   (0,x)
                jmp   POPTWO
;
;                                       C!
;                                       SCREEN 32 LINE 12
;
L813            .byt  0x82,"C",0xA1
                .wrd  L798              ;link to !
CSTOR           .wrd  $+2
                lda   2,x
                sta   (0,x)
                jmp   POPTWO
;
;                                       :
;                                       SCREEN 33 LINE 2
;
L823            .byt  0xC1,0xBA
                .wrd  L813              ;link to C!
COLON           .wrd  DOCOL
                .wrd  QEXEC
                .wrd  SCSP
                .wrd  CURR
                .wrd  AT
                .wrd  CON
                .wrd  STORE
                .wrd  CREAT
                .wrd  RBRAC
                .wrd  PSCOD
;
DOCOL           lda   IP+1
                pha
                lda   IP
                pha
                clc
                lda   W
                adc   #2
                sta   IP
                tya
                adc   W+1
                sta   IP+1
                jmp   NEXT
;
;                                       ;
;                                       SCREEN 33 LINE 9
;
L853            .byt  0xC1,0xBB
                .wrd  L823              ;link to :
                .wrd  DOCOL
                .wrd  QCSP
                .wrd  COMP
                .wrd  SEMIS
                .wrd  SMUDG
                .wrd  LBRAC
                .wrd  SEMIS
;
;                                       CONSTANT
;                                       SCREEN 34 LINE 1
;
L867            .byt  0x88,"CONSTAN",0xD4
                .wrd  L853              ;link to ;
CONST           .wrd  DOCOL
                .wrd  CREAT
                .wrd  SMUDG
                .wrd  COMMA
                .wrd  PSCOD
;
DOCON           ldy   #2
                lda   (W),y
                pha
                iny
                lda   (W),y
                jmp   PUSH
;
;                                       VARIABLE
;                                       SCREEN 34 LINE 5
;
L885            .byt  0x88,"VARIABL",0xC5
                .wrd  L867              ;link to CONSTANT
VAR             .wrd  DOCOL
                .wrd  CONST
                .wrd  PSCOD
;
DOVAR           clc
                lda   W
                adc   #2
                pha
                tya
                adc   W+1
                jmp   PUSH
;
;                                       USER
;                                       SCREEN 34 LINE 10
;
L902            .byt  0x84,"USE",0xD2
                .wrd  L885              ;link to VARIABLE
USER            .wrd  DOCOL
                .wrd  CONST
                .wrd  PSCOD
;
DOUSE           ldy   #2
                clc
                lda   (W),y
                adc   UP
                pha
                lda   #0
                adc   UP+1
                jmp   PUSH
;
;                                       0
;                                       SCREEN 35 LINE 2
;
L920            .byt  0x81,0xB0
                .wrd  L902              ;link to USER
ZERO            .wrd  DOCON
                .wrd  0
;
;                                       1
;                                       SCREEN 35 LINE 2
;
L928            .byt  0x81,0xB1
                .wrd  L920              ;link to 0
ONE             .wrd  DOCON
                .wrd  1
;
;                                       2
;                                       SCREEN 35 LINE 3
;
L936            .byt  0x81,0xB2
                .wrd  L928              ;link to 1
TWO             .wrd  DOCON
                .wrd  2
;
;                                       3
;                                       SCREEN 35 LINE 3
;
L944            .byt  0x81,0xB3
                .wrd  L936              ;link to 2
THREE           .wrd  DOCON
                .wrd  3
;
;                                       BL
;                                       SCREEN 35 LINE 4
;
L952            .byt  0x82,"B",0xCC
                .wrd  L944              ;link to 3
BL              .wrd  DOCON
                .wrd  0x20
;
;                                       C/L
;                                       SCREEN 35 LINE 5
;                                       Characters per line
L960            .byt  0x83,"C/",0xCC
                .wrd  L952              ;link to BL
CSLL            .wrd  DOCON
                .wrd  64
;
;                                       FIRST
;                                       SCREEN 35 LINE 7
;
L968            .byt  0x85,"FIRS",0xD4
                .wrd  L960              ;link to C/L
FIRST           .wrd  DOCON
                .wrd  DAREA             ;bottom of disk buffer area
;
;                                       LIMIT
;                                       SCREEN 35 LINE 8
;
L976            .byt  0x85,"LIMI",0xD4
                .wrd  L968              ;link to FIRST
LIMIT           .wrd  DOCON
                .wrd  UAREA             ;buffers end at user area
;
;                                       B/BUF
;                                       SCREEN 35 LINE 9
;                                       Bytes per Buffer
;
L984            .byt  0x85,"B/BU",0xC6
                .wrd  L976              ;link to LIMIT
BBUF            .wrd  DOCON
                .wrd  SSIZE             ;sector size
;
;                                       B/SCR
;                                       SCREEN 35 LINE 10
;                                       Blocks per screen
;
L992            .byt  0x85,"B/SC",0xD2
                .wrd  L984              ;link to B/BUF
BSCR            .wrd  DOCON
                .wrd  8                 ;blocks to make one screen





;
;                                       +ORIGIN
;                                       SCREEN 35 LINE 12
;
L1000           .byt  0x87,"+ORIGI",0xCE
                .wrd  L992              ;link to B/SCR
PORIG           .wrd  DOCOL
                .wrd  LIT,ORIG
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       TIB
;                                       SCREEN 36 LINE 4
;
L1010           .byt  0x83,"TI",0xC2
                .wrd  L1000             ;link to +ORIGIN
TIB             .wrd  DOUSE
                .byt  0xA
;
;                                       WIDTH
;                                       SCREEN 36 LINE 5
;
L1018           .byt  0x85,"WIDT",0xC8
                .wrd  L1010             ;link to TIB
WIDTH           .wrd  DOUSE
                .byt  0xC
;
;                                       WARNING
;                                       SCREEN 36 LINE 6
;
L1026           .byt  0x87,"WARNIN",0xC7
                .wrd  L1018             ;link to WIDTH
WARN            .wrd  DOUSE
                .byt  0xE
;
;                                       FENCE
;                                       SCREEN 36 LINE 7
;
L1034           .byt  0x85,"FENC",0xC5
                .wrd  L1026             ;link to WARNING
FENCE           .wrd  DOUSE
                .byt  0x10
;
;
;                                       DP
;                                       SCREEN 36 LINE 8
;
L1042           .byt  0x82,"D",0xD0
                .wrd  L1034             ;link to FENCE
DP              .wrd  DOUSE
                .byt  0x12
;
;                                       VOC-LINK
;                                       SCREEN 36 LINE 9
;
L1050           .byt  0x88,"VOC-LIN",0xCB
                .wrd  L1042             ;link to DP
VOCL            .wrd  DOUSE
                .byt  0x14
;
;                                       BLK
;                                       SCREEN 36 LINE 10
;
L1058           .byt  0x83,"BL",0xCB
                .wrd  L1050             ;link to VOC-LINK
BLK             .wrd  DOUSE
                .byt  0x16
;
;                                       IN
;                                       SCREEN 36 LINE 11
;
L1066           .byt  0x82,"I",0xCE
                .wrd  L1058             ;link to BLK
IN              .wrd  DOUSE
                .byt  0x18
;
;                                       OUT
;                                       SCREEN 36 LINE 12
;
L1074           .byt  0x83,"OU",0xD4
                .wrd  L1066             ;link to IN
OUT             .wrd  DOUSE
                .byt  0x1A
;
;                                       SCR
;                                       SCREEN 36 LINE 13
;
L1082           .byt  0x83,"SC",0xD2
                .wrd  L1074             ;link to OUT
SCR             .wrd  DOUSE
                .byt  0x1C
;
;                                       OFFSET
;                                       SCREEN 37 LINE 1
;
L1090           .byt  0x86,"OFFSE",0xD4
                .wrd  L1082             ;link to SCR
OFSET           .wrd  DOUSE
                .byt  0x1E
;
;                                       CONTEXT
;                                       SCREEN 37 LINE 2
;
L1098           .byt  0x87,"CONTEX",0xD4
                .wrd  L1090             ;link to OFFSET
CON             .wrd  DOUSE
                .byt  0x20
;
;                                       CURRENT
;                                       SCREEN 37 LINE 3
;
L1106           .byt  0x87,"CURREN",0xD4
                .wrd  L1098             ;link to CONTEXT
CURR            .wrd  DOUSE
                .byt  0x22
;
;                                       STATE
;                                       SCREEN 37 LINE 4
;
L1114           .byt  0x85,"STAT",0xC5
                .wrd  L1106             ;link to CURRENT
STATE           .wrd  DOUSE
                .byt  0x24
;
;                                       BASE
;                                       SCREEN 37 LINE 5
;
L1122           .byt  0x84,"BAS",0xC5
                .wrd  L1114             ;link to STATE
BASE            .wrd  DOUSE
                .byt  0x26
;
;                                       DPL
;                                       SCREEN 37 LINE 6
;
L1130           .byt  0x83,"DP",0xCC
                .wrd  L1122             ;link to BASE
DPL             .wrd  DOUSE
                .byt  0x28
;
;                                       FLD
;                                       SCREEN 37 LINE 7
;
L1138           .byt  0x83,"FL",0xC4
                .wrd  L1130             ;link to DPL
FLD             .wrd  DOUSE
                .byt  0x2A
;
;
;
;                                       CSP
;                                       SCREEN 37 LINE 8
;
L1146           .byt  0x83,"CS",0xD0
                .wrd  L1138             ;link to FLD
CSP             .wrd  DOUSE
                .byt  0x2C
;
;                                       R#
;                                       SCREEN 37  LINE 9
;
L1154           .byt  0x82,"R",0xA3
                .wrd  L1146             ;link to CSP
RNUM            .wrd  DOUSE
                .byt  0x2E
;
;                                       HLD
;                                       SCREEN 37 LINE 10
;
L1162           .byt  0x83,"HL",0xC4
                .wrd  L1154             ;link to R#
HLD             .wrd  DOUSE
                .byt  0x30
;
;                                       1+
;                                       SCREEN 38 LINE  1
;
L1170           .byt  0x82,"1",0xAB
                .wrd  L1162             ;link to HLD
ONEP            .wrd  DOCOL
                .wrd  ONE
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       2+
;                                       SCREEN 38 LINE 2
;
L1180           .byt  0x82,"2",0xAB
                .wrd  L1170             ;link to 1+
TWOP            .wrd  DOCOL
                .wrd  TWO
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       HERE
;                                       SCREEN 38 LINE 3
;
L1190           .byt  0x84,"HER",0xC5
                .wrd  L1180             ;link to 2+
HERE            .wrd  DOCOL
                .wrd  DP
                .wrd  AT
                .wrd  SEMIS
;
;                                       ALLOT
;                                       SCREEN 38 LINE 4
;
L1200           .byt  0x85,"ALLO",0xD4
                .wrd  L1190             ;link to HERE
ALLOT           .wrd  DOCOL
                .wrd  DP
                .wrd  PSTOR
                .wrd  SEMIS
;
;                                       ,
;                                       SCREEN 38 LINE 5
;
L1210           .byt  0x81,0xAC
                .wrd  L1200             ;link to ALLOT
COMMA           .wrd  DOCOL
                .wrd  HERE
                .wrd  STORE
                .wrd  TWO
                .wrd  ALLOT
                .wrd  SEMIS
;
;                                       C,
;                                       SCREEN 38 LINE 6
;
L1222           .byt  0x82,"C",0xAC
                .wrd  L1210             ;link to ,
CCOMM           .wrd  DOCOL
                .wrd  HERE
                .wrd  CSTOR
                .wrd  ONE
                .wrd  ALLOT
                .wrd  SEMIS
;
;                                       -
;                                       SCREEN 38 LINE 7
;
L1234           .byt  0x81,0xAD
                .wrd  L1222             ;link to C,
SUB             .wrd  DOCOL
                .wrd  MINUS
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       =
;                                       SCREEN 38 LINE 8
;
L1244           .byt  0x81,0xBD
                .wrd  L1234             ;link to -
EQUAL           .wrd  DOCOL
                .wrd  SUB
                .wrd  ZEQU
                .wrd  SEMIS
;
;                                       U<
;                                       Unsigned less than
;
L1246           .byt  0x82,"U",0xBC
                .wrd  L1244             ;link to =
ULESS           .wrd  DOCOL
                .wrd  SUB               ;subtract two values
                .wrd  ZLESS             ;test sign
                .wrd  SEMIS
;
;                                       <
;                                       Altered from model
;                                       SCREEN 38 LINE 9
;
L1254           .byt  0x81,0xBC
                .wrd  L1246             ;link to U<
LESS            .wrd  $+2
                sec
                lda   2,x
                sbc   0,x               ;subtract
                lda   3,x
                sbc   1,x
                sty   3,x               ;zero high byte
                bvc   L1258
                eor   #0x80              ;correct overflow
L1258           bpl   L1260
                iny                     ;invert boolean
L1260           sty   2,x               ;leave boolean
                jmp   POP
;
;                                       >
;                                       SCREEN 38 LINE 10
L1264           .byt  0x81,0xBE
                .wrd  L1254             ;link to <
GREAT           .wrd  DOCOL
                .wrd  SWAP
                .wrd  LESS
                .wrd  SEMIS
;
;                                       ROT
;                                       SCREEN 38 LINE 11
;
L1274           .byt  0x83,"RO",0xD4
                .wrd  L1264             ;link to >
ROT             .wrd  DOCOL
                .wrd  TOR
                .wrd  SWAP
                .wrd  RFROM
                .wrd  SWAP
                .wrd  SEMIS
;
;                                       SPACE
;                                       SCREEN 38 LINE 12
;
L1286           .byt  0x85,"SPAC",0xC5
                .wrd  L1274             ;link to ROT
SPACE           .wrd  DOCOL
                .wrd  BL
                .wrd  EMIT
                .wrd  SEMIS
;
;                                       -DUP
;                                       SCREEN 38 LINE 13
;
L1296           .byt  0x84,"-DU",0xD0
                .wrd  L1286             ;link to SPACE
DDUP            .wrd  DOCOL
                .wrd  DUP
                .wrd  ZBRAN
L1301           .wrd  0x4                ;L1303-L1301
                .wrd  DUP
L1303           .wrd  SEMIS
;
;                                       TRAVERSE
;                                       SCREEN 39 LINE 14
;
L1308           .byt  0x88,"TRAVERS",0xC5
                .wrd  L1296             ;link to -DUP
TRAV            .wrd  DOCOL
                .wrd  SWAP
L1312           .wrd  OVER
                .wrd  PLUS
                .wrd  CLIT
                .byt  0x7F
                .wrd  OVER
                .wrd  CAT
                .wrd  LESS
                .wrd  ZBRAN
L1320           .wrd  0xFFF1             ;L1312-L1320
                .wrd  SWAP
                .wrd  DROP
                .wrd  SEMIS
;
;                                       LATEST
;                                       SCREEN 39 LINE 6
;
L1328           .byt  0x86,"LATES",0xD4
                .wrd  L1308             ;link to TRAVERSE
LATES           .wrd  DOCOL
                .wrd  CURR
                .wrd  AT
                .wrd  AT
                .wrd  SEMIS
;
;
;                                       LFA
;                                       SCREEN 39 LINE 11
;
L1339           .byt  0x83,"LF",0xC1
                .wrd  L1328             ;link to LATEST
LFA             .wrd  DOCOL
                .wrd  CLIT
                .byt  4
                .wrd  SUB
                .wrd  SEMIS
;
;                                       CFA
;                                       SCREEN 39 LINE 12
;
L1350           .byt  0x83,"CF",0xC1
                .wrd  L1339             ;link to LFA
CFA             .wrd  DOCOL
                .wrd  TWO
                .wrd  SUB
                .wrd  SEMIS
;
;                                       NFA
;                                       SCREEN 39 LIINE 13
;
L1360           .byt  0x83,"NF",0xC1
                .wrd  L1350             ;link to CFA
NFA             .wrd  DOCOL
                .wrd  CLIT
                .byt  0x5
                .wrd  SUB
                .wrd  LIT,0xFFFF
                .wrd  TRAV
                .wrd  SEMIS
;
;                                       PFA
;                                       SCREEN 39 LINE 14
;
L1373           .byt  0x83,"PF",0xC1
                .wrd  L1360             ;link to NFA
PFA             .wrd  DOCOL
                .wrd  ONE
                .wrd  TRAV
                .wrd  CLIT
                .byt  5
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       !CSP
;                                       SCREEN 40 LINE 1
;
L1386           .byt  0x84,"!CS",0xD0
                .wrd  L1373             ;link to PFA
SCSP            .wrd  DOCOL
                .wrd  SPAT
                .wrd  CSP
                .wrd  STORE
                .wrd  SEMIS
;
;                                       ?ERROR
;                                       SCREEN 40 LINE 3
;
L1397           .byt  0x86,"?ERRO",0xD2
                .wrd  L1386             ;link to !CSP
QERR            .wrd  DOCOL
                .wrd  SWAP
                .wrd  ZBRAN
L1402           .wrd  8                 ;L1406-L1402
                .wrd  ERROR
                .wrd  BRAN
L1405           .wrd  4                 ;L1407-L1405
L1406           .wrd  DROP
L1407           .wrd  SEMIS
;
;                                       ?COMP
;                                       SCREEN 40 LINE 6
;
L1412           .byt  0x85,"?COM",0xD0
                .wrd  L1397             ;link to ?ERROR
QCOMP           .wrd  DOCOL
                .wrd  STATE
                .wrd  AT
                .wrd  ZEQU
                .wrd  CLIT
                .byt  0x11
                .wrd  QERR
                .wrd  SEMIS
;
;                                       ?EXEC
;                                       SCREEN 40 LINE 8
;
L1426           .byt  0x85,"?EXE",0xC3
                .wrd  L1412             ;link to ?COMP
QEXEC           .wrd  DOCOL
                .wrd  STATE
                .wrd  AT
                .wrd  CLIT
                .byt  0x12
                .wrd  QERR
                .wrd  SEMIS
;
;                                       ?PAIRS
;                                       SCREEN 40 LINE 10
;
L1439           .byt  0x86,"?PAIR",0xD3
                .wrd  L1426             ;link to ?EXEC
QPAIR           .wrd  DOCOL
                .wrd  SUB
                .wrd  CLIT
                .byt  0x13
                .wrd  QERR
                .wrd  SEMIS
;
;                                       ?CSP
;                                       SCREEN 40 LINE 12
;
L1451           .byt  0x84,"?CS",0xD0
                .wrd  L1439             ;link to ?PAIRS
QCSP            .wrd  DOCOL
                .wrd  SPAT
                .wrd  CSP
                .wrd  AT
                .wrd  SUB
                .wrd  CLIT
                .byt  0x14
                .wrd  QERR
                .wrd  SEMIS
;
;                                       ?LOADING
;                                       SCREEN 40 LINE 14
;
L1466           .byt  0x88,"?LOADIN",0xC7
                .wrd  L1451             ;link to ?CSP
QLOAD           .wrd  DOCOL
                .wrd  BLK
                .wrd  AT
                .wrd  ZEQU
                .wrd  CLIT
                .byt  0x16
                .wrd  QERR
                .wrd  SEMIS
;
;                                       COMPILE
;                                       SCREEN 41 LINE 2
;
L1480           .byt  0x87,"COMPIL",0xC5
                .wrd  L1466             ;link to ?LOADING
COMP            .wrd  DOCOL
                .wrd  QCOMP
                .wrd  RFROM
                .wrd  DUP
                .wrd  TWOP
                .wrd  TOR
                .wrd  AT
                .wrd  COMMA
                .wrd  SEMIS
;
;                                       [
;                                       SCREEN 41 LINE 5
;
L1495           .byt  0xC1,0x.byt
                .wrd  L1480             ;link to COMPILE
LBRAC           .wrd  DOCOL
                .wrd  ZERO
                .wrd  STATE
                .wrd  STORE
                .wrd  SEMIS
;
;                                       ]
;                                       SCREEN 41 LINE 7
;
L1507           .byt  0x81,0xDD
                .wrd  L1495             ;link to [
RBRAC           .wrd  DOCOL
                .wrd  CLIT
                .byt  0xC0
                .wrd  STATE
                .wrd  STORE
                .wrd  SEMIS
;
;                                       SMUDGE
;                                       SCREEN 41 LINE 9
;
L1519           .byt  0x86,"SMUDG",0xC5
                .wrd  L1507             ;link to ]
SMUDG           .wrd  DOCOL
                .wrd  LATES
                .wrd  CLIT
                .byt  0x20
                .wrd  TOGGL
                .wrd  SEMIS
;
;                                       HEX
;                                       SCREEN 41 LINE 11
;
L1531           .byt  0x83,"HE",0xD8
                .wrd  L1519             ;link to SMUDGE
HEX             .wrd  DOCOL
                .wrd  CLIT
                .byt  16
                .wrd  BASE
                .wrd  STORE
                .wrd  SEMIS
;
;                                       DECIMAL
;                                       SCREEN 41 LINE 13
;
L1543           .byt  0x87,"DECIMA",0xCC
                .wrd  L1531             ;link to HEX
DECIM           .wrd  DOCOL
                .wrd  CLIT
                .byt  10
                .wrd  BASE
                .wrd  STORE
                .wrd  SEMIS
;
;
;
;                                       (;CODE)
;                                       SCREEN 42 LINE 2
;
L1555           .byt  0x87,"(            ;CODE",0xA9
                .wrd  L1543             ;link to DECIMAL
PSCOD           .wrd  DOCOL
                .wrd  RFROM
                .wrd  LATES
                .wrd  PFA
                .wrd  CFA
                .wrd  STORE
                .wrd  SEMIS
;
;                                       ;CODE
;                                       SCREEN 42 LINE 6
;
L1568           .byt  0xC5,";COD",0xC5
                .wrd  L1555             ;link to (;CODE)
SEMICOD         .wrd  DOCOL
                .wrd  QCSP
                .wrd  COMP
                .wrd  PSCOD
                .wrd  LBRAC
                .wrd  SMUDG
                .wrd  SEMIS
;
;                                       <BUILDS
;                                       SCREEN 43 LINE 2
;
L1582           .byt  0x87,"<BUILD",0xD3
                .wrd  L1568             ;link to ;CODE
BUILD           .wrd  DOCOL
                .wrd  ZERO
                .wrd  CONST
                .wrd  SEMIS
;
;                                       DOES>
;                                       SCREEN 43 LINE 4
;
L1592           .byt  0x85,"DOES",0xBE
                .wrd  L1582             ;link to <BUILDS
DOES            .wrd  DOCOL
                .wrd  RFROM
                .wrd  LATES
                .wrd  PFA
                .wrd  STORE
                .wrd  PSCOD
;
DODOE           lda   IP+1
                pha
                lda   IP
                pha
                ldy   #2
                lda   (W),y
                sta   IP
                iny
                lda   (W),y
                sta   IP+1
                clc
                lda   W
                adc   #4
                pha
                lda   W+1
                adc   #0
                jmp   PUSH
;
;                                       COUNT
;                                       SCREEN 44 LINE 1
;
L1622           .byt  0x85,"COUN",0xD4
                .wrd  L1592             ;link to DOES>
COUNT           .wrd  DOCOL
                .wrd  DUP
                .wrd  ONEP
                .wrd  SWAP
                .wrd  CAT
                .wrd  SEMIS
;
;                                       TYPE
;                                       SCREEN 44 LINE 2
;
L1634           .byt  0x84,"TYP",0xC5
                .wrd  L1622             ;link to COUNT
TYPE            .wrd  DOCOL
                .wrd  DDUP
                .wrd  ZBRAN
L1639           .wrd  0x18               ;L1651-L1639
                .wrd  OVER
                .wrd  PLUS
                .wrd  SWAP
                .wrd  PDO
L1644           .wrd  I
                .wrd  CAT
                .wrd  EMIT
                .wrd  PLOOP
L1648           .wrd  0xFFF8             ;L1644-L1648
                .wrd  BRAN
L1650           .wrd  0x4                ;L1652-L1650
L1651           .wrd  DROP
L1652           .wrd  SEMIS
;
;                                       -TRAILING
;                                       SCREEN 44 LINE 5
;
L1657           .byt  0x89,"-TRAILIN",0xC7
                .wrd  L1634             ;link to TYPE
DTRAI           .wrd  DOCOL
                .wrd  DUP
                .wrd  ZERO
                .wrd  PDO
L1663           .wrd  OVER
                .wrd  OVER
                .wrd  PLUS
                .wrd  ONE
                .wrd  SUB
                .wrd  CAT
                .wrd  BL
                .wrd  SUB
                .wrd  ZBRAN
L1672           .wrd  8                 ;L1676-L1672
                .wrd  LEAVE
                .wrd  BRAN
L1675           .wrd  6                 ;L1678-L1675
L1676           .wrd  ONE
                .wrd  SUB
L1678           .wrd  PLOOP
L1679           .wrd  0xFFE0             ;L1663-L1679
                .wrd  SEMIS
;
;                                       (.")
;                                       SCREEN 44 LINE 8
L1685           .byt  0x84,"(.",0x22,0xA9  ;0x84 (." 0xA9
                .wrd  L1657             ;link to -TRAILING
PDOTQ           .wrd  DOCOL
                .wrd  R
                .wrd  COUNT
                .wrd  DUP
                .wrd  ONEP
                .wrd  RFROM
                .wrd  PLUS
                .wrd  TOR
                .wrd  TYPE
                .wrd  SEMIS
;
;                                       ."
;                                       SCREEN 44 LINE12
;
L1701           .byt  0xC2,".",0xA2
                .wrd  L1685             ;link to PDOTQ
                .wrd  DOCOL
                .wrd  CLIT
                .byt  0x22
                .wrd  STATE
                .wrd  AT
                .wrd  ZBRAN
L1709           .wrd  0x14               ;L1719-L1709
                .wrd  COMP
                .wrd  PDOTQ
                .wrd  WORD
                .wrd  HERE
                .wrd  CAT
                .wrd  ONEP
                .wrd  ALLOT
                .wrd  BRAN
L1718           .wrd  0xA                ;L1723-L1718
L1719           .wrd  WORD
                .wrd  HERE
                .wrd  COUNT
                .wrd  TYPE
L1723           .wrd  SEMIS
;
;                                       EXPECT
;                                       SCREEN 45 LINE 2
;
L1729           .byt  0x86,"EXPEC",0xD4
                .wrd  L1701             ;link to ."
EXPEC           .wrd  DOCOL
                .wrd  OVER
                .wrd  PLUS
                .wrd  OVER
                .wrd  PDO
L1736           .wrd  KEY
                .wrd  DUP
                .wrd  CLIT
                .byt  0xE
                .wrd  PORIG
                .wrd  AT
                .wrd  EQUAL
                .wrd  ZBRAN
L1744           .wrd  0x1F               ;L1760-L1744
                .wrd  DROP
                .wrd  CLIT
                .byt  8                  ;Backspace!
                .wrd  OVER
                .wrd  I
                .wrd  EQUAL
                .wrd  DUP
                .wrd  RFROM
                .wrd  TWO
                .wrd  SUB
                .wrd  PLUS
                .wrd  TOR
                .wrd  SUB
                .wrd  BRAN
L1759           .wrd  0x27               ;L1779-L1759
L1760           .wrd  DUP
                .wrd  CLIT
                .byt  0x0D
                .wrd  EQUAL
                .wrd  ZBRAN
L1765           .wrd  0x0E               ;L1772-L1765
                .wrd  LEAVE
                .wrd  DROP
                .wrd  BL
                .wrd  ZERO
                .wrd  BRAN
L1771           .wrd  4                  ;L1773-L1771
L1772           .wrd  DUP
L1773           .wrd  I
                .wrd  CSTOR
                .wrd  ZERO
                .wrd  I
                .wrd  ONEP
                .wrd  STORE
L1779           .wrd  EMIT
                .wrd  PLOOP
L1781           .wrd  0xFFA9
                .wrd  DROP              ;L1736-L1781
                .wrd  SEMIS
;
;                                       QUERY
;                                       SCREEN 45 LINE 9
;
L1788           .byt  0x85,"QUER",0xD9
                .wrd  L1729             ;link to EXPECT
QUERY           .wrd  DOCOL
                .wrd  TIB
                .wrd  AT
                .wrd  CLIT
                .byt  80                ;80 characters from terminal
                .wrd  EXPEC
                .wrd  ZERO
                .wrd  IN
                .wrd  STORE
                .wrd  SEMIS
;
;                                       X
;                                       SCREEN 45 LINE 11
;                                       Actually Ascii Null
;
L1804           .byt  0xC1,0x80
                .wrd  L1788             ;link to QUERY
                .wrd  DOCOL
                .wrd  BLK
                .wrd  AT
                .wrd  ZBRAN
L1810           .wrd  0x2A               ;L1830-l1810
                .wrd  ONE
                .wrd  BLK
                .wrd  PSTOR
                .wrd  ZERO
                .wrd  IN
                .wrd  STORE
                .wrd  BLK
                .wrd  AT
                .wrd  ZERO,BSCR
                .wrd  USLAS
                .wrd  DROP              ;fixed from model
                .wrd  ZEQU
                .wrd  ZBRAN
L1824           .wrd  8                 ;L1828-L1824
                .wrd  QEXEC
                .wrd  RFROM
                .wrd  DROP
L1828           .wrd  BRAN
L1829           .wrd  6                 ;L1832-L1829
L1830           .wrd  RFROM
                .wrd  DROP
L1832           .wrd  SEMIS
;
;                                       FILL
;                                       SCREEN 46 LINE 1
;
;
L1838           .byt  0x84,"FIL",0xCC
                .wrd  L1804             ;link to X
FILL            .wrd  DOCOL
                .wrd  SWAP
                .wrd  TOR
                .wrd  OVER
                .wrd  CSTOR
                .wrd  DUP
                .wrd  ONEP
                .wrd  RFROM
                .wrd  ONE
                .wrd  SUB
                .wrd  CMOVE
                .wrd  SEMIS
;
;                                       ERASE
;                                       SCREEN 46 LINE 4
;
L1856           .byt  0x85,"ERAS",0xC5
                .wrd  L1838             ;link to FILL
ERASE           .wrd  DOCOL
                .wrd  ZERO
                .wrd  FILL
                .wrd  SEMIS
;
;                                       BLANKS
;                                       SCREEN 46 LINE 7
;
L1866           .byt  0x86,"BLANK",0xD3
                .wrd  L1856             ;link to ERASE
BLANK           .wrd  DOCOL
                .wrd  BL
                .wrd  FILL
                .wrd  SEMIS
;
;                                       HOLD
;                                       SCREEN 46 LINE 10
;
L1876           .byt  0x84,"HOL",0xC4
                .wrd  L1866             ;link to BLANKS
HOLD            .wrd  DOCOL
                .wrd  LIT,0xFFFF
                .wrd  HLD
                .wrd  PSTOR
                .wrd  HLD
                .wrd  AT
                .wrd  CSTOR
                .wrd  SEMIS
;
;                                       PAD
;                                       SCREEN 46 LINE 13
;
L1890           .byt  0x83,"PA",0xC4
                .wrd  L1876             ;link to HOLD
PAD             .wrd  DOCOL
                .wrd  HERE
                .wrd  CLIT
                .byt  68                ;PAD is 68 bytes above here.
                .wrd  PLUS
                .wrd  SEMIS
;
;                                       WORD
;                                       SCREEN 47 LINE 1
;
L1902           .byt  0x84,"WOR",0xC4
                .wrd  L1890             ;link to PAD
WORD            .wrd  DOCOL
                .wrd  BLK
                .wrd  AT
                .wrd  ZBRAN
L1908           .wrd  0xC                ;L1914-L1908
                .wrd  BLK
                .wrd  AT
                .wrd  BLOCK
                .wrd  BRAN
L1913           .wrd  0x6                ;L1916-L1913
L1914           .wrd  TIB
                .wrd  AT
L1916           .wrd  IN
                .wrd  AT
                .wrd  PLUS
                .wrd  SWAP
                .wrd  ENCL
                .wrd  HERE
                .wrd  CLIT
                .byt  0x22
                .wrd  BLANK
                .wrd  IN
                .wrd  PSTOR
                .wrd  OVER
                .wrd  SUB
                .wrd  TOR
                .wrd  R
                .wrd  HERE
                .wrd  CSTOR
                .wrd  PLUS
                .wrd  HERE
                .wrd  ONEP
                .wrd  RFROM
                .wrd  CMOVE
                .wrd  SEMIS
;
;                                       UPPER
;                                       SCREEN 47 LINE 12
;
L1943           .byt  0x85,"UPPE",0xD2
                .wrd  L1902             ;link to WORD
UPPER           .wrd  DOCOL
                .wrd  OVER              ;This routine converts text to U case
                .wrd  PLUS              ;It allows interpretation from a term.
                .wrd  SWAP              ;without a shift-lock.
                .wrd  PDO
L1950           .wrd  I
                .wrd  CAT
                .wrd  CLIT
                .byt  0x5F
                .wrd  GREAT
                .wrd  ZBRAN
L1956           .wrd  9                  ;L1961-L1956
                .wrd  I
                .wrd  CLIT
                .byt  0x20
                .wrd  TOGGL
L1961           .wrd  PLOOP
L1962           .wrd  0xFFEA             ;L1950-L1962
                .wrd  SEMIS
;
;                                       (NUMBER)
;                                       SCREEN 48 LINE 1
;
L1968           .byt  0x88,"(NUMBER",0xA9
                .wrd  L1943             ;link to UPPER
PNUMB           .wrd  DOCOL
L1971           .wrd  ONEP
                .wrd  DUP
                .wrd  TOR
                .wrd  CAT
                .wrd  BASE
                .wrd  AT
                .wrd  DIGIT
                .wrd  ZBRAN
L1979           .wrd  0x2C               ;L2001-L1979
                .wrd  SWAP
                .wrd  BASE
                .wrd  AT
                .wrd  USTAR
                .wrd  DROP
                .wrd  ROT
                .wrd  BASE
                .wrd  AT
                .wrd  USTAR
                .wrd  DPLUS
                .wrd  DPL
                .wrd  AT
                .wrd  ONEP
                .wrd  ZBRAN
L1994           .wrd  8                 ;L1998-L1994
                .wrd  ONE
                .wrd  DPL
                .wrd  PSTOR
L1998           .wrd  RFROM
                .wrd  BRAN
L2000           .wrd  0xFFC6             ;L1971-L2000
L2001           .wrd  RFROM
                .wrd  SEMIS
;
;                                       NUMBER
;                                       SCREEN 48 LINE 6
;
L2007           .byt  0x86,"NUMBE",0xD2
                .wrd  L1968             ;link to (NUMBER)
NUMBER          .wrd  DOCOL
                .wrd  ZERO
                .wrd  ZERO
                .wrd  ROT
                .wrd  DUP
                .wrd  ONEP
                .wrd  CAT
                .wrd  CLIT
                .byt  0x2D
                .wrd  EQUAL
                .wrd  DUP
                .wrd  TOR
                .wrd  PLUS
                .wrd  LIT,0xFFFF
L2023           .wrd  DPL
                .wrd  STORE
                .wrd  PNUMB
                .wrd  DUP
                .wrd  CAT
                .wrd  BL
                .wrd  SUB
                .wrd  ZBRAN
L2031           .wrd  0x15               ;L2042-L2031
                .wrd  DUP
                .wrd  CAT
                .wrd  CLIT
                .byt  0x2E
                .wrd  SUB
                .wrd  ZERO
                .wrd  QERR
                .wrd  ZERO
                .wrd  BRAN
L2041           .wrd  0xFFDD             ;L2023-L2041
L2042           .wrd  DROP
                .wrd  RFROM
                .wrd  ZBRAN
L2045           .wrd  4                  ;L2047-L2045
                .wrd  DMINU
L2047           .wrd  SEMIS
;
;                                       -FIND
;                                       SCREEN 48 LINE 12
;
L2052           .byt  0x85,"-FIN",0xC4
                .wrd  L2007             ;link to NUMBER
DFIND           .wrd  DOCOL
                .wrd  BL
                .wrd  WORD
                .wrd  HERE              ;)
                .wrd  COUNT             ;|- Optional allowing free use of low
                .wrd  UPPER             ;)  case from terminal
                .wrd  HERE
                .wrd  CON
                .wrd  AT
                .wrd  AT
                .wrd  PFIND
                .wrd  DUP
                .wrd  ZEQU
                .wrd  ZBRAN
L2068           .wrd  0xA                ;L2073-L2068
                .wrd  DROP
                .wrd  HERE
                .wrd  LATES
                .wrd  PFIND
L2073           .wrd  SEMIS
;
;                                       (ABORT)
;                                       SCREEN 49 LINE 2
;
L2078           .byt  0x87,"(ABORT",0xA9
                .wrd  L2052             ;link to -FIND
PABOR           .wrd  DOCOL
                .wrd  ABORT
                .wrd  SEMIS
;
;                                       ERROR
;                                       SCREEN 49 LINE 4
;
L2087           .byt  0x85,"ERRO",0xD2
                .wrd  L2078             ;link to (ABORT)
ERROR           .wrd  DOCOL
                .wrd  WARN
                .wrd  AT
                .wrd  ZLESS
                .wrd  ZBRAN
L2094           .wrd  0x4                ;L2096-L2094
                .wrd  PABOR
L2096           .wrd  HERE
                .wrd  COUNT
                .wrd  TYPE
                .wrd  PDOTQ
                .byt  4,"  ? "
                .wrd  MESS
                .wrd  SPSTO
                .wrd  DROP,DROP         ;make room for 2 error values
                .wrd  IN
                .wrd  AT
                .wrd  BLK
                .wrd  AT
                .wrd  QUIT
                .wrd  SEMIS
;
;                                       ID.
;                                       SCREEN 49 LINE 9
;
L2113           .byt  0x83,"ID",0xAE
                .wrd  L2087             ;link to ERROR
IDDOT           .wrd  DOCOL
                .wrd  PAD
                .wrd  CLIT
                .byt  0x20
                .wrd  CLIT
                .byt  0x5F
                .wrd  FILL
                .wrd  DUP
                .wrd  PFA
                .wrd  LFA
                .wrd  OVER
                .wrd  SUB
                .wrd  PAD
                .wrd  SWAP
                .wrd  CMOVE
                .wrd  PAD
                .wrd  COUNT
                .wrd  CLIT
                .byt  0x1F
                .wrd  ANDD
                .wrd  TYPE
                .wrd  SPACE
                .wrd  SEMIS
;
;                                       CREATE
;                                       SCREEN 50 LINE 2
;
L2142           .byt  0x86,"CREAT",0xC5
                .wrd  L2113             ;link to ID
CREAT           .wrd  DOCOL
                .wrd  TIB               ;)
                .wrd  HERE              ;|
                .wrd  CLIT              ;|  6502 only, assures
                .byt  0xA0               ;|  room exists in dict.
                .wrd  PLUS              ;|
                .wrd  ULESS             ;|
                .wrd  TWO               ;|
                .wrd  QERR              ;)
                .wrd  DFIND
                .wrd  ZBRAN
L2155           .wrd  0x0F
                .wrd  DROP
                .wrd  NFA
                .wrd  IDDOT
                .wrd  CLIT
                .byt  4
                .wrd  MESS
                .wrd  SPACE
L2163           .wrd  HERE
                .wrd  DUP
                .wrd  CAT
                .wrd  WIDTH
                .wrd  AT
                .wrd  MIN
                .wrd  ONEP
                .wrd  ALLOT
                .wrd  DP                ;)
                .wrd  CAT               ;| 6502 only. The code field
                .wrd  CLIT              ;| must not straddle page
                .byt  0xFD               ;| boundaries
                .wrd  EQUAL             ;|
                .wrd  ALLOT             ;)
                .wrd  DUP
                .wrd  CLIT
                .byt  0xA0
                .wrd  TOGGL
                .wrd  HERE
                .wrd  ONE
                .wrd  SUB
                .wrd  CLIT
                .byt  0x80
                .wrd  TOGGL
                .wrd  LATES
                .wrd  COMMA
                .wrd  CURR
                .wrd  AT
                .wrd  STORE
                .wrd  HERE
                .wrd  TWOP
                .wrd  COMMA
                .wrd  SEMIS
;
;                                       [COMPILE]
;                                       SCREEN 51 LINE 2
;
L2200           .byt  0xC9,"[COMPILE",0xDD
                .wrd  L2142             ;link to CREATE
                .wrd  DOCOL
                .wrd  DFIND
                .wrd  ZEQU
                .wrd  ZERO
                .wrd  QERR
                .wrd  DROP
                .wrd  CFA
                .wrd  COMMA
                .wrd  SEMIS
;
;                                       LITERAL
;                                       SCREEN 51 LINE 2
;
L2216           .byt  0xC7,"LITERA",0xCC
                .wrd  L2200             ;link to [COMPILE]
LITER           .wrd  DOCOL
                .wrd  STATE
                .wrd  AT
                .wrd  ZBRAN
L2222           .wrd  8                 ;L2226-L2222
                .wrd  COMP
                .wrd  LIT
                .wrd  COMMA
L2226           .wrd  SEMIS
;
;                                       DLITERAL
;                                       SCREEN 51 LINE 8
;
L2232           .byt  0xC8,"DLITERA",0xCC
                .wrd  L2216             ;link to LITERAL
DLIT            .wrd  DOCOL
                .wrd  STATE
                .wrd  AT
                .wrd  ZBRAN
L2238           .wrd  8                 ;L2242-L2238
                .wrd  SWAP
                .wrd  LITER
                .wrd  LITER
L2242           .wrd  SEMIS
;
;                                       ?STACK
;                                       SCREEN 51 LINE 13
;
L2248           .byt  0x86,"?STAC",0xCB
                .wrd  L2232             ;link to DLITERAL
QSTAC           .wrd  DOCOL
                .wrd  CLIT
                .byt  TOS
                .wrd  SPAT
                .wrd  ULESS
                .wrd  ONE
                .wrd  QERR
                .wrd  SPAT
                .wrd  CLIT
                .byt  BOS
                .wrd  ULESS
                .wrd  CLIT
                .byt  7
                .wrd  QERR
                .wrd  SEMIS
;
;                                       INTERPRET
;                                       SCREEN 52 LINE 2
;
L2269           .byt  0x89,"INTERPRE",0xD4
                .wrd  L2248             ;link to ?STACK
INTER           .wrd  DOCOL
L2272           .wrd  DFIND
                .wrd  ZBRAN
L2274           .wrd  0x1E               ;L2289-L2274
                .wrd  STATE
                .wrd  AT
                .wrd  LESS
                .wrd  ZBRAN
L2279           .wrd  0xA                ;L2284-L2279
                .wrd  CFA
                .wrd  COMMA
                .wrd  BRAN
L2283           .wrd  0x6                ;L2286-L2283
L2284           .wrd  CFA
                .wrd  EXEC
L2286           .wrd  QSTAC
                .wrd  BRAN
L2288           .wrd  0x1C               ;L2302-L2288
L2289           .wrd  HERE
                .wrd  NUMBER
                .wrd  DPL
                .wrd  AT
                .wrd  ONEP
                .wrd  ZBRAN
L2295           .wrd  8                 ;L2299-L2295
                .wrd  DLIT
                .wrd  BRAN
L2298           .wrd  0x6                ;L2301-L2298
L2299           .wrd  DROP
                .wrd  LITER
L2301           .wrd  QSTAC
L2302           .wrd  BRAN
L2303           .wrd  0xFFC2             ;L2272-L2303
;
;                                       IMMEDIATE
;                                       SCREEN 53 LINE 1
;
L2309           .byt  0x89,"IMMEDIAT",0xC5
                .wrd  L2269             ;; link to INTERPRET
                .wrd  DOCOL
                .wrd  LATES
                .wrd  CLIT
                .byt  0x40
                .wrd  TOGGL
                .wrd  SEMIS
;
;                                       VOCABULARY
;                                       SCREEN 53 LINE 4
;
L2321           .byt  0x8A,"VOCABULAR",0xD9
                .wrd  L2309             ;link to IMMEDIATE
                .wrd  DOCOL
                .wrd  BUILD
                .wrd  LIT,0xA081
                .wrd  COMMA
                .wrd  CURR
                .wrd  AT
                .wrd  CFA
                .wrd  COMMA
                .wrd  HERE
                .wrd  VOCL
                .wrd  AT
                .wrd  COMMA
                .wrd  VOCL
                .wrd  STORE
                .wrd  DOES
DOVOC           .wrd  TWOP
                .wrd  CON
                .wrd  STORE
                .wrd  SEMIS
;
;                                       FORTH
;                                       SCREEN 53 LINE 9
;
L2346           .byt  0xC5,"FORT",0xC8
                .wrd  L2321             ;link to VOCABULARY
FORTH           .wrd  DODOE
                .wrd  DOVOC
                .wrd  0xA081
XFOR            .wrd  NTOP              ;points to top name in FORTH
VL0             .wrd  0                 ;last vocab link ends at zero
;
;                                       DEFINITIONS
;                                       SCREEN 53 LINE 11
;
;
L2357           .byt  0x8B,"DEFINITION",0xD3
                .wrd  L2346             ;link to FORTH
DEFIN           .wrd  DOCOL
                .wrd  CON
                .wrd  AT
                .wrd  CURR
                .wrd  STORE
                .wrd  SEMIS
;
;                                       (
;                                       SCREEN 53 LINE 14
;
L2369           .byt  0xC1,0xA8
                .wrd  L2357             ;link to DEFINITIONS
                .wrd  DOCOL
                .wrd  CLIT
                .byt  0x29
                .wrd  WORD
                .wrd  SEMIS
;
;                                       QUIT
;                                       SCREEN 54 LINE 2
;
L2381           .byt  0x84,"QUI",0xD4
                .wrd  L2369             ;link to (
QUIT            .wrd  DOCOL
                .wrd  ZERO
                .wrd  BLK
                .wrd  STORE
                .wrd  LBRAC
L2388           .wrd  RPSTO
                .wrd  CR
                .wrd  QUERY
                .wrd  INTER
                .wrd  STATE
                .wrd  AT
                .wrd  ZEQU
                .wrd  ZBRAN
L2396           .wrd  7                 ;L2399-L2396
                .wrd  PDOTQ
                .byt  2,"OK"
L2399           .wrd  BRAN
L2400           .wrd  0xFFE7             ;L2388-L2400
                .wrd  SEMIS
;
;                                       ABORT
;                                       SCREEN 54 LINE 7
;
L2406           .byt  0x85,"ABOR",0xD4
                .wrd  L2381             ;link to QUIT
ABORT           .wrd  DOCOL
                .wrd  SPSTO
                .wrd  DECIM
                .wrd  DR0
                .wrd  CR
                .wrd  PDOTQ
                .byt  14,"fig-FORTH 1.0a"
                .wrd  FORTH
                .wrd  DEFIN
L2408           .wrd  VLIST         ;; Added for debugging
                .wrd  QUIT
;
;                                       COLD
;                                       SCREEN 55 LINE 1
;
L2423           .byt  0x84,"COL",0xC4
                .wrd  L2406             ;link to ABORT
COLD            .wrd  $+2
                lda   ORIG+0x0C          ;from cold start area
                sta   FORTH+6
                lda   ORIG+0x0D
                sta   FORTH+7
                ldy   #0x15
                bne   L2433
WARM            ldy   #0x0F
L2433           lda   ORIG+0x10
                sta   UP
                lda   ORIG+0x11
                sta   UP+1
L2437           lda   ORIG+0x0C,y
                sta   (UP),y
                dey
                bpl   L2437
                lda   #((ABORT+2) >> 8) & 0xFF          ;actually #>(ABORT+2)
                sta   IP+1
                lda   #((ABORT+2) >> 0) & 0xFF
                sta   IP
                cld
                lda   #0x6C              ;ind jump opcode
                sta   W-1
                jmp   RPSTO+2           ;And off we go !
;
;                                       S->D
;                                       SCREEN 56 LINE 1
;
L2453           .byt  0x84,"S->",0xC4
                .wrd  L2423             ;link to COLD
STOD            .wrd  DOCOL
                .wrd  DUP
                .wrd  ZLESS
                .wrd  MINUS
                .wrd  SEMIS
;
;                                       +-
;                                       SCREEN 56 LINE 4
;
L2464           .byt  0x82,"+",0xAD
                .wrd  L2453             ;link to S->D
PM              .wrd  DOCOL
                .wrd  ZLESS
                .wrd  ZBRAN
L2469           .wrd  4
                .wrd  MINUS
L2471           .wrd  SEMIS
;
;                                       D+-
;                                       SCREEN 56 LINE 6
;
L2476           .byt  0x83,"D+",0xAD
                .wrd  L2464             ;link to +-
DPM             .wrd  DOCOL
                .wrd  ZLESS
                .wrd  ZBRAN
L2481           .wrd  4                 ;L2483-L2481
                .wrd  DMINU
L2483           .wrd  SEMIS
;
;                                       ABS
;                                       SCREEN 56 LINE 9
;
L2488           .byt  0x83,"AB",0xD3
                .wrd  L2476             ;link to D+-
ABS             .wrd  DOCOL
                .wrd  DUP
                .wrd  PM
                .wrd  SEMIS
;
;                                       DABS
;                                       SCREEN 56 LINE 10
;
L2498           .byt  0x84,"DAB",0xD3
                .wrd  L2488             ;link to ABS
DABS            .wrd  DOCOL
                .wrd  DUP
                .wrd  DPM
                .wrd  SEMIS
;
;                                       MIN
;                                       SCREEN 56 LINE 12
;
L2508           .byt  0x83,"MI",0xCE
                .wrd  L2498             ;link to DABS
MIN             .wrd  DOCOL
                .wrd  OVER
                .wrd  OVER
                .wrd  GREAT
                .wrd  ZBRAN
L2515           .wrd  4                 ;L2517-L2515
                .wrd  SWAP
L2517           .wrd  DROP
                .wrd  SEMIS
;
;                                       MAX
;                                       SCREEN 56 LINE 14
;
L2523           .byt  0x83,"MA",0xD8
                .wrd  L2508             ;link to MIN
MAX             .wrd  DOCOL
                .wrd  OVER
                .wrd  OVER
                .wrd  LESS
                .wrd  ZBRAN
L2530           .wrd  4                 ;L2532-L2530
                .wrd  SWAP
L2532           .wrd  DROP
                .wrd  SEMIS
;
;                                       M*
;                                       SCREEN 57 LINE 1
;
L2538           .byt  0x82,"M",0xAA
                .wrd  L2523             ;link to MAX
MSTAR           .wrd  DOCOL
                .wrd  OVER
                .wrd  OVER
                .wrd  XOR
                .wrd  TOR
                .wrd  ABS
                .wrd  SWAP
                .wrd  ABS
                .wrd  USTAR
                .wrd  RFROM
                .wrd  DPM
                .wrd  SEMIS
;
;                                       M/
;                                       SCREEN 57 LINE 3
;
L2556           .byt  0x82,"M",0xAF
                .wrd  L2538             ;link to M*
MSLAS           .wrd  DOCOL
                .wrd  OVER
                .wrd  TOR
                .wrd  TOR
                .wrd  DABS
                .wrd  R
                .wrd  ABS
                .wrd  USLAS
                .wrd  RFROM
                .wrd  R
                .wrd  XOR
                .wrd  PM
                .wrd  SWAP
                .wrd  RFROM
                .wrd  PM
                .wrd  SWAP
                .wrd  SEMIS
;
;                                       *
;                                       SCREEN 57 LINE 7
;
L2579           .byt  0x81,0xAA
                .wrd  L2556             ;link to M/
STAR            .wrd  DOCOL
                .wrd  USTAR
                .wrd  DROP
                .wrd  SEMIS
;
;                                       /MOD
;                                       SCREEN 57 LINE 8
;
L2589           .byt  0x84,"/MO",0xC4
                .wrd  L2579             ;link to *
SLMOD           .wrd  DOCOL
                .wrd  TOR
                .wrd  STOD
                .wrd  RFROM
                .wrd  MSLAS
                .wrd  SEMIS
;
;                                       /
;                                       SCREEN 57 LINE 9
;
L2601           .byt  0x81,0xAF
                .wrd  L2589             ;link to /MOD
SLASH           .wrd  DOCOL
                .wrd  SLMOD
                .wrd  SWAP
                .wrd  DROP
                .wrd  SEMIS
;
;                                       MOD
;                                       SCREEN 57 LINE 10
;
L2612           .byt  0x83,"MO",0xC4
                .wrd  L2601             ;link to /
MOD             .wrd  DOCOL
                .wrd  SLMOD
                .wrd  DROP
                .wrd  SEMIS
;
;                                       */MOD
;                                       SCREEN 57 LINE 11
;
L2622           .byt  0x85,"*/MO",0xC4
                .wrd  L2612             ;link to MOD
SSMOD           .wrd  DOCOL
                .wrd  TOR
                .wrd  MSTAR
                .wrd  RFROM
                .wrd  MSLAS
                .wrd  SEMIS
;
;                                       */
;                                       SCREEN 57 LINE 13
;
L2634           .byt  0x82,"*",0xAF
                .wrd  L2622             ;link to */MOD
SSLAS           .wrd  DOCOL
                .wrd  SSMOD
                .wrd  SWAP
                .wrd  DROP
                .wrd  SEMIS
;
;                                       M/MOD
;                                       SCREEN 57 LINE 14
;
L2645           .byt  0x85,"M/MO",0xC4
                .wrd  L2634             ;link to */
MSMOD           .wrd  DOCOL
                .wrd  TOR
                .wrd  ZERO
                .wrd  R
                .wrd  USLAS
                .wrd  RFROM
                .wrd  SWAP
                .wrd  TOR
                .wrd  USLAS
                .wrd  RFROM
                .wrd  SEMIS
;
;                                       USE
;                                       SCREEN 58 LINE 1
;
L2662           .byt  0x83,"US",0xC5
                .wrd  L2645             ;link to M/MOD
USE             .wrd  DOVAR
                .wrd  DAREA
;
;                                       PREV
;                                       SCREEN 58 LINE 2
;
L2670           .byt  0x84,"PRE",0xD6
                .wrd  L2662             ;link to USE
PREV            .wrd  DOVAR
                .wrd  DAREA
;
;                                       +BUF
;                                       SCREEN 58 LINE 4
;
;
L2678           .byt  0x84,"+BU",0xC6
                .wrd  L2670             ;link to PREV
PBUF            .wrd  DOCOL
                .wrd  LIT
                .wrd  SSIZE+4           ;hold block #, one sector two num
                .wrd  PLUS
                .wrd  DUP
                .wrd  LIMIT
                .wrd  EQUAL
                .wrd  ZBRAN
L2688           .wrd  6                 ;L2691-L2688
                .wrd  DROP
                .wrd  FIRST
L2691           .wrd  DUP
                .wrd  PREV
                .wrd  AT
                .wrd  SUB
                .wrd  SEMIS
;
;                                       UPDATE
;                                       SCREEN 58 LINE 8
;
L2700           .byt  0x86,"UPDAT",0xC5
                .wrd  L2678             ;link to +BUF
UPDAT           .wrd  DOCOL
                .wrd  PREV
                .wrd  AT
                .wrd  AT
                .wrd  LIT,0x8000
                .wrd  OR
                .wrd  PREV
                .wrd  AT
                .wrd  STORE
                .wrd  SEMIS
;
;                                       FLUSH
;
L2705           .byt  0x85,"FLUS",0xC8
                .wrd  L2700             ;link to UPDATE
                .wrd  DOCOL
                .wrd  LIMIT,FIRST,SUB
                .wrd  BBUF,CLIT
                .byt  4
                .wrd  PLUS,SLASH,ONEP
                .wrd  ZERO,PDO
L2835           .wrd  LIT,0x7FFF,BUFFR
                .wrd  DROP,PLOOP
L2839           .wrd  0xFFF6             ;L2835-L2839
                .wrd  SEMIS
;
;                                       EMPTY-BUFFERS
;                                       SCREEN 58 LINE 11
;
L2716           .byt  0x8D,"EMPTY-BUFFER",0xD3
                .wrd  L2705             ;link to FLUSH
                .wrd  DOCOL
                .wrd  FIRST
                .wrd  LIMIT
                .wrd  OVER
                .wrd  SUB
                .wrd  ERASE
                .wrd  SEMIS
;
;                                       DR0
;                                       SCREEN 58 LINE 14
;
L2729           .byt  0x83,"DR",0xB0
                .wrd  L2716             ;link to EMPTY-BUFFERS
DR0             .wrd  DOCOL
                .wrd  ZERO
                .wrd  OFSET
                .wrd  STORE
                .wrd  SEMIS
;
;                                       DR1
;                                       SCREEN 58 LINE 15
;
L2740           .byt  0x83,"DR",0xB1
                .wrd  L2729             ;link to DR0
                .wrd  DOCOL
                .wrd  LIT,SECTR         ;sectors per drive
                .wrd  OFSET
                .wrd  STORE
                .wrd  SEMIS
;
;                                       BUFFER
;                                       SCREEN 59 LINE 1
;
L2751           .byt  0x86,"BUFFE",0xD2
                .wrd  L2740             ;link to DR1
BUFFR           .wrd  DOCOL
                .wrd  USE
                .wrd  AT
                .wrd  DUP
                .wrd  TOR
L2758           .wrd  PBUF
                .wrd  ZBRAN
L2760           .wrd  0xFFFC             ;L2758-L2760
                .wrd  USE
                .wrd  STORE
                .wrd  R
                .wrd  AT
                .wrd  ZLESS
                .wrd  ZBRAN
L2767           .wrd  0x14               ;L2776-L2767
                .wrd  R
                .wrd  TWOP
                .wrd  R
                .wrd  AT
                .wrd  LIT,0x7FFF
                .wrd  ANDD
                .wrd  ZERO
;          .WORD RSLW
                .wrd  RSW
L2776           .wrd  R
                .wrd  STORE
                .wrd  R
                .wrd  PREV
                .wrd  STORE
                .wrd  RFROM
                .wrd  TWOP
                .wrd  SEMIS
;
;                                       BLOCK
;                                       SCREEN 60 LINE 1
;
L2788           .byt  0x85,"BLOC",0xCB
                .wrd  L2751             ;link to BUFFER
BLOCK           .wrd  DOCOL
                .wrd  OFSET
                .wrd  AT
                .wrd  PLUS
                .wrd  TOR
                .wrd  PREV
                .wrd  AT
                .wrd  DUP
                .wrd  AT
                .wrd  R
                .wrd  SUB
                .wrd  DUP
                .wrd  PLUS
                .wrd  ZBRAN
L2804           .wrd  0x34               ;L2830-L2804
L2805           .wrd  PBUF
                .wrd  ZEQU
                .wrd  ZBRAN
L2808           .wrd  0x14               ;L2818-L2808
                .wrd  DROP
                .wrd  R
                .wrd  BUFFR
                .wrd  DUP
                .wrd  R
                .wrd  ONE
;          .WORD RSLW
                .wrd  RSW
                .wrd  TWO
                .wrd  SUB
L2818           .wrd  DUP
                .wrd  AT
                .wrd  R
                .wrd  SUB
                .wrd  DUP
                .wrd  PLUS
                .wrd  ZEQU
                .wrd  ZBRAN
L2826           .wrd  0xFFD6             ;L2805-L2826
                .wrd  DUP
                .wrd  PREV
                .wrd  STORE
L2830           .wrd  RFROM
                .wrd  DROP
                .wrd  TWOP
                .wrd  SEMIS             ;end of BLOCK
;
;
;                                       (LINE)
;                                       SCREEN 61 LINE 2
;
L2838           .byt  0x86,"(LINE",0xA9
                .wrd  L2788             ;link to BLOCK
PLINE           .wrd  DOCOL
                .wrd  TOR
                .wrd  CSLL
                .wrd  BBUF
                .wrd  SSMOD
                .wrd  RFROM
                .wrd  BSCR
                .wrd  STAR
                .wrd  PLUS
                .wrd  BLOCK
                .wrd  PLUS
                .wrd  CSLL
                .wrd  SEMIS
;
;                                       .LINE
;                                       SCREEN 61 LINE 6
;
L2857           .byt  0x85,".LIN",0xC5
                .wrd  L2838             ;link to (LINE)
DLINE           .wrd  DOCOL
                .wrd  PLINE
                .wrd  DTRAI
                .wrd  TYPE
                .wrd  SEMIS
;
;                                       MESSAGE
;                                       SCREEN 61 LINE 9
;
L2868           .byt  0x87,"MESSAG",0xC5
                .wrd  L2857             ;link to .LINE
MESS            .wrd  DOCOL
                .wrd  WARN
                .wrd  AT
                .wrd  ZBRAN
L2874           .wrd  0x1B               ;L2888-L2874
                .wrd  DDUP
                .wrd  ZBRAN
L2877           .wrd  0x11               ;L2886-L2877
                .wrd  CLIT
                .byt  4
                .wrd  OFSET
                .wrd  AT
                .wrd  BSCR
                .wrd  SLASH
                .wrd  SUB
                .wrd  DLINE
L2886           .wrd  BRAN
L2887           .wrd  13                ;L2891-L2887
L2888           .wrd  PDOTQ
                .byt  6,"MSG # "
                .wrd  DOT
L2891           .wrd  SEMIS
;
;                                       LOAD
;                                       SCREEN 62 LINE 2
;
L2896           .byt  0x84,"LOA",0xC4
                .wrd  L2868             ;link to MESSAGE
LOAD            .wrd  DOCOL
                .wrd  BLK
                .wrd  AT
                .wrd  TOR
                .wrd  IN
                .wrd  AT
                .wrd  TOR
                .wrd  ZERO
                .wrd  IN
                .wrd  STORE
                .wrd  BSCR
                .wrd  STAR
                .wrd  BLK
                .wrd  STORE
                .wrd  INTER
                .wrd  RFROM
                .wrd  IN
                .wrd  STORE
                .wrd  RFROM
                .wrd  BLK
                .wrd  STORE
                .wrd  SEMIS
;
;                                       -->
;                                       SCREEN 62 LINE 6
;
L2924           .byt  0xC3,"--",0xBE
                .wrd  L2896             ;link to LOAD
                .wrd  DOCOL
                .wrd  QLOAD
                .wrd  ZERO
                .wrd  IN
                .wrd  STORE
                .wrd  BSCR
                .wrd  BLK
                .wrd  AT
                .wrd  OVER
                .wrd  MOD
                .wrd  SUB
                .wrd  BLK
                .wrd  PSTOR
                .wrd  SEMIS
;
;    XEMIT writes one ascii character to terminal
;
;
;XEMIT
;	             TYA
;                SEC
;                LDY    #0x1A
;                ADC    (UP),Y
;                STA    (UP),Y
;                INY                 ; bump user variable OUT
;                LDA    #0
;                ADC    (UP),Y
;                STA    (UP),Y
XEMIT           lda     0,x         ; fetch character to output
;                STX    XSAVE
                and     #0x7F
                jsr     cout        ; and display it
;                LDX    XSAVE
                 jmp    POP
;
;         XKEY reads one terminal keystroke to stack
;
;
;XKEY
;                STX     XSAVE
XKEY            jsr     cin         ; might otherwise clobber it while
;                LDX     XSAVE      ; inputting a char to accumulator
                jmp     PUSHOA
;
;         XQTER leaves a boolean representing terminal break
;
;
;XQTER
;               jsr     cbrk         ;if Ctrl-c, set C else clear C
XQTER           clc
                lda     #0x00        ; 0
                rol     a           ; move carry to bit 0
                jmp     PUSHOA
;
;         XCR displays a CR and LF to terminal
;
;
;XCR
;                STX     XSAVE
XCR             jsr     crout               ;use monitor call
;                LDX     XSAVE
                jmp     NEXT
;
; ***                                      -DISC
;                                       machine level sector R/W
;
;L3030     .BYTE 0x85,"-DIS",0xC3
;          .WORD L2924    ; link to -->
;DDISC     .WORD $+2
;          LDA 0,X
;          STA 0xC60C
;          STA 0xC60D      ; store sector number
;          LDA 2,X
;          STA 0xC60A
;          STA 0xC60B      ; store track number
;          LDA 4,X
;          STA 0xC4CD
;          STA 0xC4CE      ; store drive number
;          STX XSAVE
;          LDA 0xC4DA      ; sense read or write
;          BNE L3032
;          JSR 0xE1FE
;          JMP L3040
;L3032     JSR 0xE262
;L3040     JSR 0xE3EF      ; head up motor off
;          LDX XSAVE
;          LDA 0xC4E1      ; report error code
;          STA 4,X
;          JMP POPTWO
;
;                                       -BCD
;                             Convert binary value to BCD
;
L3050           .byt  0x84,"-BC",0xC4
                .wrd  L2924             ;link to -DISC
DBCD            .wrd  DOCOL
                .wrd  ZERO,CLIT
                .byt  10
                .wrd  USLAS,CLIT
                .byt  16
                .wrd  STAR,OR,SEMIS

;
; ***                                       R/W
;                              Read or write one sector
;
;L3060     .BYTE 0x83,"R/",0xD7
;          .WORD L3050    ; link to -BCD
;RSLW      .WORD DOCOL
;          .WORD ZEQU,LIT,0xC4DA,CSTOR
;          .WORD SWAP,ZERO,STORE
;          .WORD ZERO,OVER,GREAT,OVER
;          .WORD LIT,SECTL-1,GREAT,OR,CLIT
;          .BYTE 6
;          .WORD QERR
;          .WORD ZERO,LIT,SECTR,USLAS,ONEP
;          .WORD SWAP,ZERO,CLIT
;          .BYTE 0x12
;          .WORD USLAS,DBCD,SWAP,ONEP
;          .WORD DBCD,DDISC,CLIT
;          .BYTE 8
;          .WORD QERR
;          .WORD SEMIS
;
;
;                                           RSW
;                              Read or write one sector
;
L3070           .byt  0x83,"RS",0xD7
                .wrd  L3050             ;link to R/W
RSW             .wrd  DOCOL
                .wrd  TOR
                .wrd  BBUF, STAR, LIT, 0x4000, PLUS, DUP
                .wrd  LIT, 0x6800, GREAT, LIT, 0x6, QERR
                .wrd  RFROM, ZBRAN, 0x4, SWAP
                .wrd  BBUF, CMOVE
                .wrd  SEMIS
;
;
;                                       '
;                                       SCREEN 72 LINE 2
;
L3202           .byt  0xC1,0xA7
                .wrd  L3070             ;link to RSW
TICK            .wrd  DOCOL
                .wrd  DFIND
                .wrd  ZEQU
                .wrd  ZERO
                .wrd  QERR
                .wrd  DROP
                .wrd  LITER
                .wrd  SEMIS
;
;                                       FORGET
;                                       Altered from model
;                                       SCREEN 72 LINE 6
;
L3217           .byt  0x86,"FORGE",0xD4
                .wrd  L3202             ;link to ' TICK
FORG            .wrd  DOCOL
                .wrd  TICK,NFA,DUP
                .wrd  FENCE,AT,ULESS,CLIT
                .byt  0x15
                .wrd  QERR,TOR,VOCL,AT
L3220           .wrd  R,OVER,ULESS
                .wrd  ZBRAN,L3225-$
                .wrd  FORTH,DEFIN,AT,DUP
                .wrd  VOCL,STORE
                .wrd  BRAN,0xFFFF-24+1   ;L3220-$
L3225           .wrd  DUP,CLIT
                .byt  4
                .wrd  SUB
L3228           .wrd  PFA,LFA,AT
                .wrd  DUP,R,ULESS
                .wrd  ZBRAN,0xFFFF-14+1  ;L3228-$
                .wrd  OVER,TWO,SUB,STORE
                .wrd  AT,DDUP,ZEQU
                .wrd  ZBRAN,0xFFFF-39+1  ;L3225-$
                .wrd  RFROM,DP,STORE
                .wrd  SEMIS
;
;                                       BACK
;                                       SCREEN 73 LINE 1
;
L3250           .byt  0x84,"BAC",0xCB
                .wrd  L3217             ;link to FORGET
BACK            .wrd  DOCOL
                .wrd  HERE
                .wrd  SUB
                .wrd  COMMA
                .wrd  SEMIS
;
;                                       BEGIN
;                                       SCREEN 73 LINE 3
;
L3261           .byt  0xC5,"BEGI",0xCE
                .wrd  L3250             ;link to BACK
                .wrd  DOCOL
                .wrd  QCOMP
                .wrd  HERE
                .wrd  ONE
                .wrd  SEMIS
;
;                                       ENDIF
;                                       SCREEN 73 LINE 5
;
L3273           .byt  0xC5,"ENDI",0xC6
                .wrd  L3261             ;link to BEGIN
ENDIF           .wrd  DOCOL
                .wrd  QCOMP
                .wrd  TWO
                .wrd  QPAIR
                .wrd  HERE
                .wrd  OVER
                .wrd  SUB
                .wrd  SWAP
                .wrd  STORE
                .wrd  SEMIS
;
;                                       THEN
;                                       SCREEN 73 LINE 7
;
L3290           .byt  0xC4,"THE",0xCE
                .wrd  L3273             ;link to ENDIF
                .wrd  DOCOL
                .wrd  ENDIF
                .wrd  SEMIS
;
;                                       DO
;                                       SCREEN 73 LINE 9
;
L3300           .byt  0xC2,"D",0xCF
                .wrd  L3290             ;link to THEN
                .wrd  DOCOL
                .wrd  COMP
                .wrd  PDO
                .wrd  HERE
                .wrd  THREE
                .wrd  SEMIS
;
;                                       LOOP
;                                       SCREEN 73 LINE 11
;
;
L3313           .byt  0xC4,"LOO",0xD0
                .wrd  L3300             ;link to DO
                .wrd  DOCOL
                .wrd  THREE
                .wrd  QPAIR
                .wrd  COMP
                .wrd  PLOOP
                .wrd  BACK
                .wrd  SEMIS
;
;                                       +LOOP
;                                       SCREEN 73 LINE 13
;
L3327           .byt  0xC5,"+LOO",0xD0
                .wrd  L3313             ;link to LOOP
                .wrd  DOCOL
                .wrd  THREE
                .wrd  QPAIR
                .wrd  COMP
                .wrd  PPLOO
                .wrd  BACK
                .wrd  SEMIS
;
;                                       UNTIL
;                                       SCREEN 73 LINE 15
;
L3341           .byt  0xC5,"UNTI",0xCC
                .wrd  L3327             ;link to +LOOP
UNTIL           .wrd  DOCOL
                .wrd  ONE
                .wrd  QPAIR
                .wrd  COMP
                .wrd  ZBRAN
                .wrd  BACK
                .wrd  SEMIS
;
;                                       END
;                                       SCREEN 74 LINE 1
;
L3355           .byt  0xC3,"EN",0xC4
                .wrd  L3341             ;link to UNTIL
                .wrd  DOCOL
                .wrd  UNTIL
                .wrd  SEMIS
;
;                                       AGAIN
;                                       SCREEN 74 LINE 3
;
L3365           .byt  0xC5,"AGAI",0xCE
                .wrd  L3355             ;link to END
AGAIN           .wrd  DOCOL
                .wrd  ONE
                .wrd  QPAIR
                .wrd  COMP
                .wrd  BRAN
                .wrd  BACK
                .wrd  SEMIS
;
;                                       REPEAT
;                                       SCREEN 74 LINE 5
;
L3379           .byt  0xC6,"REPEA",0xD4
                .wrd  L3365             ;link to AGAIN
                .wrd  DOCOL
                .wrd  TOR
                .wrd  TOR
                .wrd  AGAIN
                .wrd  RFROM
                .wrd  RFROM
                .wrd  TWO
                .wrd  SUB
                .wrd  ENDIF
                .wrd  SEMIS
;
;                                       IF
;                                       SCREEN 74 LINE 8
;
L3396           .byt  0xC2,"I",0xC6
                .wrd  L3379             ;link to REPEAT
IF              .wrd  DOCOL
                .wrd  COMP
                .wrd  ZBRAN
                .wrd  HERE
                .wrd  ZERO
                .wrd  COMMA
                .wrd  TWO
                .wrd  SEMIS
;
;                                       ELSE
;                                       SCREEN 74 LINE 10
;
L3411           .byt  0xC4,"ELS",0xC5
                .wrd  L3396             ;link to IF
                .wrd  DOCOL
                .wrd  TWO
                .wrd  QPAIR
                .wrd  COMP
                .wrd  BRAN
                .wrd  HERE
                .wrd  ZERO
                .wrd  COMMA
                .wrd  SWAP
                .wrd  TWO
                .wrd  ENDIF
                .wrd  TWO
                .wrd  SEMIS
;
;                                       WHILE
;                                       SCREEN 74 LINE 13
;
L3431           .byt  0xC5,"WHIL",0xC5
                .wrd  L3411             ;link to ELSE
                .wrd  DOCOL
                .wrd  IF
                .wrd  TWOP
                .wrd  SEMIS
;
;                                       SPACES
;                                       SCREEN 75 LINE 1
;
L3442           .byt  0x86,"SPACE",0xD3
                .wrd  L3431             ;link to WHILE
SPACS           .wrd  DOCOL
                .wrd  ZERO
                .wrd  MAX
                .wrd  DDUP
                .wrd  ZBRAN
L3449           .wrd  0x0C               ;L3455-L3449
                .wrd  ZERO
                .wrd  PDO
L3452           .wrd  SPACE
                .wrd  PLOOP
L3454           .wrd  0xFFFC             ;L3452-L3454
L3455           .wrd  SEMIS
;
;                                       <#
;                                       SCREEN 75 LINE 3
;
L3460           .byt  0x82,"<",0xA3
                .wrd  L3442             ;link to SPACES
BDIGS           .wrd  DOCOL
                .wrd  PAD
                .wrd  HLD
                .wrd  STORE
                .wrd  SEMIS
;
;                                       #>
;                                       SCREEN 75 LINE 5
;
L3471           .byt  0x82,"#",0xBE
                .wrd  L3460             ;link to <#
EDIGS           .wrd  DOCOL
                .wrd  DROP
                .wrd  DROP
                .wrd  HLD
                .wrd  AT
                .wrd  PAD
                .wrd  OVER
                .wrd  SUB
                .wrd  SEMIS
;
;                                       SIGN
;                                       SCREEN 75 LINE 7
;
L3486           .byt  0x84,"SIG",0xCE
                .wrd  L3471             ;link to #>
SIGN            .wrd  DOCOL
                .wrd  ROT
                .wrd  ZLESS
                .wrd  ZBRAN
L3492           .wrd  0x7                ;L3496-L3492
                .wrd  CLIT
                .byt  0x2D
                .wrd  HOLD
L3496           .wrd  SEMIS
;
;                                       #
;                                       SCREEN 75 LINE 9
;
L3501           .byt  0x81,0xA3
                .wrd  L3486             ;link to SIGN
DIG             .wrd  DOCOL
                .wrd  BASE
                .wrd  AT
                .wrd  MSMOD
                .wrd  ROT
                .wrd  CLIT
                .byt  9
                .wrd  OVER
                .wrd  LESS
                .wrd  ZBRAN
L3513           .wrd  7                 ;L3517-L3513
                .wrd  CLIT
                .byt  7
                .wrd  PLUS
L3517           .wrd  CLIT
                .byt  0x30
                .wrd  PLUS
                .wrd  HOLD
                .wrd  SEMIS
;
;                                       #S
;                                       SCREEN 75 LINE 12
;
L3526           .byt  0x82,"#",0xD3
                .wrd  L3501             ;link to #
DIGS            .wrd  DOCOL
L3529           .wrd  DIG
                .wrd  OVER
                .wrd  OVER
                .wrd  OR
                .wrd  ZEQU
                .wrd  ZBRAN
L3535           .wrd  0xFFF4             ;L3529-L3535
                .wrd  SEMIS
;
;                                       D.R
;                                       SCREEN 76 LINE 1
;
L3541           .byt  0x83,"D.",0xD2
                .wrd  L3526             ;link to #S
DDOTR           .wrd  DOCOL
                .wrd  TOR
                .wrd  SWAP
                .wrd  OVER
                .wrd  DABS
                .wrd  BDIGS
                .wrd  DIGS
                .wrd  SIGN
                .wrd  EDIGS
                .wrd  RFROM
                .wrd  OVER
                .wrd  SUB
                .wrd  SPACS
                .wrd  TYPE
                .wrd  SEMIS
;
;                                       D.
;                                       SCREEN 76 LINE 5
;
L3562           .byt  0x82,"D",0xAE
                .wrd  L3541             ;link to D.R
DDOT            .wrd  DOCOL
                .wrd  ZERO
                .wrd  DDOTR
                .wrd  SPACE
                .wrd  SEMIS
;
;                                       .R
;                                       SCREEN 76 LINE 7
;
L3573           .byt  0x82,".",0xD2
                .wrd  L3562             ;link to D.
DOTR            .wrd  DOCOL
                .wrd  TOR
                .wrd  STOD
                .wrd  RFROM
                .wrd  DDOTR
                .wrd  SEMIS
;
;                                       .
;                                       SCREEN 76  LINE  9
;
L3585           .byt  0x81,0xAE
                .wrd  L3573             ;link to .R
DOT             .wrd  DOCOL
                .wrd  STOD
                .wrd  DDOT
                .wrd  SEMIS
;
;                                       ?
;                                       SCREEN 76 LINE 11
;
L3595           .byt  0x81,0xBF
                .wrd  L3585             ;link to .
QUES            .wrd  DOCOL
                .wrd  AT
                .wrd  DOT
                .wrd  SEMIS
;
;                                       LIST
;                                       SCREEN 77 LINE 2
;
L3605           .byt  0x84,"LIS",0xD4
                .wrd  L3595             ;link to ?
LIST            .wrd  DOCOL
                .wrd  DECIM
                .wrd  CR
                .wrd  DUP
                .wrd  SCR
                .wrd  STORE
                .wrd  PDOTQ
                .byt  6,"SCR # "
                .wrd  DOT
                .wrd  CLIT
                .byt  16
                .wrd  ZERO
                .wrd  PDO
L3620           .wrd  CR
                .wrd  I
                .wrd  THREE
                .wrd  DOTR
                .wrd  SPACE
                .wrd  I
                .wrd  SCR
                .wrd  AT
                .wrd  DLINE
                .wrd  PLOOP
L3630           .wrd  0xFFEC
                .wrd  CR
                .wrd  SEMIS
;
;                                       INDEX
;                                       SCREEN 77 LINE 7
;
L3637           .byt  0x85,"INDE",0xD8
                .wrd  L3605             ;link to LIST
                .wrd  DOCOL
                .wrd  CR
                .wrd  ONEP
                .wrd  SWAP
                .wrd  PDO
L3647           .wrd  CR
                .wrd  I
                .wrd  THREE
                .wrd  DOTR
                .wrd  SPACE
                .wrd  ZERO
                .wrd  I
                .wrd  DLINE
                .wrd  QTERM
                .wrd  ZBRAN
L3657           .wrd  4                 ;L3659-L3657
                .wrd  LEAVE
L3659           .wrd  PLOOP
L3660           .wrd  0xFFE6             ;L3647-L3660
                .wrd  CLIT
                .byt  0x0C               ;form feed for printer
                .wrd  EMIT
                .wrd  SEMIS
;
;                                       TRIAD
;                                       SCREEN 77 LINE 12
;
L3666           .byt  0x85,"TRIA",0xC4
                .wrd  L3637             ;link to INDEX
                .wrd  DOCOL
                .wrd  THREE
                .wrd  SLASH
                .wrd  THREE
                .wrd  STAR
                .wrd  THREE
                .wrd  OVER
                .wrd  PLUS
                .wrd  SWAP
                .wrd  PDO
L3681           .wrd  CR
                .wrd  I
                .wrd  LIST
                .wrd  PLOOP
L3685           .wrd  0xFFF8             ;L3681-L3685
                .wrd  CR
                .wrd  CLIT
                .byt  0xF
                .wrd  MESS
                .wrd  CR
                .wrd  CLIT
                .byt  0x0C               ;form feed for printer
                .wrd  EMIT
                .wrd  SEMIS
;
;                                       VLIST
;                                       SCREEN 78 LINE 2
;
;
L3696           .byt  0x85,"VLIS",0xD4
                .wrd  L3666             ;link to TRIAD
VLIST           .wrd  DOCOL
                .wrd  CLIT
                .byt  0x80
                .wrd  OUT
                .wrd  STORE
                .wrd  CON
                .wrd  AT
                .wrd  AT
L3706           .wrd  OUT
                .wrd  AT
                .wrd  CSLL
                .wrd  GREAT
                .wrd  ZBRAN
L3711           .wrd  0xA                ;L3716-L3711
                .wrd  CR
                .wrd  ZERO
                .wrd  OUT
                .wrd  STORE
L3716           .wrd  DUP
                .wrd  IDDOT
                .wrd  SPACE
                .wrd  SPACE
                .wrd  PFA
                .wrd  LFA
                .wrd  AT
                .wrd  DUP
                .wrd  ZEQU
                .wrd  QTERM
                .wrd  OR
                .wrd  ZBRAN
L3728           .wrd  0xFFD4             ;L3706-L3728
                .wrd  DROP
                .wrd  SEMIS
;
;                                       MON
;                                       SCREEN 79 LINE 3
;
NTOP            .byt    0x83,"MO",0xCE
                .wrd    L3696             ;link to VLIST
MON             .wrd    $+2
                brk
;                jmp     (0xFFFC)           ;back to SBC Monitor
                jmp     NEXT
;                STX     XSAVE
;                BRK                     ; break to monitor which is assumed
;                LDX     XSAVE           ; to save this as reentry point
;                JMP     NEXT
;
TOP             .equ    $                ;end of listing

