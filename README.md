KanjiVocab
==========

Introduction
------------

This Anki addon adds Japanese words to a kanji writing deck (such as RTK), using known words from other decks.

Vocab card scanning is self-contained. Text scanning requires the "Japanese Support" addon. See https://ankiweb.net/shared/info/3918629684

The Python code is licensed under the GNU AGPL, version 3 or later (the same as Anki itself). See http://www.gnu.org/licenses/agpl.html

This addon includes a dictionary derived from the JMdict dictionary file. JMdict is property of the Electronic Dictionary Research and Development Group, and is used in conformance with the Group's licence. See http://www.edrdg.org/jmdict/j_jmdict.html

Installation
------------

Always backup your collection before installing an addon that modifies it!

**Anki 2.1:** Copy the `kanjivocab` directory into the Anki `addons21` directory.

**Anki 2.0:** Copy `KanjiVocab.py` and the `kanjivocab` directory into the Anki `addons` directory.

Restart Anki, and "KanjiVocab..." should appear on the Tools menu. This opens a dialog with the various options.

Field Setup
-----------

Add fields to your kanji deck for the new information, named as follows:

* "KanjiVocabQuestion" for the words with masked kanji (put this on the front of the card);
* "KanjiVocabAnswer" for the answers to the questions (put this on the back of the card, ideally so that it appears in the same place as the question field);
* "KanjiVocabExtra" for words which would have more than one likely answer (put this on the back of the card).

The above fields contain furigana, so add them using {{furigana:KanjiVocabQuestion}} etc.

Note: These were renamed to remove spaces (as spaces make searching etc more awkward). You can rename existing fields within Anki. Apologies for any inconvenience.

CSS Setup
---------

Add CSS to your kanji deck to style the words as you like. There is an example in cards_example.css (so just copy that unless you have a different idea). Each word will have exactly one of the following classes:

* "kv_unique" for words with only one possible answer;
* "kv_likely" for words with only one likely answer;
* "kv_confuse" for words with more than one likely answer (by default these only appear as "extra" words).

Also, each word will have exactly one of the following classes (with the ones listed first being higher priority):

* "kv_kanji_mature" for words where the kanji version is mature;
* "kv_kanji_known" for words where the kanji version is known;
* "kv_kana_mature" for words where the kana version is mature;
* "kv_kana_known" for words where the kana version is known;
* "kv_kanji_inactive" for words where the kanji version was scanned from a new or suspended card;
* "kv_kana_inactive" for words where the kana version was scanned from a new or suspended card;
* "kv_unknown" for words which were not scanned.

Since they are separated like this, it makes sense to use text styles for one set and background colour for the other.

Settings Dialog
---------------

In the "Cards to update" tab:

* "Note type" is the note type you wish to add the words to.
* "Kanji field" is the name of the field containing only the kanji character being tested (used to decide which words to add to the card).
* "Dictionary words" allows words to be taken from the dictionary by frequency (based on JMdict priority tags), even if they did not appear in any scans.
* "Questions" is the maximum number of words with masked kanji to add to each card.
* "Extra answers" is the maximum number of extra words to add to each card.
* "Allow ambiguous questions" lets you choose whether to allow questions with more than one likely answer. Even if not, they can still appear as "extra".
* The "Fields to update" section shows whether the listed fields have been added correctly.

In the "Cards to scan" tab, each row can be set to a different scan:

* "Note type" is the note type you wish to scan. A note type can appear more than once with different options.
* "Scan type" can be "vocab" or "text". A vocab scan considers the expression and reading as-is (the reading is optional). A text scan splits the expression with MeCab (and does not use a reading).
* The other drop-downs let you select the expression and reading fields for each scan.
* The checkboxes let you choose whether each scan will consider new and suspended cards. Words from such cards will be prioritised above dictionary words, but not counted as "known".

