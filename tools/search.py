#!/usr/bin/python

import sys
import sqlite3

words = open(sys.argv[1]).read().split()
book = 'Eph'

# TODO: Review how mapping of text, words, and Strongs numbers works!

# Table: Text (textId PRIMARY)
#   textId, wordId, posId, verseId

# Table: Verses (prmary verseId)
#   verseId, book, chapter, verse

# Table: Words (every word in order)
#   wordId, word

# Table: PartsOfSpeech (posId PRIMARY)
#   posId, description

# Table StrongsVerses (one=>many)
#   strongsId   verseId

# Table: StrongsWords (one=>many)
#   strongsId   wordId

SCHEMA = (
    """DROP TABLE IF EXISTS Words""",
    """CREATE TABLE Words(
        wordId          INTEGER PRIMARY KEY AUTOINCREMENT,
        verseId         INTEGER,
        word            TEXT,
        partOfSpeech    TEXT,
        strongsId       INTEGER)""",
    """DROP TABLE IF EXISTS Verses""",
    """CREATE TABLE Verses(
        verseId         INTEGER PRIMARY KEY AUTOINCREMENT,
        book            TEXT,
        chapter         INTEGER,
        verse           INTEGER,
        firstWordId     INTEGER,
        lastWordId      INTEGER)""")

def addVerse(cursor, book, chapter, verse):
    cursor.execute(
        "INSERT INTO Verses (book, chapter, verse) VALUES ('%s', %d, %d)" %
        (book, chapter, verse))
    return cursor.lastrowid

def updateVerse(cursor, verseId, firstWordId, lastWordId):
    cursor.execute(
        "UPDATE Verses SET firstWordId=%d, lastWordId=%d WHERE verseId=%d" %
        (firstWordId, lastWordId, verseId))


def newWord(verseId):
    return {
        'verseId':      verseId,
        'word':         None,
        'partOfSpeech': None,
        'strongsId':    None}

def addWord():
    pass


# Connect to database and get a cursor
db = sqlite3.connect('gnt.db')
cursor = db.cursor()

# Create the tables
for statement in SCHEMA:
    cursor.execute(statement)



verseId = None
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
        w['strongsId'].append(int(word))
    elif word.startswith('{'):
        # Part of speech
        w['pos'] = word.translate(None, '{}')
    elif word.startswith('('):
        # Not sure what this is
        pass
    elif word.find(':') != -1:
        # Verse
        (chapter, sep, verse) = word.partition(':')
        verseId = addVerse(cursor, book, int(chapter), int(verse))
    elif word.isalpha():
        # Greek word
        if w:
            print w
        w = {
            'word': word,
            'book': book,
            'chapter': chapter,
            'verse': verse,
            'pos': None,
            'strongsId': []}

db.commit()
db.close()

if w:
    print w
