# -*- coding: utf-8 -*-
# Copyright (C) 2015,2017,2019  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

# KanjiVocab is an Anki addon which adds known vocab to a kanji deck.

from aqt import mw
from aqt.qt import QAction

try:
    from importlib import reload
except:
    pass #Python 2 has reload built-in

def updateKanjiVocab():
    from . import run
    reload(run)
    run.updateKanjiVocab()

action = QAction("KanjiVocab...", mw)
action.triggered.connect(updateKanjiVocab)
mw.form.menuTools.addAction(action)
