#!/bin/bash

inp=$1
basp=$2

if [ -z "$basp" ]; then
    basp=$(pwd)/iate_eurovoc_output;
fi

mkdir -p $basp

for file in $inp; do 
    echo $file; 
    cat $file | python3 iate_eurovoc/module/main.py > $basp/out_$(basename $file);
done

