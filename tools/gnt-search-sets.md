Design review for GNT search sets
---------------------------------

All query results returned as sets (immutable collections of unique items).

The GNT can be expressed as sets at different levels of abstraction
- words - subset of the text
- forms - subset of inflected forms
- roots - subset of Strongs roots
- verses - subset of verses
- pos - subset of parts of speech

Fundamental operations:
- verses(book) - set verses present in a given book (could refine to citation)
- words(verses) - set of words present in set of verses
- forms(words) - set of Greek forms used in set of words
- text(forms) - textual representation of Greek forms

Some Thoughts on Use Cases
--------------------------

A search will typically start at one level of abstraction and move to another.
Functions must be used to convert between sets at different levels of
abstraction. The result is always a set (contains no duplicates). This means
that some functions are necessarily one way.

For example, to find all the roots in Eph

    roots(words(verses('eph')))

Set theory can be used on sets at the same level of abstraction. See the set
operators for Python. For example, to find all roots common to Eph and Col

    roots(words(verses('eph'))) & roots(words(verses('col')))

Or to find all roots in Eph and Col

    roots(words(verses('eph') | verses('col')))

Interesting possibilities exist. This would find all root verbs in Eph

    roots(forms(pos('VERB'))) & roots(forms(words(verses('eph'))))

To find all verses in Mat that contain G4172

    verses('mat') & verses(words(forms('G4172')))

We may also consider abbreviated functions. So the previous search may look like

    V('mat') & V(W(F('G4172')))