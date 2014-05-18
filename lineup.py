#!env python

import sys
import os
from pager import *
from StringIO import StringIO
import csv

def usage():
    print "Usage: %s FILE <delimiter: t=<tab>, default ',' " % sys.argv[0]
    exit()

#if len(sys.argv) <2:
#    usage()
if len(sys.argv) == 1:
    fh=sys.stdin
    sys.stdin = open('/dev/tty')
else:
    csvfile = sys.argv[1]
    if not os.path.exists(csvfile):
        usage()
    fh = open(csvfile,'r')

if len(sys.argv) >=3:
    if len(sys.argv[2]) > 1:
        usage()
    elif sys.argv[2] == 't':
        delim = '\t'
    else:
        delim = sys.argv[2]
else:
    delim = ','

def max_len(l1, l2):
    lendiff=len(l1) - len(l2)
    if lendiff >0:
        l2=l2+[None] * (lendiff)
    if lendiff <0:
        l1=l1+[None] * (-lendiff)
    return [max(a,b) for a, b in zip(l1, l2)]


csvreader=csv.reader(fh,delimiter=delim)
srch_txt=None

def highlight_part(text, substring, highlight_fmt = '\x1b[31;1m%s\x1b[0m'): #bold red

    if substring:
        return text.replace(substring, highlight_fmt%substring)
    else:
        return text

def prepare_data(rows=None, csvreader=csvreader):
    while rows is None or csvreader.line_num < rows:
        try:
            line = csvreader.next()
            contents.append([row_num_fmt%csvreader.line_num] + line) # -1 for header
        except:
            return

width=getwidth()
height=getheight()
start_row=0
start_col=0
row_shifts={'\n': height -3,
            ' ': height//2,
            #'B': height//2, #arrow down
            #'A': -height//2, #arrow up
            'B': 1,
            'A': -1,
            'G': 5000,
            }
col_shifts= {'C': width//2, #arrow right
             'D': -width//2, #arrow left
            }
#row_num_fmt='%04d:'
row_num_fmt='\x1b[33m%04d\x1b[0m'
header = [row_num_fmt%1] + csvreader.next()

hdrlengths= [len(x) for x in header]
contents=[]
response=None

prepare_data(start_row + height) #may need more data   

while response not in ['q', 'Q']:
    
    refresh = True 
    prev_start_row=start_row
    prev_start_col=start_col

    if response in row_shifts:
        if row_shifts[response]>0:
            prepare_data(start_row + height + row_shifts[response])
        start_row = max(0, min(csvreader.line_num-height+1, start_row+row_shifts[response]))

    if response in col_shifts:
        start_col = max(0, min(len(hdrstr)-width, start_col+col_shifts[response]))

    if response in ['g']: #top
        start_row = 0
    
    if response in ['/']: #search
        srch_txt = raw_input("Type string to be hilighted and then press Enter:")

    if (prev_start_row != start_row) or response is None: #may need to update col widths
        lengths=hdrlengths
        for line in contents[start_row:start_row+height-2]:
            lengths=max_len(lengths, [len(x) for x in line])
        hdrstr = ' '.join([s+' '*(l-len(s)) for (s, l) in zip(header, lengths)])
    
    if (prev_start_row != start_row) or (prev_start_col != start_col) or response in ['/', None]: #need to refresh
        print highlight_part( hdrstr[start_col:start_col+width], srch_txt )
        for line in contents[start_row:start_row+height-2]:
            linestr = ' '.join([s+' '*(l-len(s)) for (s, l) in zip(line, lengths)])
            print highlight_part( linestr[start_col:start_col+width], srch_txt)
        extra_rows = (height - len(contents) + start_row - 3) # clear screen in case file rows < height
        if extra_rows>0:
             print "\n" * extra_rows
    response=getch()
#    print "|", response,"|", "\n" #,dumpkey(response),"\n"

fh.close()
