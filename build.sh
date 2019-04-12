#!/usr/bin/sh

# Run this file from the directory it's in.
# Creates kanjivocab20.zip (for Anki 2.0) and kanjivocab21.zip (for Anki 2.1)

if [ -e "kanjivocab20.zip" ]
then
  echo "Please rename or delete kanjivocab20.zip"
  exit
fi

if [ -e "kanjivocab21.zip" ]
then
  echo "Please rename or delete kanjivocab21.zip"
  exit
fi

zip -r kanjivocab20.zip KanjiVocab.py kanjivocab --exclude \*.pyc \*pycache\*

zip -rj kanjivocab21.zip kanjivocab --exclude \*.pyc \*pycache\*
