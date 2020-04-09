
HEAD=500

all: fjev

fjev:
	echo ; cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py
	for i in hu-* ; do echo "\n--- $$i" ; \
  cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py | head -$(HEAD) ; \
  done > out ; sleep 1
	vi out ; rm -f fjev_part.py ; echo ; diffvi out.r out ; echo

regi:
	mv out out.r

