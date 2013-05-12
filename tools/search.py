#!/usr/bin/python

import sys
import sqlite3

# TODO: find a better home for this
def sqlTuple(v):
    if isinstance(v, int):
        return "(%s)" % str(v)
    else:
        if len(v) == 1:
            return "(%s)" % str(v[0])
        else:
            return str(tuple(v))


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

    def verses(self, book):
        return self._querySet(
            "SELECT id from Verse WHERE bookId is \
            (SELECT id from Book WHERE abbreviation is '%s')" % book)

    def words(self, verses):
        return self._querySet(
            "SELECT id from Word WHERE verseId in %s" % sqlTuple(verses))

    def forms(self, words):
        return self._querySet(
            "SELECT formId from Word WHERE id in %s" % sqlTuple(words))

    def text(self, forms):
        return self._querySet(
            "SELECT text from Form WHERE id in %s" % sqlTuple(forms))

    def _querySet(self, query):
        #print("_querySet: " + query)
        return set([r[0] for r in self.cursor.execute(query)])

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


class GntParser:
    def __init__(self, listener):
        self.listener = listener
        self.word = None
        self.variation = False
        self.nextWord()

    def nextWord(self):
        if self.word:
            self.listener.nextWord(self.word, self.strongsId[0], self.tag)
        self.word = None
        self.strongsId = []
        self.tag = None

    def parse(self, word):
        # For details see http://koti.24.fi/jusalak/GreekNT/PARSINGS.TXT
        if self.variation:
            # Skip over variants of the text
            if word == ':END':
                self.variation = False
        elif word is None:
            self.nextWord()
        elif word == 'VAR:':
            # Textual variant
            self.variation = True
        elif word.isdigit():
            # Strong's number
            self.strongsId.append(int(word))
        elif word.startswith('{'):
            # Part of speech
            self.tag = word.translate(None, '{}')
        elif word.startswith('('):
            # Not sure what this is
            pass
        elif word.find(':') != -1:
            # Verse
            self.nextWord()
            (chapter, sep, verse) = word.partition(':')
            listener.nextVerse(int(chapter), int(verse))
        elif word.isalpha():
            # Greek word
            self.nextWord()
            self.word = word


class GntParseListener:
    def __init__(self, db):
        self.db = db
        self.verseId = None
        self.book = None

    def nextBook(self, book):
        #print "nextBook: %s" % book
        self.book = book

    def nextVerse(self, chapter, verse):
        #print "nextVerse: %d:%d" % (chapter, verse)
        self.verseId = db.addVerse(self.book, chapter, verse)

    def nextWord(self, word, strongsId, tag):
        #print "nextWord: %s, %d, %s" % (word, strongsId, tag)
        db.addWord(self.verseId, db.addForm(word,
            db.addRoot(strongsId),
            db.addInflection(tag)))


with GntDb('gnt.db') as db:
    db.createSchema()

    for book in ORDER_OF_BOOKS:
        db.addBook(BOOKS[book], book)

    listener = GntParseListener(db)
    parser = GntParser(listener)
    listener.nextBook('EPH')

    words = open(sys.argv[1]).read().split()
    for word in words:
        parser.parse(word)
    parser.parse(None)

    print db.words(set([1, 2]))
    # The forms in verse 1
    print db.text(db.forms(db.words([1,])))
    # The forms in verse 2
    print db.text(db.forms(db.words([2,])))
    # The forms common to verses 1 and 2
    print db.text(db.forms(db.words(1)) & db.forms(db.words(2)))
