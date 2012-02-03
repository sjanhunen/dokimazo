#!/usr/bin/python

import sys
import sqlite3


class GntDb:
    def __init__(self, filename):
        self.SCHEMA = (
            """DROP TABLE IF EXISTS Book""",
            # Every GNT book in order by id
            """CREATE TABLE Book(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT,
                abbreviation    TEXT)""",
            """DROP TABLE IF EXISTS Verse""",
            # Every GNT verse in order by id
            """CREATE TABLE Verse(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                bookId          INTEGER,
                chapter         INTEGER,
                verse           INTEGER)""",
            """DROP TABLE IF EXISTS Word""",
            # Every GNT word (of the Greek text) in order by id
            """CREATE TABLE Word(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                verseId         INTEGER,
                formId          INTEGER)""",
            """DROP TABLE IF EXISTS Form""",
            # Each unique inflected form of a root in the GNT
            # TODO: is there a better name for 'text'?
            """CREATE TABLE Form(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                text            TEXT,
                rootId          INTEGER,
                inflectionId    INTEGER)""",
            """DROP TABLE IF EXISTS Root""",
            # Each unique root form in the GNT
            """CREATE TABLE Root(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                strongsId       INTEGER)""",
            """DROP TABLE IF EXISTS Inflection""",
            # Each possible type of inflection used on forms
            # TODO: Eventually we want Inflection(id, part, gender, case, etc)
            """CREATE TABLE Inflection(
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                tag             TEXT)"""
        )
        self.filename = filename


    def __enter__(self):
        self.db = sqlite3.connect(self.filename)
        self.cursor = self.db.cursor()
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.db.commit()
        self.db.close()


    def createSchema(self):
        for statement in self.SCHEMA:
            self.cursor.execute(statement)


with GntDb('gnt.db') as db:
    db.createSchema()


# For details on parsing see http://koti.24.fi/jusalak/GreekNT/PARSINGS.TXT

words = open(sys.argv[1]).read().split()
book = 'Eph'

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

if w:
    print w
