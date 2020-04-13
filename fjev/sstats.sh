#!/bin/bash
# 1. create frequency list
# 2. sort output according to item
# method: change separator space to tab

sort | uniq -c | sort -nr | \
sed "s/^\( *[0-9][0-9]*\) \(.*\)/\1	\2/g" | sort -t '	' -k2,2

