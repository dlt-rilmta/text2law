
FILES=hu-*

HEAD=
#HEAD=| head -500

TF := $(shell mktemp --suffix .gitdiff)

all: fjev

fjev:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > out ; sleep 1 ; \
vi out ; rm -f fjev_part.py ; echo ; \
gitd out ; \
echo

# prerequisite: make fjev
freq:
	cat out | tr ' ' '\n' | grep "\[\[T:" | sstats > out.types.freq


