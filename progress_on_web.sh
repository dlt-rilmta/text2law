#!/bin/bash

# azt mutatja, hogy az egeys elemzésekben hány fájl van készen

# ennyi másodpercenként frissít
INTERVAL=10

# dict: RUN_ID -> ennyi fájlt kell lefuttatnia
declare -A runs=(
  ["K00001"]=7999
  ["K08000"]=6001
  ["K14001"]=3500
  ["K17501"]=99
  ["K17600"]=401
  ["K18001"]=1000
  ["K19001"]=919
  ["K19920"]=81
  ["K20001"]=1000
  ["K21001"]=1299
  ["K22300"]=201
  ["K22501"]=500
  ["K23001"]=1000
  ["K24001"]=1299
  ["K25300"]=141
  ["K25441"]=60
  ["K25501"]=649
  ["K26150"]=71
  ["K26221"]=30
  ["K26251"]=300
  ["K26551"]=150
  ["K26701"]=75
  ["K26776"]=30
  ["K26806"]=16
)
ORDER="K00001 K08000 K14001 K17501 K17600 K18001 K19001 K19920 K20001 K21001 K22300 K22501 K23001 K24001 K25300 K25441 K25501 K26150 K26221 K26251 K26551 K26701 K26776 K26806"

while true
do
  (
    echo "<html><head><meta http-equiv='refresh' content='$INTERVAL'></head><body>"
    echo "start:"
    echo "Mon Nov 11 18:30:00 CET 2019"
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

