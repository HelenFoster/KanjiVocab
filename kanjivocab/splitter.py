# -*- coding: utf-8 -*-
# New code copyright (C) 2017  Helen Foster
#
# Based on japanese/reading.py
# Copyright: Damien Elmes <anki@ichi2.net>
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
            raise Exception('Failed to import "japanese"')
        
        base = "../../addons/japanese/support/"
        mecabCmd = japanese.reading.mungeForPlatform(
            [base + "mecab"] + mecabArgs + [
                '-d', base, '-r', base + "mecabrc"])
        os.environ['DYLD_LIBRARY_PATH'] = base
        os.environ['LD_LIBRARY_PATH'] = base
        
        try:
            if not isWin:
                os.chmod(mecabCmd[0], 0755)
            self.mecab = subprocess.Popen(
                mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                startupinfo=japanese.reading.si)
        except OSError:
            raise Exception("Failed to run MeCab")

    def analyze(self, expr):
        import japanese
        expr = japanese.reading.escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore")+'\n')
        self.mecab.stdin.flush()
        expr = unicode(self.mecab.stdout.readline().rstrip('\r\n'), "euc-jp")
        return expr.split("@")

