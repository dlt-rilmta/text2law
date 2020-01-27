#!/bin/bash
# investigate2.sh "általános" továbbfejlesztése

if [ $# -ne 5 ]
then
  echo "5 paraméter kötelező:"
  echo "  * 1. input könyvtár"
  echo "  * 2. futtatás azonosítója"
  echo "  * 3. emtsv REST URL"
  echo "  * 4. emtsv modulok így: \"m1,m2 m3\""
  echo "  * 5. hányadik fájltól (kicsiktől nagyok felé)"
  exit 1;
fi

# ORIGDIR=official_text2law_output
ORIGDIR=$1

# RUN_ID=i
RUN_ID=$2

# EMTSV_REST_URL=http://oliphant.nytud.hu:10001
EMTSV_REST_URL=$3

# EMTSV_MODULES="tok morph pos conv-morph dep chunk ner" = minden külön-külön
EMTSV_MODULES=$4

# FROM=1
FROM=$5

# ./investigate.sh official_text2law_output ELTE http://emtsv.duckdns.org:5000 16000

(
  for F in `ls -Sr $ORIGDIR/* | tail -n +$FROM`
  do

F=$(basename $F)
F_CONLL=`echo $F | sed "s/\.txt/.conll/"`
F_FINAL=`echo $F | sed "s/\.txt/.conllup/"`

# infó a fájlról
echo "--- file: $F"
echo -n "text2law wc: "
cat $ORIGDIR/$F | tr ' ' '\n' | wc -l

# -----

PREVDIR=$ORIGDIR

# 0a emtsv / tok előre
DIR=${RUN_ID}_rst_tok
echo
date
time make 1-emtsv-docker-rest FILE=$F \
  EMTSV_REST_URL=$EMTSV_REST_URL EMTSV_MODULES=tok \
  TEXT2LAW_OUTPUT=$PREVDIR EMTSV_OUTPUT=$DIR
# emtsv: IN = .txt -> OUT = out_...txt
# itt nem kell ln, mert emtsv/OUT = prep2dep/IN = out_...txt
PREVDIR=$DIR

# 0b prep2dep
DIR=${RUN_ID}_rst_prep2dep
echo
date
time make x-prep2dep FILE=$F \
  TOKENIZED_OUTPUT=$PREVDIR PREP2DEP_OUTPUT=$DIR
# prep2dep: IN = out_...txt -> OUT = out_...txt
# mivel emtsv futtatás következik: vissza kell nevezni '.txt'-re
ln $DIR/out_$F $DIR/$F
PREVDIR=$DIR

# 1. emtsv elemzés -- tok utáni rész
for STEP in $EMTSV_MODULES
do
  # feltesszük, hogy nincs '_' az emtsv modulnevekben... bár ha van, se nagy baj
  DIR=`echo $STEP | sed "s/,/_/g" | sed "s/^/${RUN_ID}_rst_/"`
  echo
  date
  time make 1-emtsv-docker-rest FILE=$F \
    EMTSV_REST_URL=$EMTSV_REST_URL EMTSV_MODULES=$STEP \
    TEXT2LAW_OUTPUT=$PREVDIR EMTSV_OUTPUT=$DIR
  # emtsv: IN = .txt -> OUT = out_...txt
  # de mivel több emtsv hívás lehet, vissza kell nevezni!
  ln $DIR/out_$F $DIR/$F
  PREVDIR=$DIR
done

# 2. konverzió conll formátumra
DIR=${RUN_ID}_rst_conll
echo
date
time make 2-conll FILE=$F \
  EMTSV_OUTPUT=$PREVDIR CONLL_OUTPUT=$DIR
# itt nem kell ln, mert conll/OUT = metadata/IN = out_...conll
PREVDIR=$DIR

# 3. metaadatok hozzáadása
DIR=${RUN_ID}_rst_metadata
echo
date
time make 3-metadata FILE=$F \
  CONLL_OUTPUT=$PREVDIR METADATA_OUTPUT=$DIR
# itt nem kell ln, mert metadata/OUT = iate/IN = .conllup
PREVDIR=$DIR

# 4. IATE/EUROVOC hozzáadása
DIR=${RUN_ID}_rst_final
echo
date
time make 4-iate-eurovoc FILE=$F \
  METADATA_OUTPUT=$PREVDIR FINAL_OUTPUT=$DIR
ln $DIR/out_$F_FINAL $DIR/$F_FINAL

echo -n "dockrest wc: "
cat $DIR/$F_FINAL | wc -l

echo
echo "====="
echo

  done
) > out.investigate.$RUN_ID 2>&1

# fájlnevek -- 2020.01.20.
#
#           IN                OUT             átmenet (OUT =? köv IN)
# emtsv/tok      .txt      -> out_...txt       ok
# prep2dep  out_...txt     -> out_...txt       ln!
# emtsv          .txt      -> out_...txt       ok (ezen belül kell)
# conll     out_...txt     -> out_...conll     ok
# metadata  out_...conll   ->      .conllup    ok
# iate           .conllup  -> out_...conllup   ln!
#
# fájlnevek -- 2019.11.11.
#
#           IN                OUT
# emtsv          .txt      -> out_...txt
# conll     out_...txt     -> out_...conll
# metadata  out_...conll   ->      .conllup
# iate           .conllup  -> out_...conllup 
#
# XXX ugye ehelyett lehetne végig 'out_' nélküli txt
#     -> ha ez lesz, akkor módosítandó a Makefile-ban és itt. :) XXX
