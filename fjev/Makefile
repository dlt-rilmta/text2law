
FILES=hu-*

HEAD=
#HEAD=| head -500

TF := $(shell mktemp --suffix .gitdiff)

all: fjev

# basic usage with investigating output
fjev:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > out ; sleep 1 ; \
vi out ; rm -f fjev_part.py ; echo ; \
gitd out ; \
echo

# for measuring running time with 'time make fjev-plain'
fjev-plain:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > out ; \
echo

fjev-old:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > out ; sleep 1 ; \
vi out ; rm -f fjev_part.py ; echo ; \
diffvi out.old out ; \
echo

old:
	cp -p out out.old

# prerequisite: make fjev
freq:
	cat out | tr ' ' '\n' | grep "\[\[T:" | sstats > out.types.freq

