# -*- coding: utf-8 -*-
# Copyright (C) 2015,2016,2017,2019  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import os, collections, json
from copy import deepcopy
from aqt import mw
from aqt.utils import *
from anki.utils import stripHTML
from anki.template import furigana

try:
    from importlib import reload
except:
    pass #Python 2 has reload built-in


def clean(fieldText):
    return stripHTML(fieldText).strip()


def updateKanjiVocab():
    output = _updateKanjiVocab()
    if output:
        showText(output)


def _updateKanjiVocab():
    from . import core as kvcore
    reload(kvcore)
    from . import config as kvconfig
    reload(kvconfig)
    from . import splitter as kvsplitter
    reload(kvsplitter)
    from . import gui as kvgui
    reload(kvgui)
    
    conf = deepcopy(kvconfig.config)
    output = ""
    
    try:
        splitter = kvsplitter.Splitter(conf["mecabArgs"])
    except Exception as e:
        conf["textScanError"] = str(e) + "\n"
        conf["textScanError"] += "Can't do sentence scan: check Japanese Support is installed and working properly"
    
    
    if os.path.exists(conf["pathConfigFile"]):
        try:
            with open(conf["pathConfigFile"]) as fp:
                fileConf = json.load(fp)
            output += "Loaded config file\n"
        except IOError as e:
            return output + "Can't read config file\n"
        except ValueError as e:
            return output + "Invalid JSON in config file\n"
        for key in conf["allowOverride"]:
            if key in fileConf:
                conf[key] = fileConf[key]
    else:
        output += "No config file found: loading defaults\n"
    
    if True:  #maybe make the GUI optional?
        
        settingsGui = kvgui.Settings(mw, conf, checkConfig)
        result = settingsGui.exec_()
        if result == QDialog.Rejected:
            return ""
        
        #save settings
        conf = settingsGui.conf
        fileConf = {}
        for key in conf["allowOverride"]:
            fileConf[key] = conf[key]
        try:
            with open(conf["pathConfigFile"], "w") as fp:
                json.dump(fileConf, fp)
            output += "Wrote config file\n"
        except IOError as e:
            return output + "Can't write config file\n"
        
        if not conf["run"]:
            return ""
    
    confError = checkConfig(mw, conf)
    if confError:
        return output + confError + "\n"
    
    
    if conf["gotFieldVocabQuestion"]:
        output += "Found vocab question field\n"
    else:
        output += "Warning: can't find vocab question field\n"
    if conf["gotFieldVocabResponse"]:
        output += "Found vocab response field\n"
    else:
        output += "Warning: can't find vocab response field\n"
    if conf["gotFieldVocabExtra"]:
        output += "Found vocab extra field\n"
    else:
        output += "Warning: can't find vocab extra field\n"
    
    
    freqFilter = conf["freqFilters"][conf["freqFilter"]]
    def questionFilterExtra(q):
        return q.kanjiKnown != kvcore.KNOWN_NOT or q.kanaKnown != kvcore.KNOWN_NOT or freqFilter(q)
    
    def questionFilter(q):
        return questionFilterExtra(q) and q.isLikely()
    
    conf["questionFilterExtra"] = questionFilterExtra
    if conf["allowAmbig"]:
        conf["questionFilter"] = questionFilterExtra
    else:
        conf["questionFilter"] = questionFilter
    
    
    mw.progress.start(label="Loading dictionary", immediate=True)
    try:
        words = kvcore.Words(conf)
    except IOError:
        return output + "Can't load dictionary"
    output += "Loaded dictionary\n"
    
    
    mw.progress.update(label="Marking known words")
    wordCounts = {} #[scanIndex][metric]
    notFound = {}   #[scanIndex][expression]
    for scanIndex in range(len(conf["scan"])):
        scanDic = conf["scan"][scanIndex]
        if scanDic.get("noteType", "") == "":
            continue
        wordCounts[scanIndex] = collections.Counter()
        notFound[scanIndex]   = collections.Counter()
        isVocab = (scanDic["scanType"] == "vocab")
        modelName = scanDic["noteType"]
        expressionFieldName = scanDic["expression"]
        readingFieldName = scanDic["reading"]
        model = mw.col.models.byName(modelName)
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
                wordCounts[scanIndex]["cells"] += 1
                known = kvcore.KNOWN_KNOWN
                if noteMature:
                    known = kvcore.KNOWN_MATURE
                expression = furigana.kanji(clean(note[expressionFieldName]))
                if isVocab:
                    if readingFieldName == "":
                        learned = words.learnPart(expression, known)
                    else:
                        reading = furigana.kana(clean(note[readingFieldName]))
                        learned = words.learnVocab(expression, reading, known)
                    learned = [(expression, learned)]
                else:
                    wordItems = set(splitter.analyze(expression))
                    learned = [(wordItem, words.learnPart(wordItem, known)) for wordItem in wordItems]
                for (expression, wordLearned) in learned:
                    wordCounts[scanIndex][wordLearned] += 1
                    if wordLearned == kvcore.LEARNED_NOTFOUND:
                        notFound[scanIndex][expression] += 1


    for scanIndex in sorted(wordCounts.keys()):
        wc = wordCounts[scanIndex]
        scanDic = conf["scan"][scanIndex]
        if scanDic["scanType"] == "vocab":
            output += "Done vocab scan on note type "
        else:
            output += "Done text scan on note type "
        output += '"%s" ' % scanDic["noteType"]
        if scanDic["reading"] == "":
            output += '(field "%s")\n' % (scanDic["expression"],)
        else:
            output += '(fields "%s", "%s")\n' % (scanDic["expression"], scanDic["reading"])
        msg = " Marked %d known words from %d active notes\n"
        output += msg % (wc[kvcore.LEARNED_YES], wc["cells"])
        msg = " (%d duplicates, %d with >1 possible word, %d not found)\n"
        output += msg % (wc[kvcore.LEARNED_ALREADY],
                         wc[kvcore.LEARNED_CONFUSE],
                         len(notFound[scanIndex]))  #LEARNED_NOTFOUND is way too big
    
    
    mw.progress.update(label="Creating questions")
    questions = kvcore.Questions(words)
    output += "Created questions\n"

    
    mw.progress.update(label="Updating notes")
    mw.checkpoint("KanjiVocab")  #set undo checkpoint (about to start changing stuff here)
    
    model = mw.col.models.byName(conf["noteType"])
    nids = mw.col.findNotes("mid:" + str(model["id"]))
    filledKanji = 0
    knownKanji = 0
    def hasKnown(text):
        return "_known" in text or "_mature" in text
    for nid in nids:
        note = mw.col.getNote(nid)
        kanji = clean(note[conf["fieldKanji"]])
        (fieldQ, fieldR, fieldX) = questions.getAnkiFields(kanji)
        filled = False
        known = False
        if conf["gotFieldVocabQuestion"]:
            note[conf["fieldVocabQuestion"]] = fieldQ
            if fieldQ != "":
                filled = True
            if hasKnown(fieldQ):
                known = True
        if conf["gotFieldVocabResponse"]:
            note[conf["fieldVocabResponse"]] = fieldR
            if fieldR != "":
                filled = True
            if hasKnown(fieldR):
                known = True
        if conf["gotFieldVocabExtra"]:
            note[conf["fieldVocabExtra"]] = fieldX
            if fieldX != "":
                filled = True
            if hasKnown(fieldX):
                known = True
        if filled:
            filledKanji += 1
        if known:
            knownKanji += 1
        note.flush()
    output += "Updated %d kanji notes\n (%d with word(s), %d with known word(s))\n" % \
        (len(nids), filledKanji, knownKanji)
    
    
    mw.progress.finish()
    return output + "Finished\n"
    

def checkConfig(mw, conf):
    model = mw.col.models.byName(conf["noteType"])
    if model is None:
        #shouldn't happen with GUI
        return "Can't find note type: " + conf["noteType"]
    
    fieldNames = [fld["name"] for fld in model["flds"]]
    
    if conf["fieldKanji"] not in fieldNames:
        #shouldn't happen with GUI
        return "Can't find kanji field: " + conf["fieldKanji"]

    if conf["freqFilter"] not in conf["freqFilters"]:
        #shouldn't happen with GUI
        return "Can't find freq filter: " + conf["freqFilter"]

    gotFieldQ = gotFieldR = gotFieldX = False
    if conf["fieldVocabQuestion"] in fieldNames:
        gotFieldQ = True
    if conf["fieldVocabResponse"] in fieldNames:
        gotFieldR = True
    if conf["fieldVocabExtra"] in fieldNames:
        gotFieldX = True
    if conf["numQuestions"] == 0 and conf["numExtra"] == 0:
        return "0 words requested: nothing to do"
    if not gotFieldQ and not gotFieldR and not gotFieldX:
        return "No fields found to update"
    if conf["numQuestions"] > 0 and not gotFieldQ and not gotFieldR:
        return "Requested %d questions, but not found question/answer fields" % conf["numQuestions"]
    if conf["numExtra"] > 0 and not gotFieldX:
        return "Requested %d extra answers, but not found extra answer field" % conf["numExtra"]
    conf["gotFieldVocabQuestion"] = gotFieldQ
    conf["gotFieldVocabResponse"] = gotFieldR
    conf["gotFieldVocabExtra"] = gotFieldX

    #Except the last one, these errors shouldn't happen with GUI
    for scanDic in conf["scan"]:
        if scanDic.get("noteType", "") == "":
            continue
        modelName = scanDic["noteType"]
        expressionFieldName = scanDic["expression"]
        readingFieldName = scanDic["reading"]
        model = mw.col.models.byName(modelName)
        if model is None:
            return "Can't find model %s to analyze" % modelName
        fieldNames = [fld["name"] for fld in model["flds"]]
        if expressionFieldName not in fieldNames:
            return "Can't find field %s in model %s to analyze" % (expressionFieldName, modelName)
        if readingFieldName != "" and readingFieldName not in fieldNames:
            return "Can't find field %s in model %s to analyze" % (readingFieldName, modelName)
        if scanDic["scanType"] == "text" and "textScanError" in conf:
            return conf["textScanError"]

