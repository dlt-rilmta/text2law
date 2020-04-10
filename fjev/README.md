## fjev = "formális jogi egységekre vagdosás"

Használat: `make` hatására előál' az `out` fájlt
a könyvtárban található `hu-*` fájlokból.
Az `out`-ot lehet nézegetni.

Kétféle annotációt tartalmaz:
 * "type" = `[[T:...` (csak típusok)
 * "full" = `[[F:...` (teljes leírás)

Az annotációk sosem tartalmaz(hat)nak whitespace-t!

### "type" leírás

 * `[[T:t0+t1+t2]]`
azaz: `T:` mint "type" leírás,
és jelenleg egy olyan ponton vagyunk a dokumentumban, hogy
egy nullás típusú számozón (`t0`) belül
egy 1-es típusú számozó (`t1`), és azon belül 
egy 2-es típusú számozó (`t2`).

Lényeg:
_A `[[T:...` leírásokból készített gyaklista egész jól mutatja
 a dokumentum szerkezetét!_

Előállítása: `make freq` -> `out.types.freq`.


### "full" leírás

 * `[[F:"b)"=type2/next@2=t0/1+t1/0+t2/1]]`
azaz: `F:` mint "full" leírás,
a `b)` egy 2. típusú (`type2`) számozó,
egy "nem első" elem (`next`),
2-es szinten, mélységben van (`@2`),
és jelenleg itt vagyunk a dokumentumban:
0-s szinten egy nullás típusú számozó 1-es tagja (`t0/1`),
1-es szinten egy 1-es típusú számozó nullás tagja (`t1/0`), és 
2-es szinten pedig egy 2-es típusú számozó 1-es tagja (`t2/1`)
ez a bizonyos `b` az aktuális.
(Mindent 0-tól számozunk.)

 * `3._§ [[F:"3._§"=type0/next<-up2@0=t0/2]]`
Itt annyi van pluszban, hogy a dokumentumban található
ezt megelőző számozóhoz képest
2 szintet, mélységet (`<-up2`) kijjebb jöttünk.

