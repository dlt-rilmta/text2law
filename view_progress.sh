#!/bin/bash

ls -ltgo | tail -n +2 | cut -b13- | grep -v out_ > /tmp/a

cat /tmp/a | wc -l

cat /tmp/a | head -1

for i in 1200 800 400
do
  echo -n "$i. "
  cat /tmp/a | tail -$i | head -1
done

echo -n "--1. "
cat /tmp/a | tail -1

