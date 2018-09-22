import re
import os
import array

filename = input('Enter filename to convert to binary: ')

pgm = array.array('B', [])

with open(filename+'.mem', 'rt') as finp:
    while True:
        line = finp.readline()
        if line == '':
            break
        pgm.append(int(line[:-1], 16))

pgm = bytes(pgm)

print(pgm)

with open(filename+'.bin', 'wb') as fout:
    fout.write(pgm)
