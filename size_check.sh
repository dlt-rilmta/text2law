#!/bin/bash

if [ $# -ne 1 ]
then
  echo "1 paraméter kötelező:"
  echo "  * futtatás azonosítója"
  exit 1;
fi

RUN_ID=$1

cat out.investigate.$RUN_ID | grep wc | paste -d ' ' - - | cat -n | \
  sed "s/........ wc://g" | \
  awk '{ if ( $2 < $3 ) { print $1, $2, $3, "ok" } else { print $1, $2, $3, "ERROR" } }'

