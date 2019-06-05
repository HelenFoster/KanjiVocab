#!/usr/bin/sh

# Run this file from the directory it's in.
# Creates kanjivocab.zip (for Anki 2.0) and kanjivocab.ankiaddon (for Anki 2.1)

if [ -e "kanjivocab.zip" ]
then
  echo "Please rename or delete kanjivocab.zip"
  exit
fi

if [ -e "kanjivocab.ankiaddon" ]
then
  echo "Please rename or delete kanjivocab.ankiaddon"
  exit
fi

zip -r kanjivocab.zip KanjiVocab.py kanjivocab --exclude \*.pyc \*pycache\*

zip -rj kanjivocab.ankiaddon kanjivocab --exclude \*.pyc \*pycache\*
