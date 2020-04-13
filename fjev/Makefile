
FILES=hu-*
OUT=out

HEAD=
#HEAD=| head -500

SHELL := /bin/bash

all: fjev

# basic usage with investigating output
# hack: handling 'exit( 0 )' (for development)
fjev:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo -e "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > $(OUT) ; sleep 1 ; \
vi $(OUT) ; rm -f fjev_part.py ; echo ; \
git diff --word-diff $(OUT) ; \
echo

# the same but for measuring running time
# use: 'time make fjev-plain'
fjev-plain:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo -e "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > $(OUT) ; \
echo

# the same but comparing to 'out.old' instead of committed version of 'out'
fjev-old:
	echo ; \
cat fjev.py | sed '/exit( 0 )/q' | sed '/exit( 0 )/d' > fjev_part.py ; \
for i in $(FILES) ; do echo -e "\n--- $$i" ; \
cat $$i | sed -f preproc_marks.sed | python3 fjev_part.py $(HEAD) ; \
done > $(OUT) ; sleep 1 ; \
vi $(OUT) ; rm -f fjev_part.py ; echo ; \
./diffvi.sh $(OUT).old $(OUT) ; \
echo

# save a version of 'out' for use with 'make fjev-old'
old:
	cp -p $(OUT) $(OUT).old

# create frequency list of marktypes
# prerequisite: make fjev
freq:
	cat $(OUT) | tr ' ' '\n' | grep "\[\[T:" | ./sstats.sh > $(OUT).types.freq

freq-nosort:
	cat $(OUT) | tr ' ' '\n' | grep "\[\[T:" | ./sstat.sh > $(OUT).types.freq

