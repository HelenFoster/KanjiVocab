# -*- coding: utf-8 -*-
# Copyright (C) 2017  Helen Foster
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


from PyQt4.QtCore import Qt
from PyQt4.QtGui import *


class Settings(QDialog):

    def __init__(self, mw):

        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw

        self.resize(600, 400)
        self.setWindowTitle("Useless dialog")
        
        layout = QVBoxLayout(self)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

