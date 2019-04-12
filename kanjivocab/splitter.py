# -*- coding: utf-8 -*-
# New code copyright (C) 2017,2019  Helen Foster
#
# Based on japanese/reading.py
# Copyright: Ankitects Pty Ltd and contributors
# https://ankiweb.net/shared/info/3918629684
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#

import os, subprocess
from anki.utils import isWin

class Splitter:
    def __init__(self, mecabArgs):
        try:
            import japanese
        except:
            try:
                japanese = __import__("3918629684")
            except:
                raise Exception('Failed to import Japanese Support module')
        self.jpr = japanese.reading
        try:
            supportDir = self.jpr.supportDir
        except:
            supportDir = "../../addons/japanese/support/"
        
        mecabCmd = self.jpr.mungeForPlatform(
            [os.path.join(supportDir, "mecab")] + mecabArgs + [
                '-d', supportDir, '-r', os.path.join(supportDir,"mecabrc")])
        os.environ['DYLD_LIBRARY_PATH'] = supportDir
        os.environ['LD_LIBRARY_PATH'] = supportDir
        
        try:
            if not isWin:
                os.chmod(mecabCmd[0], 0o755)
            self.mecab = subprocess.Popen(
                mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                startupinfo=self.jpr.si)
        except OSError:
            raise Exception("Failed to run MeCab at %s" % mecabCmd[0])

    def analyze(self, expr):
        expr = self.jpr.escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore") + b'\n')
        self.mecab.stdin.flush()
        expr = self.mecab.stdout.readline().rstrip(b'\r\n').decode('euc-jp')
        return expr.split("@")

