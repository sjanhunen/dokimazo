#!/usr/bin/python

import sys
import sqlite3

words = open(sys.argv[1]).read().split()
book = 'Eph'

# Create an sqlite database for storing gnt
#
# Table: Words (every word in order)
#   wordId   verseId    word    partOfSpeech    strongsId
# Table: Verses (every verse in order)
#   verseId     book    chapter verse   firstWord   lastWord
# Table: Strongs (every Strong's number in order)
#   strongsId   TBD

index = 0

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
        w['strongs'].append(int(word))
    elif word.startswith('{'):
        # Part of speech
        w['pos'] = word.translate(None, '{}')
    elif word.startswith('('):
        # Not sure what this is
        pass
    elif word.find(':') != -1:
        # Verse
        (chapter, sep, verse) = word.partition(':')
        chapter = int(chapter)
        verse = int(verse)
        print '%s %d:%d' % (book, chapter, verse)
    elif word.isalpha():
        # Greek word
        if w:
            print w
        w = {
            'word': word,
            'index': index,
            'book': book,
            'chapter': chapter,
            'verse': verse,
            'pos': None,
            'strongs': []}
        index = index + 1

if w:
    print w
