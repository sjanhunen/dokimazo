#!/usr/bin/python

import sys

text = open(sys.argv[1]).read()
words = text.split()

w = None
for word in words:
    verse = word.partition(':')
    if verse[1] == ':':
        print '%s %d:%d' % (sys.argv[1], int(verse[0]), int(verse[2]))
    else:
        if word.isdigit():
            w['number'].append(int(word))
        elif word.startswith('{'):
            w['part'] = word.translate(None, '{}')
        elif word.isalpha(): 
            if w:
                print w
            w = {'text': word, 'part': None, 'number': []}

print w
