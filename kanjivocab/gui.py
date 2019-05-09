# -*- coding: utf-8 -*-
# Copyright (C) 2017,2019  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from aqt.qt import *
from copy import deepcopy


class ComboBoxKV(QComboBox):
    
    def setup(self, dic, key, callback):
        self.setCurrentByText(dic.get(key, ""))
        callback(self.currentText())
        self.currentIndexChanged[str].connect(callback)
        
    def setCurrentByText(self, text, defaultIndex=0):
        index = self.findText(text)
        if index == -1:
            index = defaultIndex
        self.setCurrentIndex(index)


class Count:
    
    def __init__(self, start=0, step=1):
        self.x = start
        self.step = step
    
    def next(self):
        x = self.x
        self.x = x + self.step
        return x


class Settings(QDialog):

    def __init__(self, mw, conf, checkConfig):

        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.conf = deepcopy(conf)
        self.checkConfig = checkConfig

        self.resize(780, 400)
        self.setWindowTitle("KanjiVocab settings")
        
        self.layoutOuter = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.layoutOuter.addWidget(self.tabs)
        self.tabUpdate = QWidget()
        self.tabScan = QWidget()
        self.tabs.addTab(self.tabUpdate, "Cards to update")
        self.tabs.addTab(self.tabScan, "Cards to scan")
        
        
        self.layoutUpdate = QGridLayout(self.tabUpdate)
        
        r = Count()
        self.layoutUpdate.addWidget(
            QLabel(text="Note type"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Kanji field (the kanji character by itself)"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Dictionary words (not scanned)"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Questions"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Extra answers"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Allow ambiguous questions"), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text="<b>Fields to update (the existing contents will be lost!)</b>"), 
            r.next(), 0, 1, 2)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabQuestion"]), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabResponse"]), r.next(), 0)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabExtra"]), r.next(), 0)
        
        self.pickNoteType = ComboBoxKV()
        self.pickFieldKanji = ComboBoxKV()
        self.pickFreqFilter = ComboBoxKV()
        self.pickNumQuestions = QSpinBox()
        self.pickNumExtra = QSpinBox()
        self.pickAllowAmbig = QCheckBox()
        self.foundFieldQuestion = QLabel()
        self.foundFieldAnswer = QLabel()
        self.foundFieldExtra = QLabel()
        
        r = Count()
        self.layoutUpdate.addWidget(self.pickNoteType, r.next(), 1)
        self.layoutUpdate.addWidget(self.pickFieldKanji, r.next(), 1)
        self.layoutUpdate.addWidget(self.pickFreqFilter, r.next(), 1)
        self.layoutUpdate.addWidget(self.pickNumQuestions, r.next(), 1)
        self.layoutUpdate.addWidget(self.pickNumExtra, r.next(), 1)
        self.layoutUpdate.addWidget(self.pickAllowAmbig, r.next(), 1)
        r.next()
        self.layoutUpdate.addWidget(self.foundFieldQuestion, r.next(), 1)
        self.layoutUpdate.addWidget(self.foundFieldAnswer, r.next(), 1)
        self.layoutUpdate.addWidget(self.foundFieldExtra, r.next(), 1)
        
        
        self.layoutScan = QGridLayout(self.tabScan)
        
        self.layoutScan.addWidget(QLabel(text="Note type"), 0, 0)
        self.layoutScan.addWidget(QLabel(text="Scan type"), 0, 1)
        self.layoutScan.addWidget(QLabel(text="Expression field"), 0, 2)
        self.layoutScan.addWidget(QLabel(text="Reading field"), 0, 3)
        
        numScans = self.conf["numScans"]
        self.pickScanNoteTypes = [ComboBoxKV() for i in range(numScans)]
        self.pickScanTypes = [ComboBoxKV() for i in range(numScans)]
        self.pickScanExpressions = [ComboBoxKV() for i in range(numScans)]
        self.pickScanReadings = [ComboBoxKV() for i in range(numScans)]
        self.pickScanColumns = [
            self.pickScanNoteTypes,
            self.pickScanTypes,
            self.pickScanExpressions,
            self.pickScanReadings]
        for row in range(numScans):
            for col in range(4):
                self.layoutScan.addWidget(self.pickScanColumns[col][row], row + 1, col)
        
        
        buttons = QDialogButtonBox()
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.addButton(QDialogButtonBox.Save)
        buttons.addButton("Run", QDialogButtonBox.YesRole)
        self.conf["run"] = False
        def buttonClicked(button):
            role = buttons.buttonRole(button)
            if role == QDialogButtonBox.YesRole:
                self.checkAndRun()
            elif role == QDialogButtonBox.AcceptRole:
                self.accept()
            else:
                self.reject()
        buttons.clicked.connect(buttonClicked)
        self.layoutOuter.addWidget(buttons)
        
        
        noteTypeNames = self.mw.col.models.allNames()
        for box in self.pickScanNoteTypes:
            box.addItem("")
        for box in [self.pickNoteType] + self.pickScanNoteTypes:
            for noteTypeName in noteTypeNames:
                box.addItem(noteTypeName)
        
        for box in self.pickScanTypes:
            box.addItem("vocab")
            box.addItem("text")
        
        def pickNoteTypeChanged(text):
            self.conf["noteType"] = text
            self.refillFieldBox(self.pickFieldKanji, text)
            self.updateFieldsToUpdate(text)
        self.pickNoteType.setup(self.conf, "noteType", pickNoteTypeChanged)
        
        def pickFieldKanjiChanged(text):
            self.conf["fieldKanji"] = text
        self.pickFieldKanji.setup(self.conf, "fieldKanji", pickFieldKanjiChanged)
        
        def pickFreqFilterChanged(text):
            self.conf["freqFilter"] = text
        for item in self.conf["freqFilters"]:
            self.pickFreqFilter.addItem(item)
        self.pickFreqFilter.setup(self.conf, "freqFilter", pickFreqFilterChanged)
        
        def pickNumQuestionsChanged(value):
            self.conf["numQuestions"] = value
        self.pickNumQuestions.setValue(self.conf.get("numQuestions", 4))
        pickNumQuestionsChanged(self.pickNumQuestions.value())
        self.pickNumQuestions.valueChanged.connect(pickNumQuestionsChanged)
        
        def pickNumExtraChanged(value):
            self.conf["numExtra"] = value
        self.pickNumExtra.setValue(self.conf.get("numExtra", 4))
        pickNumExtraChanged(self.pickNumExtra.value())
        self.pickNumExtra.valueChanged.connect(pickNumExtraChanged)
        
        def pickAllowAmbigChanged(state):
            self.conf["allowAmbig"] = self.pickAllowAmbig.isChecked()
        self.pickAllowAmbig.setChecked(self.conf.get("allowAmbig", False))
        pickAllowAmbigChanged(None)
        self.pickAllowAmbig.stateChanged.connect(pickAllowAmbigChanged)
        
        scanConfs = self.conf.get("scan", [])
        scanConfs = scanConfs[:numScans]  #discard any scans we can't see
        self.conf["scan"] = scanConfs
        for row in range(numScans):
            if len(scanConfs) <= row:
                scanConfs.append({})
            
            def pickScanNoteTypeChanged(text, r=row):
                scanConfs[r]["noteType"] = text
                self.recalcScanFields(r)
            self.pickScanNoteTypes[row].setup(scanConfs[row], "noteType", pickScanNoteTypeChanged)
            
            def pickScanTypeChanged(text, r=row):
                scanConfs[r]["scanType"] = text
                self.recalcScanFields(r)
            self.pickScanTypes[row].setup(scanConfs[row], "scanType", pickScanTypeChanged)
            
            def pickScanExpressionChanged(text, r=row):
                scanConfs[r]["expression"] = text
            self.pickScanExpressions[row].setup(scanConfs[row], "expression", pickScanExpressionChanged)
            
            def pickScanReadingChanged(text, r=row):
                scanConfs[r]["reading"] = text
            self.pickScanReadings[row].setup(scanConfs[row], "reading", pickScanReadingChanged)
    

    def lookupFieldNames(self, noteTypeName):
        model = self.mw.col.models.byName(noteTypeName)
        if model is None:
            fieldNames = []  #happens if no model is selected
        else:
            fieldNames = [fld["name"] for fld in model["flds"]]
        return fieldNames

    def refillFieldBox(self, pickField, noteTypeName, optional=False):
        fieldNames = self.lookupFieldNames(noteTypeName)
        pickField.clear()
        if optional and fieldNames != []:
            pickField.addItem("")
        pickField.addItems(fieldNames)
    
    def recalcScanFields(self, row):
        noteTypeName = self.pickScanNoteTypes[row].currentText()
        self.refillFieldBox(self.pickScanExpressions[row], noteTypeName)
        self.pickScanReadings[row].clear()
        if self.pickScanTypes[row].currentText() == "vocab":
            self.refillFieldBox(self.pickScanReadings[row], noteTypeName, optional=True)

    def updateFieldsToUpdate(self, noteTypeName):
        fieldNames = self.lookupFieldNames(noteTypeName)
        def updateLine(widget, fieldName):
            if fieldName in fieldNames:
                text = "found"
            else:
                text = "not found"
            widget.setText(text)
        updateLine(self.foundFieldQuestion, self.conf["fieldVocabQuestion"])
        updateLine(self.foundFieldAnswer, self.conf["fieldVocabResponse"])
        updateLine(self.foundFieldExtra, self.conf["fieldVocabExtra"])
    
    def checkAndRun(self):
        confError = self.checkConfig(self.mw, self.conf)
        if confError:
            msgbox = QMessageBox(QMessageBox.Warning, "Error", confError, QMessageBox.Ok)
            msgbox.exec_()
        else:
            self.conf["run"] = True
            self.accept()

