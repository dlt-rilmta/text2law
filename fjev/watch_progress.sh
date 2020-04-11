#!/bin/bash

# 2000 <=
GREP_PATTERN="^ *[0-9][0-9][0-9][0-9][0-9]\|^ *[2-9][0-9][0-9][0-9]"

watch "make freq ; ls -lt out ; \
echo -n $(cat out | grep '^---' | wc -l) ; echo \" / 26821\" ; \
cat out.types.freq | grep '$GREP_PATTERN'"
