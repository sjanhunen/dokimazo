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


    def addBook(self, name, abbreviation):
        self.cursor.execute(
            "INSERT INTO Book \
                (name, abbreviation) VALUES ('%s', '%s')" %
                (BOOKS[book], book))
        return self.cursor.lastrowid


    def addVerse(self, book, chapter, verse):
        self.cursor.execute(
            "INSERT OR REPLACE INTO Verse \
                (bookId, chapter, verse) VALUES \
                ((SELECT id FROM Book WHERE abbreviation='%s'), %d, %d)" %
                (book, chapter, verse))
        return self.cursor.lastrowid


    def addRoot(self, strongsId):
        self.cursor.execute(
            "INSERT OR REPLACE INTO Root \
                (id, strongsId) VALUES \
                ((SELECT id FROM Root WHERE strongsId=%d), %d)" %
                (strongsId, strongsId))
        return self.cursor.lastrowid


    def addInflection(self, tag):
        self.cursor.execute(
            "INSERT OR REPLACE INTO Inflection \
            (id, tag) VALUES \
            ((SELECT id FROM Inflection WHERE tag = '%s'), '%s')" %
            (tag, tag))
        return self.cursor.lastrowid


    def addForm(self, text, rootId, inflectionId):
        self.cursor.execute(
            "INSERT OR REPLACE INTO Form \
                (id, text, rootId, inflectionId) VALUES \
                ((SELECT id FROM Form WHERE text='%s'), '%s', %d, %d)" %
                (text, text, rootId, inflectionId))
        return self.cursor.lastrowid


    def addWord(self, verseId, formId):
        self.cursor.execute(
            "INSERT INTO Word \
                (verseId, formId) VALUES \
                (%d, %d)" %
                (verseId, formId))
        return self.cursor.lastrowid


BOOKS = {
    'MT':   'Matthew',          'MR':   'Mark',
    'LU':   'Luke',             'JOH':  'John',
    'AC':   'Acts',             'RO':   'Romans',
    '1CO':  '1 Corinthians',    '2CO':  '2 Corinthians',
    'GA':   'Galatians',        'EPH':  'Ephesians',
    'PHP':  'Philippians',      'COL':  'Colossians',
    '1TH':  '1 Thessalonians',  '2TH':  '2 Thessalonians',
    '1TI':  '1 Timothy',        '2TI':  '2 Timothy',
    'TIT':  'Titus',            'PHM':  'Philemon',
    'HEB':  'Hebrews',          'JAS':  'James',
    '1PE':  '1 Peter',          '2PE':  '2 Peter',
    '1JO':  '1 John',           '2JO':  '2 John',
    '3JO':  '3 John',           'JUDE': 'Jude',
    'RE':   'Revelation'
}

ORDER_OF_BOOKS = (
    'MT',   'MR',   'LU',   'JOH',  'AC',
    'RO',   '1CO',  '2CO',  'GA',   'EPH',
    'PHP',  'COL',  '1TH',  '2TH',  '1TI',
    '2TI',  'TIT',  'PHM',  'HEB',  'JAS',
    '1PE',  '2PE',  '1JO',  '2JO',  '3JO',
    'JUDE', 'RE'
)

# For details on parsing see http://koti.24.fi/jusalak/GreekNT/PARSINGS.TXT

with GntDb('gnt.db') as db:
    db.createSchema()

    for book in ORDER_OF_BOOKS:
        db.addBook(BOOKS[book], book)

    words = open(sys.argv[1]).read().split()
    book = 'EPH'

    verseId = None
    variation = False
    strongsId = []
    tag = None
    text = None
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
            strongsId.append(int(word))
        elif word.startswith('{'):
            # Part of speech
            tag = word.translate(None, '{}')
        elif word.startswith('('):
            # Not sure what this is
            pass
        elif word.find(':') != -1:
            # Verse
            (chapter, sep, verse) = word.partition(':')
            verseId = db.addVerse(book, int(chapter), int(verse))
        elif word.isalpha():
            # Greek word
            if text:
                #print "Adding %s (%d, %s)" % (text, strongsId[0], tag)
                db.addWord(verseId, db.addForm(text,
                    db.addRoot(strongsId[0]),
                    db.addInflection(tag)))
                strongsId = []
                tag = None
            text = word

    if text:
        #print "Adding %s (%d, %s)" % (text, strongsId[0], tag)
        db.addWord(verseId, db.addForm(text,
            db.addRoot(strongsId[0]),
            db.addInflection(tag)))
