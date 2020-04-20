#!/usr/bin/sh

# Run this file from the directory it's in.
# Creates kanjivocab.ankiaddon (preventing overwriting).

if [ -e "kanjivocab.ankiaddon" ]
then
  echo "Please rename or delete kanjivocab.ankiaddon"
  exit
fi

zip -rj kanjivocab.ankiaddon kanjivocab --exclude \*.pyc \*pycache\*
