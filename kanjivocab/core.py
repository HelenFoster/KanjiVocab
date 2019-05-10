# -*- coding: utf-8 -*-
# Copyright (C) 2015,2017,2019  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import collections



KNOWN_MATURE = 0
KNOWN_KNOWN = 1
KNOWN_INACTIVE = 2
KNOWN_NOT = 3

LEARNED_YES = 0
LEARNED_ALREADY = 1
LEARNED_NOTFOUND = 2
LEARNED_CONFUSE = 3
LEARNED_NOTKNOWN = 4



def isKanji(ch):
    return ord(ch) >= 0x4E00 and ord(ch) <= 0x9FBF

def hideKanjiCombos(expression, questionChar):
    kanjiSet = set(filter(isKanji, expression))
    return [(kanji, expression.replace(kanji, questionChar)) for kanji in kanjiSet]

def ankiFurigana(expression, reading):
    e = expression
    r = reading
    
    i = 0
    while i < len(e) and i < len(r) and e[i] == r[i]:
        i += 1
    commonLeft = e[:i]
    e = e[i:]
    r = r[i:]
    
    iE = len(e) - 1
    iR = len(r) - 1
    while iE >=0 and iR >= 0 and e[iE] == r[iR]:
        iE -= 1
        iR -= 1
    commonRight = e[iE+1:]
    e = e[:iE+1]
    r = r[:iR+1]
    
    return commonLeft + " " + e + "[" + r + "]" + commonRight



class WordInfo:
    def __init__(self, pris=set(), nf=100000, kanjiKnown=KNOWN_NOT, kanaKnown=KNOWN_NOT):
        self.pris = pris
        self.nf = nf
        self.kanjiKnown = kanjiKnown
        self.kanaKnown = kanaKnown
    def learnKanji(self, known):
        result = self._learning(known)
        self.kanjiKnown = min(self.kanjiKnown, known)
        return result
    def learnKana(self, known):
        result = self._learning(known)
        self.kanaKnown = min(self.kanaKnown, known)
        return result
    def _learning(self, known):
        didntKnowKanji = self.kanjiKnown == KNOWN_NOT
        didntKnowKana = self.kanaKnown == KNOWN_NOT
        knowOneNow = known != KNOWN_NOT
        return didntKnowKanji and didntKnowKana and knowOneNow



class Question:
    def __init__(self, config, kanji, question, reading, wordInfo, sols, solsC):
        self._config = config
        self.kanji = kanji
        self.question = question
        self.reading = reading
        self.wordInfo = wordInfo
        self.kanjiKnown = wordInfo.kanjiKnown
        self.kanaKnown = wordInfo.kanaKnown
        self.pris = wordInfo.pris
        self.nf = wordInfo.nf
        self.sols = sols
        self.solsC = solsC
    def isUnique(self):
        return self.sols == 1
    def isLikely(self):
        return self.isUnique() or (self._config["questionMatchLikely"](self.wordInfo) and (self.solsC == 1))
    def __str__(self):
        result = self.question + " [" + self.reading + "]"
        result += "(" + ",".join(self.pris) + ") {"
        result += "K" + str(self.kanjiKnown) + str(self.kanaKnown) + ","
        result += "C" + str(self.sols) + ","
        result += "CC" + str(self.solsC)  + "}"
        return result.encode("utf-8")
    def ankiQuestion(self):
        result = ankiFurigana(self.question, self.reading)
        flags = []
        #one flag for known status
        if self.kanjiKnown == KNOWN_MATURE:
            flags.append("kv_kanji_mature")
        elif self.kanjiKnown == KNOWN_KNOWN:
            flags.append("kv_kanji_known")
        elif self.kanaKnown == KNOWN_MATURE:
            flags.append("kv_kana_mature")
        elif self.kanaKnown == KNOWN_KNOWN:
            flags.append("kv_kana_known")
        elif self.kanjiKnown == KNOWN_INACTIVE:
            flags.append("kv_kanji_inactive")
        elif self.kanaKnown == KNOWN_INACTIVE:
            flags.append("kv_kana_inactive")
        else:
            flags.append("kv_unknown")
        #and one flag for uniqueness
        if self.isUnique():
            flags.append("kv_unique")
        elif self.isLikely():
            flags.append("kv_likely")
        else:
            flags.append("kv_confuse")
        result = "<span class=\"" + " ".join(flags) + "\">" + result + "</span>"
        #if len(self.pris) > 0:
        #    result += "<span class=\"kv_pris\">(" + ",".join(self.pris) + ")</span">
        return result
    def ankiAnswer(self):
        return self.ankiQuestion().replace(self._config["questionChar"], self.kanji)


class Words:

    def __init__(self, config):
        self._dic = {}  #dic[expression][reading] = WordInfo(...)
        self._dicT = {} #dicT[expression][reading] = 1
        self._config = config
        
        countWords = 0
        linesMissed = 0
        with open(config["pathDicFile"], "rb") as f:
            for line in f:
                parts = line.decode("utf-8").rstrip("\r\n").split("\t")
                if not parts[0].startswith("#") and len(parts) == 3:
                    countWords += 1
                    expression = parts[0]
                    reading = parts[1]
                    pris = set() if parts[2] == "" else set(parts[2].split(","))
                    wordInfo = WordInfo(pris)
                    for pri in pris:
                        if pri.startswith("nf"):
                            wordInfo.nf = int(pri[2:])
                    self.add(expression, reading, wordInfo)
                else:
                    linesMissed += 1
    
    def add(self, expression, reading, wordInfo):
        if expression not in self._dic:
            self._dic[expression] = {}
        if reading not in self._dicT:
            self._dicT[reading] = {}
        self._dic[expression][reading] = wordInfo
        self._dicT[reading][expression] = 1
    
    def contains(self, expression, reading):
        dic = self._dic
        return expression in dic and reading in dic[expression]
    
    def _learnFull(self, expression, reading, kanjiKnown, kanaKnown):
        if self.contains(expression, reading):
            justLearnedKanji = self._dic[expression][reading].learnKanji(kanjiKnown)
            justLearnedKana  = self._dic[expression][reading].learnKana(kanaKnown)
            justLearned = justLearnedKanji or justLearnedKana
            return LEARNED_YES if justLearned else LEARNED_ALREADY
        else:
            #self.add(expression, reading, WordInfo(kanjiKnown=kanjiKnown, kanaKnown=kanaKnown))
            #return LEARNED_YES
            return LEARNED_NOTFOUND
    
    def _learnPartHelp(self, ERs, kanjiKnown, kanaKnown):
        if (len(ERs) == 1):
            (expression, reading) = ERs[0]
            return self._learnFull(expression, reading, kanjiKnown, kanaKnown)
        else:
            selectedER = None
            candidates = 0
            for (expression, reading) in ERs:
                wordInfo = self._dic[expression][reading]
                if self._config["learnMatchLikely"](wordInfo):
                    selectedER = (expression, reading)
                if self._config["learnMatchLikely"](wordInfo) or self._config["learnMatchConfuse"](wordInfo):
                    candidates += 1
            if selectedER is not None and candidates == 1:
                (expression, reading) = selectedER
                return self._learnFull(expression, reading, kanjiKnown, kanaKnown)
            else:
                return LEARNED_CONFUSE
    
    def learnPart(self, text, known):
        if known == KNOWN_NOT:
            return LEARNED_NOTKNOWN
        elif text in self._dic:
            expression = text
            readings = self._dic[expression]
            ERs = [(expression, reading) for reading in readings]
            return self._learnPartHelp(ERs, known, KNOWN_NOT)
        elif text in self._dicT:
            reading = text
            expressions = self._dicT[reading]
            ERs = [(expression, reading) for expression in expressions]
            return self._learnPartHelp(ERs, KNOWN_NOT, known)
        else:
            return LEARNED_NOTFOUND
    
    def learnVocab(self, expression, reading, known):
        if known == KNOWN_NOT:
            return LEARNED_NOTKNOWN
        elif expression == reading or reading == "":
            return self.learnPart(expression, known)
        else:
            return self._learnFull(expression, reading, known, known)
    
    def __iter__(self):
        dic = self._dic
        for expression in dic:
            for reading in dic[expression]:
                wordInfo = dic[expression][reading]
                yield (expression, reading, wordInfo)


class Questions:

    def __init__(self, words):
        self._dic = {} #dic[kanji][(question, reading)] = WordInfo(...)
        self._counts = collections.Counter() #counts[(question, reading)]
        self._countsC = collections.Counter()
        self._config = words._config
        for (expression, reading, wordInfo) in words:
            for (kanji, question) in hideKanjiCombos(expression, self._config["questionChar"]):
                self.add(kanji, question, reading, wordInfo)

    def add(self, kanji, question, reading, wordInfo):
        dic = self._dic
        QR = (question, reading)
        if not kanji in dic:
            dic[kanji] = {}
        if not QR in dic[kanji]:
            dic[kanji][QR] = wordInfo
            self._counts[QR] += 1
            if self._config["questionMatchConfuse"](wordInfo):
                self._countsC[QR] += 1
    
    def getQuestions(self, kanji):
        dic = self._dic
        result = []
        for QR in dic.get(kanji, []):
            wordInfo = dic[kanji][QR]
            sols = self._counts[QR]
            solsC = self._countsC[QR]
            (question, reading) = QR
            result.append(Question(self._config, kanji, question, reading, wordInfo, sols, solsC))
        return result
    
    def getSomeQuestions(self, kanji, limit, fFilter=None, fSort=None):
        qs = self.getQuestions(kanji)
        qs = [q for q in filter(fFilter, qs)]
        qs.sort(key=fSort)
        return qs[:limit]
    
    def getAnkiFields(self, kanji):
        numQs = self._config["numQuestions"]
        numQsX = self._config["numExtra"]
        qFilter = self._config["questionFilter"]
        qFilterX = self._config["questionFilterExtra"]
        qKey = self._config["questionKey"]
        qKeyX = self._config["questionKeyExtra"]
        
        qs = self.getSomeQuestions(kanji, numQs, qFilter, qKey)
        xs = self.getSomeQuestions(kanji, numQs+numQsX, qFilterX, qKeyX)
        ankiQs = [q.ankiQuestion() for q in qs]
        ankiRs = [q.ankiAnswer() for q in qs]
        ankiXs = [q.ankiAnswer() for q in xs]
        ankiXs = [x for x in ankiXs if x not in ankiRs][:numQsX]
        return (u"　".join(ankiQs), u"　".join(ankiRs), u"　".join(ankiXs))
