Kanji Vocab
===========

Introduction
------------

The aim is to add Japanese words to a kanji writing deck (such as RTK), using data about known words collected by the MorphMan addon.

The Python code for the Kanji Vocab addon is licensed under the GNU AGPL, version 3 or later (the same as Anki itself).
http://www.gnu.org/licenses/agpl.html

The addon includes a dictionary derived from the JMdict dictionary file. JMdict is property of the Electronic Dictionary Research and Development Group, and is used in conformance with the Group's licence.
See http://www.edrdg.org/jmdict/j_jmdict.html

Tested with the old GitHub version of MorphMan, dated Dec 31 2014. This does not work with recent versions of Anki!
https://github.com/jre2/JapaneseStudy/tree/master/anki/plugins/morphman3

Not tested with ChangSpivey's improved version, but may be worth trying.
https://github.com/ChangSpivey/MorphMan

I intend to remove the MorphMan dependency because of licensing issues.

Instructions
------------

It is necessary to have a suitable version of MorphMan installed, and do a MorphMan Recalc before running this addon.

Copy KanjiVocab.py and the kanjivocab directory into the Anki addons directory. Edit config.py, at least for the first two entries:

* "noteType" is the name of the note type you wish to add the words to;
* "fieldKanji" is the name of the field containing only the kanji character being tested.

Add fields to your kanji deck for the new information. By default, the names are:

* "VocabQuestion" for the words with masked kanji (put this on the front of the card);
* "VocabResponse" for the answers to the questions (put this on the back of the card, ideally so that it appears in the same place as VocabQuestion);
* "VocabExtra" for words which would have more than one likely answer (put this on the back of the card).

Add CSS to your kanji deck to style the words as you like. There is an example in cards_example.css (so just copy that unless you have a different idea). Each word will have exactly one of the following classes:

* "kv_unique" for words with only one possible answer;
* "kv_likely" for words with only one likely answer;
* "kv_confuse" for words with more than one likely answer (by default these only appear in VocabExtra).

Also, each word will have exactly one of the following classes (with the ones listed first being higher priority):

* "kv_kanji_mature" for words where the kanji version is mature;
* "kv_kanji_known" for words where the kanji version is known;
* "kv_kana_mature" for words where the kana version is mature;
* "kv_kana_known" for words where the kana version is known;

Since they are separated like this, it makes sense to use text styles for one set and background colour for the other.

Restart Anki, and "Kanji Vocab Recalc" should appear on the Tools menu. When run, it overwrites the specified fields with the automatically-selected words.

