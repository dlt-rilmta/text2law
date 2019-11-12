# MARCELL projekt feldolgozólánc

Így:
```bash
./investigate.sh samples SAMPLES <emtsv_REST_server_URL> tok,morph,pos,conv-morph,chunk,ner 1
```      

... és akkor (kb. 5 perc múlva) megkapjuk
a `samples` könyvtárban lévő mintafájlok elemzését
a `SAMPLES_rst_final` könyvtárban,
aminek teljesen azonosnak kell lennie az `analyzed_samples`
könyvtárban található fájlokkal.

(Dependenciaelemzés most nincs benne.)

--

Marcell projekthez: Magyar Közlöny pdf fájljaiból generált txt/html fájlok (l.
[pdf2text-demo](https://github.com/dlt-rilmta/pdf2text-demo)) parszolása
tartalomjegyzék szerint, törvények kiírása fájlba.

