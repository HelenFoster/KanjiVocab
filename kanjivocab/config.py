# -*- coding: utf-8 -*-
# Copyright (C) 2015  Helen Foster
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
config["fieldVocabQuestion"] = u"VocabQuestion"

#Answers to the above questions on the back of the card. FIELD WILL BE OVERWRITTEN. 
config["fieldVocabResponse"] = u"VocabResponse"

#Extra vocab on the back of the card. FIELD WILL BE OVERWRITTEN.
config["fieldVocabExtra"] = u"VocabExtra"

#Fields to analyze for known words,
#as a list of (note type, field name, split with MeCab?)
#but splitting is not supported yet - so only use vocab decks for the moment!
config["analyze"] = [
    ("vocab", "expression", False),
    ("vocab", "kana", False),
]



config["numQuestions"] = 4
config["numQuestionsExtra"] = 4
config["questionChar"] = u"〇"

config["pathDicFile"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "jmdict_freqs.txt")

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
