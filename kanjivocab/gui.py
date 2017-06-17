# -*- coding: utf-8 -*-
# Copyright (C) 2017  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from copy import deepcopy


class ComboBoxKV(QComboBox):
    def setCurrentByText(self, text, defaultIndex=0):
        index = self.findText(text)
        if index == -1:
            index = defaultIndex
        self.setCurrentIndex(index)


class Settings(QDialog):

    def __init__(self, mw, conf):

        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.conf = deepcopy(conf)
        self.foundFieldToUpdate = False

        self.resize(600, 400)
        self.setWindowTitle("Useless dialog")
        
        self.layoutOuter = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        self.layoutOuter.addWidget(self.tabs)
        self.tabUpdate = QWidget()
        self.tabScan = QWidget()
        self.tabs.addTab(self.tabUpdate, "Cards to update")
        self.tabs.addTab(self.tabScan, "Cards to scan")
        
        
        self.layoutUpdate = QGridLayout(self.tabUpdate)
        
        self.layoutUpdate.addWidget(
            QLabel(text="Note type"), 0, 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Kanji field (the kanji character by itself)"), 1, 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Questions"), 2, 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Extra answers"), 3, 0)
        self.layoutUpdate.addWidget(
            QLabel(text="Avoid ambiguous questions"), 4, 0)
        self.layoutUpdate.addWidget(
            QLabel(text="<b>Fields to update (the existing contents will be lost!)</b>"), 
            5, 0, 1, 2)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabQuestion"]), 6, 0)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabResponse"]), 7, 0)
        self.layoutUpdate.addWidget(
            QLabel(text=conf["fieldVocabExtra"]), 8, 0)
        
        self.pickNoteType = ComboBoxKV()
        self.pickFieldKanji = ComboBoxKV()
        self.pickNumQuestions = QSpinBox()
        self.pickNumExtra = QSpinBox()
        self.pickAvoidAmbig = QCheckBox()
        self.foundFieldQuestion = QLabel()
        self.foundFieldAnswer = QLabel()
        self.foundFieldExtra = QLabel()
        
        self.layoutUpdate.addWidget(self.pickNoteType, 0, 1)
        self.layoutUpdate.addWidget(self.pickFieldKanji, 1, 1)
        self.layoutUpdate.addWidget(self.pickNumQuestions, 2, 1)
        self.layoutUpdate.addWidget(self.pickNumExtra, 3, 1)
        self.layoutUpdate.addWidget(self.pickAvoidAmbig, 4, 1)
        self.layoutUpdate.addWidget(self.foundFieldQuestion, 6, 1)
        self.layoutUpdate.addWidget(self.foundFieldAnswer, 7, 1)
        self.layoutUpdate.addWidget(self.foundFieldExtra, 8, 1)
        
        
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
        
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layoutOuter.addWidget(buttons)
        
        
        noteTypeNames = self.mw.col.models.allNames()
        for box in [self.pickNoteType] + self.pickScanNoteTypes:
            box.addItem("")
            for noteTypeName in noteTypeNames:
                box.addItem(noteTypeName)
        
        for box in self.pickScanTypes:
            box.addItem("vocab")
            box.addItem("text")
        
        def pickNoteTypeChanged(index):
            text = self.pickNoteType.currentText()
            self.conf["noteType"] = text
            self.refillFieldBox(self.pickFieldKanji, text)
            self.updateFieldsToUpdate(text)
        self.pickNoteType.currentIndexChanged.connect(pickNoteTypeChanged)
        self.pickNoteType.setCurrentByText(self.conf.get("noteType", ""))
        
        def pickFieldKanjiChanged(index):
            text = self.pickFieldKanji.currentText()
            self.conf["fieldKanji"] = text
        self.pickFieldKanji.currentIndexChanged.connect(pickFieldKanjiChanged)
        self.pickFieldKanji.setCurrentByText(self.conf.get("fieldKanji", ""))
        
        def pickNumQuestionsChanged(value):
            self.conf["numQuestions"] = value
        self.pickNumQuestions.valueChanged.connect(pickNumQuestionsChanged)
        self.pickNumQuestions.setValue(self.conf.get("numQuestions", 4))
        
        def pickNumExtraChanged(value):
            self.conf["numQuestionsExtra"] = value
        self.pickNumExtra.valueChanged.connect(pickNumExtraChanged)
        self.pickNumExtra.setValue(self.conf.get("numQuestionsExtra", 4))
        
        def pickAvoidAmbigChanged(state):
            self.conf["avoidAmbig"] = self.pickAvoidAmbig.isChecked()
        self.pickAvoidAmbig.stateChanged.connect(pickAvoidAmbigChanged)
        self.pickAvoidAmbig.setChecked(self.conf.get("avoidAmbig", True))

    def lookupFieldNames(self, noteTypeName):
        model = self.mw.col.models.byName(noteTypeName)
        if model is None:
            fieldNames = []  #happens if no model is selected
        else:
            fieldNames = [fld["name"] for fld in model["flds"]]
        return fieldNames

    def refillFieldBox(self, pickField, noteTypeName):
        fieldNames = self.lookupFieldNames(noteTypeName)
        pickField.clear()
        pickField.addItem("")
        pickField.addItems(fieldNames)

    def updateFieldsToUpdate(self, noteTypeName):
        fieldNames = self.lookupFieldNames(noteTypeName)
        self.foundFieldToUpdate = False
        def updateLine(widget, fieldName):
            if fieldName in fieldNames:
                text = "found"
                self.foundFieldToUpdate = True
            else:
                text = "not found"
            widget.setText(text)
        updateLine(self.foundFieldQuestion, self.conf["fieldVocabQuestion"])
        updateLine(self.foundFieldAnswer, self.conf["fieldVocabResponse"])
        updateLine(self.foundFieldExtra, self.conf["fieldVocabExtra"])

