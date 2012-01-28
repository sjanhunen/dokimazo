#!/usr/bin/python

import sys

text = open(sys.argv[1]).read()
words = text.split()

w = None
variation = False
for word in words:
    if variation:
        # Skip over variants of the text
        if word == ':END':
            variation = False
        continue

    if word == 'VAR:':
        # Textual variant
        variation = True
    elif word.isdigit():
        # Strong's number
        w['number'].append(int(word))
    elif word.startswith('{'):
        # Part of speech
        w['pos'] = word.translate(None, '{}')
    elif word.startswith('('):
        # Not sure what this is
        pass
    elif word.find(':') != -1:
        # Verse
        verse = word.partition(':')
        print '%s %d:%d' % (sys.argv[1], int(verse[0]), int(verse[2]))
    elif word.isalpha():
        # Greek text
        if w:
            print w
        w = {'text': word, 'pos': None, 'number': []}

print w
