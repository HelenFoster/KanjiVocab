# -*- coding: utf-8 -*-
# Copyright (C) 2017  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from copy import deepcopy


class Settings(QDialog):

    def __init__(self, mw, conf):

        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.conf = deepcopy(conf)

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
        
        self.pickNoteType = QComboBox()
        self.pickFieldKanji = QComboBox()
        self.pickNumQuestions = QSpinBox()
        self.pickNumExtra = QSpinBox()
        self.pickAvoidAmbig = QCheckBox()
        self.foundFieldQuestion = QLabel(text="test1")
        self.foundFieldAnswer = QLabel(text="test2")
        self.foundFieldExtra = QLabel(text="test3")
        
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
        
        numScans = 6
        self.pickScanNoteTypes = [QComboBox() for i in range(numScans)]
        self.pickScanTypes = [QComboBox() for i in range(numScans)]
        self.pickScanExpressions = [QComboBox() for i in range(numScans)]
        self.pickScanReadings = [QComboBox() for i in range(numScans)]
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

