#!/bin/bash

# azt mutatja, hogy az egeys elemzésekben hány fájl van készen

# ennyi másodpercenként frissít
INTERVAL=10

# dict: RUN_ID -> ennyi fájlt kell lefuttatnia
declare -A runs=(
  ["K00001"]=9000
  ["K09001"]=6000
  ["K15001"]=4000
  ["K19001"]=2700
  ["K21701"]=1800
  ["K23501"]=1200
  ["K24701"]=800
  ["K25501"]=500
  ["K26001"]=350
  ["K26351"]=200
  ["K26551"]=120
  ["K26671"]=70
  ["K26741"]=40
  ["K26781"]=23
  ["K26804"]=12
  ["K26816"]=6
)
ORDER="K00001 K09001 K15001 K19001 K21701 K23501 K24701 K25501 K26001 K26351 K26551 K26671 K26741 K26781 K26804 K26816"

while true
do
  (
    echo "<html><head><meta http-equiv='refresh' content='$INTERVAL'></head><body>"
    echo "start:"
    echo "Mon Jan 27 16:30:00 CET 2020"
    echo "<br/>"
    echo ".now:"
    date
    echo '<br/><br/><table>'
    for i in $ORDER
    do

      n=`cat out.investigate.$i | grep "sh iate_eurovoc.sh" | wc -l` 
      s=${runs[$i]}
      p=`expr $n \* 10000 / $s | sed "s/\(.*\)\(..\)/\1,\2/"`

      echo '<tr>'
      echo "<td>$i</td>"
      echo "<td align='right'>$n /</td>"
      echo "<td align='right'>$s =</td>"
      echo "<td align='right'>$p%</td>"
      echo '<tr/>'
    done
    echo "</table></body></html>"
  ) > K.html

  scpc K.html

  sleep $INTERVAL

done

