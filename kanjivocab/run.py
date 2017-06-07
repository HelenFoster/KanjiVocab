# -*- coding: utf-8 -*-
# Copyright (C) 2015  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import collections
from aqt import mw
from aqt.utils import *


def updateKanjiVocab():
    mw.progress.start(immediate=True)
    result = _updateKanjiVocab()
    mw.progress.finish()
    showText(result)


def _updateKanjiVocab():
    import kanjivocab.core
    reload(kanjivocab.core)
    import kanjivocab.config
    reload(kanjivocab.config)
    import kanjivocab.splitter
    reload(kanjivocab.splitter)
    
    conf = kanjivocab.config.config
    result = ""
    
    model = mw.col.models.byName(conf["noteType"])
    if model is None:
        return result + "Can't find note type: " + conf["noteType"] + ": please edit config.py\n"
    result += "Found note type: " + conf["noteType"] + "\n"
    
    kanjiModelID = model["id"]
    fieldNames = [fld[u"name"] for fld in model["flds"]]
    if conf["fieldKanji"] in fieldNames:
        result += "Found kanji field\n"
    else:
        return result + "Can't find kanji field: please edit config.py\n"
    
    gotFieldQ = gotFieldR = gotFieldX = False
    if conf["fieldVocabQuestion"] in fieldNames:
        result += "Found vocab question field\n"
        gotFieldQ = True
    else:
        result += "Warning: can't find vocab question field: please edit config.py if you want it\n"
    if conf["fieldVocabResponse"] in fieldNames:
        result += "Found vocab response field\n"
        gotFieldR = True
    else:
        result += "Warning: can't find vocab response field: please edit config.py if you want it\n"
    if conf["fieldVocabExtra"] in fieldNames:
        result += "Found vocab extra field\n"
        gotFieldX = True
    else:
        result += "Warning: can't find vocab extra field: please edit config.py if you want it\n"
    if not gotFieldQ and not gotFieldR and not gotFieldX:
        return result + "No fields to update: please edit config.py\n"
    
    
    if conf["scanText"]:
        try:
            splitter = kanjivocab.splitter.Splitter(conf["mecabArgs"])
        except Exception as e:
            result += e.message + "\n"
            result += "Warning: Can't do sentence scan: check Japanese Support is installed and working properly\n"
            conf["scanText"] = []
    
    toAnalyze1 = [(True,) + x for x in conf["scanVocab"]]
    toAnalyze1 += [(False,) + x + (None,) for x in conf["scanText"]]
    toAnalyze = []
    for (isVocab, modelName, expressionFieldName, readingFieldName) in toAnalyze1:
        model = mw.col.models.byName(modelName)
        if model is None:
            result += "Warning: can't find model %s to analyze: please edit config.py to fix\n" % modelName
            continue
        fieldNames = [fld[u"name"] for fld in model["flds"]]
        if expressionFieldName not in fieldNames:
            result += "Warning: can't find field %s in model %s to analyze: please edit config.py to fix\n" % (expressionFieldName, modelName)
            continue
        if readingFieldName is not None and readingFieldName not in fieldNames:
            result += "Warning: can't find field %s in model %s to analyze: please edit config.py to fix\n" % (readingFieldName, modelName)
            continue
        toAnalyze.append((isVocab, model, expressionFieldName, readingFieldName)) #note: model not modelName
    
    if not toAnalyze:
        result += "Warning: can't find any fields to analyze: please edit config.py if you want them\n"
    
    
    mw.progress.update(label="Loading dictionary")
    try:
        words = kanjivocab.core.Words(conf)
    except IOError:
        return result + "Can't load dictionary"
    result += "Loaded dictionary\n"
    
    
    mw.progress.update(label="Marking known words")
    wordCounts = {True: collections.Counter(), False: collections.Counter()} #[isVocab][metric]
    notFound = {True: collections.Counter(), False: collections.Counter()} #[isVocab][expression]
    for (isVocab, model, expressionFieldName, readingFieldName) in toAnalyze:
        nids = mw.col.findNotes("mid:" + str(model["id"]))
        for nid in nids:
            note = mw.col.getNote(nid)
            noteActive = False
            noteMature = False
            for card in note.cards():
                cardActive = card.queue not in (-1, 0) #not suspended or new
                cardMature = cardActive and card.ivl >= 21 #TODO: configurable?
                noteActive = noteActive or cardActive
                noteMature = noteMature or cardMature
            if noteActive:
                wordCounts[isVocab]["cells"] += 1
                known = kanjivocab.core.KNOWN_KNOWN
                if noteMature:
                    known = kanjivocab.core.KNOWN_MATURE
                if isVocab:
                    expression = note[expressionFieldName]
                    if readingFieldName is None:
                        learned = words.learnPart(expression, known)
                    else:
                        learned = words.learnVocab(expression, note[readingFieldName], known)
                    learned = [(expression, learned)]
                else:
                    wordItems = set(splitter.analyze(note[expressionFieldName]))
                    learned = [(wordItem, words.learnPart(wordItem, known)) for wordItem in wordItems]
                for (expression, wordLearned) in learned:
                    wordCounts[isVocab][wordLearned] += 1
                    if wordLearned == kanjivocab.core.LEARNED_NOTFOUND:
                        notFound[isVocab][expression] += 1
    
    
    def wordStats(msg1, isVocab):
        wc = wordCounts[isVocab]
        msg = msg1 % (wc[kanjivocab.core.LEARNED_YES], wc["cells"])
        msg2 = " (%d duplicates, %d with >1 possible word, %d not found)\n"
        msg += msg2 % (wc[kanjivocab.core.LEARNED_ALREADY],
                       wc[kanjivocab.core.LEARNED_CONFUSE],
                       len(notFound[isVocab]))  #LEARNED_NOTFOUND is way too big
        return msg
    if conf["scanVocab"]:
        result += wordStats("Marked %d known words from %d vocab notes\n", True)
    if conf["scanText"]:
        result += wordStats("Marked %d known words from %d text cells\n", False)
    
    
    mw.progress.update(label="Creating questions")
    questions = kanjivocab.core.Questions(words)
    result += "Created questions\n"

    
    mw.progress.update(label="Updating notes")
    
    nids = mw.col.findNotes("mid:" + str(kanjiModelID))
    result += "%d kanji notes to be updated\n" % len(nids)
    for nid in nids:
        note = mw.col.getNote(nid)
        kanji = note[conf["fieldKanji"]]
        (fieldQ, fieldR, fieldX) = questions.getAnkiFields(kanji)
        if gotFieldQ:
            note[conf["fieldVocabQuestion"]] = fieldQ
        if gotFieldR:
            note[conf["fieldVocabResponse"]] = fieldR
        if gotFieldX:
            note[conf["fieldVocabExtra"]] = fieldX
        note.flush()
    
    return result + "Finished\n"
    

