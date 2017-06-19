# -*- coding: utf-8 -*-
# Copyright (C) 2015,2016,2017  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html



import os
from aqt import mw
from kanjivocab.core import KNOWN_NOT

config = {}



#CHANGE THESE TO MATCH YOUR DECK (AND/OR CHANGE YOUR DECK TO MATCH THESE)

#Update cards with this note type.
config["noteType"] = u"Heisig"

#Field used to select cards to update. Should contain only the kanji character being tested.
config["fieldKanji"] = u"Kanji"

#Words with masked kanji on the front of the card. FIELD WILL BE OVERWRITTEN.
config["fieldVocabQuestion"] = u"KanjiVocab question"

#Answers to the above questions on the back of the card. FIELD WILL BE OVERWRITTEN. 
config["fieldVocabResponse"] = u"KanjiVocab answer"

#Extra vocab on the back of the card. FIELD WILL BE OVERWRITTEN.
config["fieldVocabExtra"] = u"KanjiVocab extra"



#Cards to scan for known words.
#A note type can appear more than once, with a different field.
#"scanType" can be "vocab" or "text".
#The "vocab" scan considers the expression and reading as-is.
#  If you don't have a reading field, set "reading" to "" (empty string).
#The "text" scan splits the expression with MeCab.
#  ("reading" should be an empty string)
config["scan"] = [
    {
        "noteType": "vocab",
        "scanType": "vocab",
        "expression": "expression",
        "reading": "kana"
    },
    {
        "noteType": "Nayrs Japanese Core5000",
        "scanType": "text",
        "expression": "Expression",
        "reading": ""
    }
]



config["numQuestions"] = 4
config["numExtra"] = 4
config["avoidAmbig"] = True
config["numScans"] = 6
config["questionChar"] = u"〇"

config["allowOverride"] = ["noteType", "fieldKanji", "numQuestions", "numExtra", "avoidAmbig", "scan"]
config["pathDicFile"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jmdict_freqs.txt")
config["pathConfigFile"] = os.path.normpath(os.path.join(mw.col.media.dir(), "../KanjiVocab.json"))

#Using '@' to split results.
config["mecabArgs"] = ['--node-format="%m@%f[6]@"']

def wordIsP1(wordInfo):
    p = wordInfo.pris
    return ("gai1" in p or "ichi1" in p or "news1" in p or "spec1" in p)

def wordIsP1orP2(wordInfo):
    return (len(wordInfo.pris) > 0)

def questionFilter(q):
    return questionFilterExtra(q) and q.isLikely()

def questionKey(q):
    return (q.kanjiKnown, q.kanaKnown, q.nf)

def questionFilterExtra(q):
    return q.kanjiKnown != KNOWN_NOT or q.kanaKnown != KNOWN_NOT or q.nf <= 10

config["questionMatchLikely"] = wordIsP1
config["questionMatchConfuse"] = wordIsP1orP2
config["learnMatchLikely"] = wordIsP1
config["learnMatchConfuse"] = wordIsP1
config["questionKey"] = questionKey
config["questionKeyExtra"] = questionKey
config["questionFilter"] = questionFilter
config["questionFilterExtra"] = questionFilterExtra
