#!/usr/bin/sh

# Run this file from the directory it's in.
# Creates kanjivocab.zip

if [ -e "kanjivocab.zip" ]
then
  echo "Please rename or delete kanjivocab.zip"
  exit
fi

zip -r kanjivocab.zip KanjiVocab.py kanjivocab --exclude \*.pyc
