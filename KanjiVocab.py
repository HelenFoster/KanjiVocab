# -*- coding: utf-8 -*-
# Copyright (C) 2015  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


# KanjiVocab is an Anki addon which adds known vocab to a kanji deck.
# This file belongs with the "kanjivocab" folder.
# The README might be inside depending on how you received this!


from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

def updateKanjiVocab():
    import kanjivocab.run
    reload(kanjivocab.run)
    kanjivocab.run.updateKanjiVocab()
    
action = QAction("Kanji Vocab Recalc", mw)
#action.setShortcut(_("Ctrl+K")) #this isn't good; pick a different one or leave it out
mw.connect(action, SIGNAL("triggered()"), updateKanjiVocab)
mw.form.menuTools.addAction(action)
