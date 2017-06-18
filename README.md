KanjiVocab
==========

Introduction
------------

This Anki addon adds Japanese words to a kanji writing deck (such as RTK), using known words from other decks.

Vocab card scanning is self-contained. Text scanning requires the "Japanese Support" addon. See https://ankiweb.net/shared/info/3918629684

The Python code is licensed under the GNU AGPL, version 3 or later (the same as Anki itself). See http://www.gnu.org/licenses/agpl.html

This addon includes a dictionary derived from the JMdict dictionary file. JMdict is property of the Electronic Dictionary Research and Development Group, and is used in conformance with the Group's licence. See http://www.edrdg.org/jmdict/j_jmdict.html

Instructions
------------

Always backup your collection before installing an addon that modifies it!

Copy KanjiVocab.py and the kanjivocab directory into the Anki addons directory. Edit config.py:

* "noteType" is the name of the note type you wish to add the words to;
* "fieldKanji" is the name of the field containing only the kanji character being tested;
* "scan" contains the info about what cards to scan - see the comments for details.

Add fields to your kanji deck for the new information. By default, the names are:

* "KanjiVocab question" for the words with masked kanji (put this on the front of the card);
* "KanjiVocab answer" for the answers to the questions (put this on the back of the card, ideally so that it appears in the same place as the question field);
* "KanjiVocab extra" for words which would have more than one likely answer (put this on the back of the card).

The above fields contain furigana, so add them using {{furigana:KanjiVocab question}} etc.

Add CSS to your kanji deck to style the words as you like. There is an example in cards_example.css (so just copy that unless you have a different idea). Each word will have exactly one of the following classes:

* "kv_unique" for words with only one possible answer;
* "kv_likely" for words with only one likely answer;
* "kv_confuse" for words with more than one likely answer (by default these only appear as "extra" words).

Also, each word will have exactly one of the following classes (with the ones listed first being higher priority):

* "kv_kanji_mature" for words where the kanji version is mature;
* "kv_kanji_known" for words where the kanji version is known;
* "kv_kana_mature" for words where the kana version is mature;
* "kv_kana_known" for words where the kana version is known;

Since they are separated like this, it makes sense to use text styles for one set and background colour for the other.

Restart Anki, and "Kanji Vocab Recalc" should appear on the Tools menu. When run, it overwrites the specified fields with the automatically-selected words.

