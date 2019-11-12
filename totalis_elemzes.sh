#!/bin/bash

# x oli:10001 / 1 -- fut a régi, ezt nem használhatom...

# - oli:10001 / 2 -- 00001
./investigate.sh official_text2law_output K00001 http://oliphant.nytud.hu:10001 "tok,morph,pos,conv-morph,chunk,ner" 1 &

# - oli:10002 / 1 -- 14001
./investigate.sh official_text2law_output K14001 http://oliphant.nytud.hu:10002 "tok,morph,pos,conv-morph,chunk,ner" 14001 &

# - oli:10002 / 2 -- 21001
./investigate.sh official_text2law_output K21001 http://oliphant.nytud.hu:10002 "tok,morph,pos,conv-morph,chunk,ner" 21001 &

# - ELTE:5000 / 1 -- 24001
./investigate.sh official_text2law_output K24001 http://emtsv.duckdns.org:5000 "tok,morph,pos,conv-morph,chunk,ner" 24001 &

# - ELTE:5000 / 2 -- 25501
./investigate.sh official_text2law_output K25501 http://emtsv.duckdns.org:5000 "tok,morph,pos,conv-morph,chunk,ner" 25501 &

# - ELTE:5001 / 1 -- 26251
./investigate.sh official_text2law_output K26251 http://emtsv.duckdns.org:5001 "tok,morph,pos,conv-morph,chunk,ner" 26251 &

# - ELTE:5001 / 2 -- 26551
./investigate.sh official_text2law_output K26551 http://emtsv.duckdns.org:5001 "tok,morph,pos,conv-morph,chunk,ner" 26551 &

# x ELTE:5002 / 1 -- fut a régi, ezt nem használhatom...

# - ELTE:5002 / 2 -- 26701
./investigate.sh official_text2law_output K26701 http://emtsv.duckdns.org:5002 "tok,morph,pos,conv-morph,chunk,ner" 26701 &

# - ELTE:5003 / 1 -- 26776
./investigate.sh official_text2law_output K26776 http://emtsv.duckdns.org:5003 "tok,morph,pos,conv-morph,chunk,ner" 26776 &

# - ELTE:5003 / 2 -- 26806
./investigate.sh official_text2law_output K26806 http://emtsv.duckdns.org:5003 "tok,morph,pos,conv-morph,chunk,ner" 26806 &

