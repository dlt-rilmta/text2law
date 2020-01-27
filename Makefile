
FILE=taj_egk_2010_6_32010ii18eum.txt
FILE_CONLL:=$(shell echo $(FILE) | sed "s/\.txt/.conll/g")
FILE_CONLLUP:=$(shell echo $(FILE) | sed "s/\.txt/.conllup/g")

TEXT2LAW_OUTPUT=text2law_output
EMTSV_OUTPUT=emtsv_output
CONLL_OUTPUT=conll_output
METADATA_OUTPUT=metadata_output
FINAL_OUTPUT=final_output

# prep2dep kapcsán
TOKENIZED_OUTPUT=tokenized_output
PREP2DEP_OUTPUT=prep2dep_output

EMTSV_REST_URL=http://oliphant.nytud.hu:10001

EMTSV_MODULES=tok,morph,pos,conv-morph,dep,chunk,ner
EMTSV_MODULES_REST:=$(shell echo $(EMTSV_MODULES) | sed "s/,/\//g")

# -----

# külön lépés -- közlönyönként megy (és sok idő is)
0-text2law:
	python3 text2law.py kozlony_htmls/* -d $(TEXT2LAW_OUTPUT)

# -----

# az egyes dokumentumok elemzése
# x. prep2dep -> $(PREP2DEP_OUTPUT)/out_$(FILE)
# ha akarjuk: felvágdossa a hosszú mondatokat, kell neki előtte emtsv/tok
x-prep2dep:
	@echo "$(FILE) -- prep2dep"
	python3 prep2dep.py $(TOKENIZED_OUTPUT)/out_$(FILE) -d $(PREP2DEP_OUTPUT)

# 1. emtsv -> $(EMTSV_OUTPUT)/out_$(FILE)
1-emtsv:
	@echo "$(FILE) -- emtsv analysis"
	python3 txt_to_emtsv.py $(TEXT2LAW_OUTPUT)/$(FILE) -d $(EMTSV_OUTPUT)
# XXX tok,morph,pos,conv-morph,dep,chunk,ner hardcoded :)

# alternatív megoldások erre a lépésre -- 1 db inputfájl esetére
1-emtsv-docker-rest:
	mkdir -p $(EMTSV_OUTPUT)
	curl -s -F "file=@$(TEXT2LAW_OUTPUT)/$(FILE)" $(EMTSV_REST_URL)/$(EMTSV_MODULES_REST) > $(EMTSV_OUTPUT)/out_$(FILE)

1-emtsv-docker-cli:
	mkdir -p $(EMTSV_OUTPUT)
	cat $(TEXT2LAW_OUTPUT)/$(FILE) | docker run --rm -i mtaril/emtsv $(EMTSV_MODULES) > $(EMTSV_OUTPUT)/out_$(FILE)

# 2. konverzió conll formátumra -> $(CONLL_OUTPUT)/out_$(FILE)
2-conll:
	@echo "$(FILE) -- convert to conll"
	python3 convert2conll.py $(EMTSV_OUTPUT)/out_$(FILE) -d $(CONLL_OUTPUT)

# 3. metaadatok hozzáadása -> $(METADATA_OUTPUT)/$(FILE:s/.txt/.conll/)
3-metadata:
	@echo "$(FILE) -- add metadata"
	python3 add_metadata.py $(CONLL_OUTPUT)/out_$(FILE_CONLL) -d $(METADATA_OUTPUT)

# 4. iate_eurovoc.sh: IATE/EUROVOC id-k hozzáadása a metaadatolt fájlokhoz
# itt nem kell a '-d' :)
4-iate-eurovoc:
	@echo "$(FILE) -- add IATE/EUROVOC"
	sh iate_eurovoc.sh $(METADATA_OUTPUT)/$(FILE_CONLLUP) $(FINAL_OUTPUT)

# -----

# XXX így lehet használni:
# $ for i in text2law_output/* ; do f=$(basename $i) ; echo ; echo "--- $f" ; time make 1-emtsv FILE=$f ; time make 2-conll FILE=$f ; time make 3-metadata FILE=$f ; time make 4-iate-eurovoc FILE=$f ; done

# -----

#### # -1a, download_mk.py: letölti a legújabb közlönyöket
#### # -1b, pdf2text.py: a letöltési mappát végigjárja,
#### #      nevet az a közlönyöknek és html formátumra alakítja őket.
####
#### # 0, text2law.py = html -> törvények
#### # a html formátumban lévő közlönyökből kinyeri az egyes jogi szövegeket
#### # és elmenti őket txt formátumban
#### # - html-ek innen: [./kozlony_htmls]
#### # - output fájlok neve: típus_közlönyszám_törvénynév.txt
#### #   XXX 0-val / _-val kezdődik egy dokumentumnév -> potenciálisan hibás kimenet!
#### # $ python3 text2law.py <input útvonala> [-d <output mappa>]
#### # $ python3 text2law.py kozlony_htmls/*.html [-d text2law_output]
#### #
#### # ? hogyhogy a langdetect csomag nem volt fent? -- feltettem sudo pip-pel :)
#### python3 text2law.py kozlony_htmls/* -d text2law_output
#### # XXX gondoltam, hogy ezt lefuttatom egyben, de ez is minimum 1-2 óra,
#### #     úgyhogy gondoltam, inkább átmásolom -- de Dávidnál nem találtam...
#### #
#### # XXX -> végül lefuttattam a 2015-2019-es dolgokra... MOST EZ VAN!
#### # $ python3 text2law.py kozlony_htmls/*201[56789]*html -d text2law_output
#### #   ez 119 fájl -- a 4312-ből
#### # => eredmény
#### #   881 dokumentum -- a remélt 24000-ből
#### 
#### # 1, txt_to_emtsv.py = emtsv elemzés -- ezt nem használom, helyette make..
#### # futtatja az emtsv-t (tok..ner) megadott szövegeken
#### # $ python3 txt_to_emtsv.py <input útvonala> [-d <output mappa>]
#### # $ python3 txt_to_emtsv.py text2law_output/*.txt [-d emtsv_outp]
#### # XXX az elemzett fájlokat áthelyezi az analyzed_w_emtsv mappába
#### #     -- ez miért jó? ki is szedtem belőle... :)    
#### python3 txt_to_emtsv.py all_mk10138_52010viii31ovb.txt -d .
#### time python3 txt_to_emtsv.py trv_mk06130_2006lxxxi.txt -d .
####  XXX XXX XXX ez mennyi idő? (?) XXX :)
####  XXX XXX XXX miért ilyen bazi lassú? -- biztos a túl hosszú mondatok miatt...
#### # XXX a fenti kiváltható ezzel:
#### $ time curl -F "file=@all_mk10138_52010viii31ovb.txt" http://oliphant.nytud.hu:10001/tok/morph/pos/conv-morph/dep/chunk/ner > x
#### 
#### # megcsináltam for ciklussal, és tesztelem, hogy hogy megy :)
#### # XXX XXX XXX most ez fut:  _ITT_T
#### $ ./investigate.sh
#### $ watch 'tail -20 out ; echo ; echo ; ls -lt analyzed_w_emtsv | head'
#### # XXX XXX XXX közben vhogy ellenőrizni, h teljes egészében lefutott-e a fájl!
#### 
#### # 2, külön lépés: (ner és np miatt) kézi conll-re alakítás
#### # $ python3 convert2conll.py <input útvonala> [-d <output mappa>] [-p<True / False>]
#### python3 convert2conll.py out_taj_egk_2010_6_32010ii18eum.txt -d .
#### # -p = vár-e dependencia-elemzést az inputban. Default: False = nem vár
#### 
#### # 3, add_metadata.py: metaadatok hozzáadása a kimenethez + conllup
#### # global.columns, newdoc id, date, title, type, entype,
#### # issuer, topic (ha van), newpar id (ha van), sent_id, text
#### # $ python3 add_metadata.py <input útvonala> [-d <output mappa>]
#### # $ python3 add_metadata.py emtsv_outp/*.txt [-d corpus]
#### python3 add_metadata.py out_all_mk10138_52010viii31ovb.txt -d .
####
#### # 4, iate_eurovoc.sh: IATE/EUROVOC id-k hozzáadása a metaadatolt fájlokhoz
#### # ezt a Noémi/Ági által készített iate_eurovoc modul csinálja
#### # 
#### # a modul itt: halda@oliphant.nytud.hu:/home/halda/marcell/iate_eurovoc/
#### # 12 oszlopos conllup fájlok -> hozzá IATE és EUROVOC 13. és 14. oszlopként
#### # a modul használata: cat <filename> | python3 main.py
#### # 
#### # Dávid a iate_eurovoc.sh -n keresztül hívja a modult
#### # $ sh iate_eurovoc.sh <input útvonala> <output mappa>

# -----

backup:
	tar -czvf marcell-scripts.tar.gz out.investigate* *.sh Makefile *.py marcell_kodok_hasznalata*
	scpc marcell-scripts.tar.gz
	rm -f marcell-scripts.tar.gz

