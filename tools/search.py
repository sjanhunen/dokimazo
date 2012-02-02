#!/usr/bin/python

import sys
import sqlite3

words = open(sys.argv[1]).read().split()
book = 'Eph'

# TODO
#   * understand multiple Strong's numbers per word
#   * study http://koti.24.fi/jusalak/GreekNT/PARSINGS.TXT

# Strong's numbers map only to 'root' words. So, many words in the original
# actually have the same Strong's number. This is where part of speech, 
# tense, number, etc come into play

# Which are one-to-one and one-to-many?
# Table Verse (every verse in order)
#   id, book, chapter, verse
# Table Word (every word in order)
#   id, verseId, formId
# Table Form (every Greek form in the NT)
#   id, word, lemmaId, inflectionId
# Table Lemma (or should we call it Root?)
#   id, strongsId
# Table Strongs
#   id, lemmaId
# Table Inflection
#   id, part, gender, case, etc.

# Table Lexeme
#   id, strongsNumber

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
