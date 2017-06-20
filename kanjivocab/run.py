# -*- coding: utf-8 -*-
# Copyright (C) 2015,2016,2017  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import os, collections, json
from copy import deepcopy
from aqt import mw
from aqt.utils import *


def updateKanjiVocab():
    output = _updateKanjiVocab()
    if output:
        showText(output)


def _updateKanjiVocab():
    import kanjivocab.core
    reload(kanjivocab.core)
    import kanjivocab.config
    reload(kanjivocab.config)
    import kanjivocab.splitter
    reload(kanjivocab.splitter)
    import kanjivocab.gui
    reload(kanjivocab.gui)
    
    conf = deepcopy(kanjivocab.config.config)
    output = ""
    
    try:
        splitter = kanjivocab.splitter.Splitter(conf["mecabArgs"])
    except Exception as e:
        conf["textScanError"] = e.message + "\n"
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
            if fileConf.has_key(key):
                conf[key] = fileConf[key]
    else:
        output += "No config file found: loading defaults\n"
    
    if True:  #maybe make the GUI optional?
        
        settingsGui = kanjivocab.gui.Settings(mw, conf, checkConfig)
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
    

    model = mw.col.models.byName(conf["noteType"])
    kanjiModelID = model["id"]
    
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
        output += "Warning: can't find vocab extra field"
    
    
    if not conf["avoidAmbig"]:
        conf["questionFilter"] = conf["questionFilterExtra"]
    
    
    mw.progress.start(label="Loading dictionary", immediate=True)
    try:
        words = kanjivocab.core.Words(conf)
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
                known = kanjivocab.core.KNOWN_KNOWN
                if noteMature:
                    known = kanjivocab.core.KNOWN_MATURE
                if isVocab:
                    expression = note[expressionFieldName]
                    if readingFieldName == "":
                        learned = words.learnPart(expression, known)
                    else:
                        learned = words.learnVocab(expression, note[readingFieldName], known)
                    learned = [(expression, learned)]
                else:
                    wordItems = set(splitter.analyze(note[expressionFieldName]))
                    learned = [(wordItem, words.learnPart(wordItem, known)) for wordItem in wordItems]
                for (expression, wordLearned) in learned:
                    wordCounts[scanIndex][wordLearned] += 1
                    if wordLearned == kanjivocab.core.LEARNED_NOTFOUND:
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
        output += msg % (wc[kanjivocab.core.LEARNED_YES], wc["cells"])
        msg = " (%d duplicates, %d with >1 possible word, %d not found)\n"
        output += msg % (wc[kanjivocab.core.LEARNED_ALREADY],
                         wc[kanjivocab.core.LEARNED_CONFUSE],
                         len(notFound[scanIndex]))  #LEARNED_NOTFOUND is way too big
    
    
    mw.progress.update(label="Creating questions")
    questions = kanjivocab.core.Questions(words)
    output += "Created questions\n"

    
    mw.progress.update(label="Updating notes")
    mw.checkpoint("KanjiVocab")  #set undo checkpoint (about to start changing stuff here)
    
    nids = mw.col.findNotes("mid:" + str(kanjiModelID))
    output += "%d kanji notes to be updated\n" % len(nids)
    for nid in nids:
        note = mw.col.getNote(nid)
        kanji = note[conf["fieldKanji"]]
        (fieldQ, fieldR, fieldX) = questions.getAnkiFields(kanji)
        if conf["gotFieldVocabQuestion"]:
            note[conf["fieldVocabQuestion"]] = fieldQ
        if conf["gotFieldVocabResponse"]:
            note[conf["fieldVocabResponse"]] = fieldR
        if conf["gotFieldVocabExtra"]:
            note[conf["fieldVocabExtra"]] = fieldX
        note.flush()
    
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
            return textScanError

