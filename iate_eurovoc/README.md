# Noémi

## termek kinyerése az xml-ekből

- kinyertem a descriptorokat és a iate számokat az xml-ekből
    a fontos számok és a termek tokenizálatlanul, tsv-ben is megvannak itt:
    extract_terms/terms/tsv/...
    a iate túl nagy volt, ezért darabokban dolgoztam fel (xaa-xae)

- tsv-be rendeztem az alábbiak alapján:
    descriptorok: extract_terms/tokterms/eurovoc.tsv
        forrása: extract_terms/terms/desc_hu.xml
        1. oszlop: descriptor szám (xml-ben: DESCRIPTEUR_ID tag textje)
        2. oszlop: term tokenizálva (tokenek között: @)

    iate-számok: extract_terms/tokterms/iate.tsv
    forrása: extract_terms/terms/diate.tbx
        1. oszlop: iate-szám (xml-ben: termEntry id attribútum értéke), kötőjel, másik szám (xml-ben: descrip type="subjectField" tag textje)
            a másik szám lehet több szám is, ekkor vessző és space van közöttük, ezért a splittelésnél mindenképp tabra splittelj majd, ha feldolgozod
        2. oszlop: term tokenizálva (tokenek között: @)
        a több iate fájlt egyberaktam, de a külön fájlok is megvannak, ha úgy kényelmesebb

## modul előkészítése

- a module mappába előkészítettem egy kicsike conll fájlt
- a main.py-be bekészítettem egy egyszerű tsv-olvasót a conll feldolgozásához
    - használata:  cat examp.conll | python3 main.py
- gondolkoztam, hogy minek kell megvalósulnia:
    - a mintaillesztésnek csak mondatokon belül van értelme, tehát érdemes mondatonként haladni
    - ami a conllben új sor, az a termeknél @ (ha más formátumra van szükséged a termeknél, szólj!)
    - a conll fix tíz oszlopos, de ezt a két oszlopot illesszük be 11-12. oszlopnak szerintem, aztán ha így nem jó, akkor módosítjuk

# Ági
pattern matching-es kódot (module/main.py). A részletek a kódon belül olvashatók.

Ellenőrzés:
- az 'etnikai' lemmára keresve látható olyan eset, amikor többszavas találat, és azon belül egyszavas találat is van
- a 'módosítás' lemmára keresve látható, hogy a 11. és 12. oszlop teljesen függetlenek egymástól

Ami még változtatásra szorul(hat):
1. A találatok számozása. Most a 11. és 12. oszlop teljesen függetlenek egymástól, sőt mondatonként újrakezdődik a számozás, mert Bálint pszeudokódjában így szerepelt a 'cnt'.
1. A tsv segédfájlok beolvasása. Egyelőre bele van égetve a kódba, de majd átalakítom aszerint, hogy mi a legjobb a modullá váláshoz.
1. Bizonyos esetekben ugyanahhoz a IATE term-höz több ID is tartozik. Ez szerintem nem külön találat, de nem is ,-vel elválasztós dolog, mert az a későbbi feldolgozást zavarná, egyelőre × jelet raktam az ilyen ID-k közé.
1. Különféle idézőjel-típusok egységesítésére lehet még szükség.

Ami komolyabb probléma lehet:
Bizonyos term-ök többes számúak vagy valaminek a birtokai (pl. 'elvek', 'jegyzéke'). Ha a szövegben ezek nem alanyesetben fordulnak elő, akkor nem tudom megtalálni őket, mivel se a form (pl. elveket), se a lemma (pl. elv) oszlop tartalma nem felel meg pontosan a term-nek. Ezt nem ellenőriztem, de szinte biztos, hogy vesztünk így találatokat.


# Bálint pszeudokódja

```
dict = term / descriptor connected by '_' -> identifier

cnt = 1 # menjen mondatonként

for i in tokens of sent:
  # egyszavas
  if canonical( i ) in dict:
    add_annot( cnt, i )
    ++cnt
  # kétszavas
  if canonical( i, i+1 ) in dict:
    add_annot( cnt, i..i+1 )
    ++cnt
  # így tovább többszavasokra, ameddig kell...

add_annot( cnt, seq ):
  seq[0].colIATE += "cnt:dict[canonical(seq)]" # pontosvesszővel
  seq[1].colIATE += "cnt"                      # pontosvesszővel
  ...

canonical( seq ):
  return "form_.._form_lemma"
```
