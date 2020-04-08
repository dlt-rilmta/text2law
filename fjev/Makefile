
all: fjev

fjev:
	cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py
	for i in hu-* ; do echo "\n--- $$i" ; cat $$i | sed -f preproc_marks.sed | \
	python3 fjev_part.py | head -500 ; done > out ; vi out ; rm -f fjev_part.py
	diffvi out.r out

regi:
	mv out out.r

