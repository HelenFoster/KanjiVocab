# -*- coding: utf-8 -*-
# Copyright (C) 2015  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


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
    
    
    fieldsToAnalyze = []
    for (modelName, fieldName, doSplit) in conf["analyze"]:
        model = mw.col.models.byName(modelName)
        if model is None:
            result += "Warning: can't find model %s to analyze: please edit config.py to fix\n" % modelName
            continue
        fieldNames = [fld[u"name"] for fld in model["flds"]]
        if fieldName not in fieldNames:
            result += "Warning: can't find field %s in model %s to analyze: please edit config.py to fix\n" % (fieldName, modelName)
            continue
        fieldsToAnalyze.append((model, fieldName, doSplit))
    if not fieldsToAnalyze:
        result += "Warning: can't find any fields to analyze: please edit config.py if you want them\n"
    
    
    mw.progress.update(label="Loading dictionary")
    try:
        words = kanjivocab.core.Words(conf)
    except IOError:
        return result + "Can't load dictionary"
    result += "Loaded dictionary\n"
    
    
    mw.progress.update(label="Marking known words")
    noteCount = 0
    for (model, fieldName, doSplit) in fieldsToAnalyze:
        nids = mw.col.findNotes("mid:" + str(model["id"]))
        noteCount += len(nids)
        for nid in nids:
            note = mw.col.getNote(nid)
            noteActive = False
            noteMature = False
            for card in note.cards():
                cardActive = card.queue not in (-1, 0) #not suspended or new
                cardMature = cardActive and card.ivl >= 21 #TODO: configurable?
                noteActive = noteActive or cardActive
                noteMature = noteMature or cardMature
            if noteMature:
                words.learnPart(note[fieldName], kanjivocab.core.KNOWN_MATURE)
            elif noteActive:
                words.learnPart(note[fieldName], kanjivocab.core.KNOWN_KNOWN)
    result += "Marked known words from %d cells\n" % noteCount
    
    
    mw.progress.update(label="Creating questions")
    questions = kanjivocab.core.Questions(words)
    result += "Created questions\n"

    
    mw.progress.update(label="Updating notes")
    
    nids = mw.col.findNotes("mid:" + str(kanjiModelID))
    result += "%d notes to be updated\n" % len(nids)
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
    

