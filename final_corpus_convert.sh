#!/bin/bash

IN=hu-corpus-marcell-20200128-after-iate-eurovoc
OUT=hu-corpus-marcell-20200128

# 'hu-' kell a fájlnév elejére (és 'out_' nem kell)
# IATE/EUROVOC '×'-ek ';'-vé alakítása
# NP és NE: '1-' => 'B-' valamint 'E-' => 'I-'

for i in `ls $IN`
#for i in `ls $IN | head -100`
do
  TARGET=`echo $i | sed "s/out_/hu-/"`
  cat $IN/$i \
  | sed "s/\([0-9]\)×/\1;/g" \
  | sed "s/	1-NP	/	B-NP	/g" \
  | sed "s/	1-ORG	/	B-ORG	/g" \
  | sed "s/	1-LOC	/	B-LOC	/g" \
  | sed "s/	1-PER	/	B-PER	/g" \
  | sed "s/	1-MISC	/	B-MISC	/g" \
  | sed "s/	E-NP	/	I-NP	/g" \
  | sed "s/	E-ORG	/	I-ORG	/g" \
  | sed "s/	E-LOC	/	I-LOC	/g" \
  | sed "s/	E-PER	/	I-PER	/g" \
  | sed "s/	E-MISC	/	I-MISC	/g" \
  > $OUT/$TARGET
done


