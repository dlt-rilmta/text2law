
import sys
import re

# mindent 0-tól számolunk!!! :)

# jogszabályok (hierarchikus dokumentumok) szerkezetének feltárása

NOLEVEL = -1
level = NOLEVEL                        # hányadik szinten vagyunk

strc = []                              # l-edik szinten milyen mark van

cursor = []                            # l-edik szinten lévő marktípus
                                       # hányadik eleménél tartunk

# számozók elemeinek lekérdezése/generálása
def get_D( n ): # 1 2 3 4 ...
  n += 1
  return str( n )

def get_L( n ): # a b c d ...
  n += 1
  if n <= 26:
    return chr( ord( 'a' ) + n - 1 )
  else:
    return "{{letter#{}}}".format( n ) # XXX jobban? '{{' => '{'

# XXX ennél azért lehetne jobban :) :)
def get_R( n ): # I II III IV ...
  n += 1
  if n ==  1: return 'I'
  if n ==  2: return 'II'
  if n ==  3: return 'III'
  if n ==  4: return 'IV'
  if n ==  5: return 'V'
  if n ==  6: return 'VI'
  if n ==  7: return 'VII'
  if n ==  8: return 'VIII'
  if n ==  9: return 'IX'
  if n == 10: return 'X'
  return "{{roman#{}}}".format( n ) # XXX jobban? '{{' => '{'

# számozók
ntools = {
  '{D}': get_D,
  '{L}': get_L,
  '{R}': get_R
}
# '{D}': '[0-9]{1,3}'    # arab szám
# '{L}': '[a-z]{1}'      # betű -- esetleg majd {1,2}
# '{R}': '[CDILMVX]{1,8} # római szám -- sok számjegy kellhet!
# XXX hm a regex-ek végül nem is kellenek -- hogyhogy? :)
# XXX gondolom, mert a get_mark() -kal a konkrét mark-okat hozom elő

# '[(]' -- így tudom escape-elni, mert a '\' vmiért megduplázódik XXX
marktypecodes = [
  '{D}._§',      # 0 '1._§'
  '({D})',       # 1 '(1)'  XXX hekk!
  '{L})',        # 2 'a)'   XXX hekk!
  '{R}.',        # 3 'I.'
  '{D}.',        # 4 '1.'
  '{D}._cikk',   # 5 '1._cikk'
  '{R}._FEJEZET' # 6 'I._FEJEZET'
  # ...
]
# XXX csak 1 token lehet => preproc_marks.sed alakítja ilyenre
# XXX egyéb mark-típusok jöhetnének...

# XXX re.compile() által esetleg vhogy gyorsítani...
def get_mark( m, n ):
  """
  visszaad egy konkrét 'mark'-ot: az 'm' indexű marktype 'n'-edik elemét
  """
  mark = marktypecodes[m]
  for ( code, func ) in ntools.items():
    mark = re.sub( code, func( n ), mark )
  return mark

# pl.: "(1)"
def search_pos( stuff, pos ):
  """
  'stuff'-ot keressük 'mark' (list of lists) allistáinak 'pos' pozíciójában
  return: az allista indexe (vagy None)
  """
  for ( m, c ) in enumerate( marktypecodes ): 
    mark = get_mark( m, pos )
    if mark == stuff:
      return m
  return None

MAXITEMS = 4

# pl.: "(1)"
def search_ser( stuff, index ): # XXX XXX XXX
  """
  'stuff'-ot keressük 'mark' (list of lists) 'index'-edik allistájában
  return: az elem indexe (vagy None)
  """
  # XXX totál nem ciklussal kéne, hanem:
  # XXX x = get_number_from( stuff )
  # XXX get_mark( index, x )
  # XXX sztem ez jelentősen gyorsítana!!!
  for j in range( MAXITEMS ):
    # XXX vhogy mindenképp le kell korlátozni asszem...
    # XXX kül végtelen ciklus lesz...
    # XXX -> kivéve, ha megcsinálom a ciklus nélküli verziót,
    # XXX    akkor nem kell korlát!!! :)
    mark = get_mark( index, j ) # XXX if not None...
    if mark == stuff:
      return j
  return None
       
def annotate( word, level, marktype, message ): # XXX lehet, hogy nem is kell a 'level' param
  """
  megjelöljük a szövegben a cuccot / vagy legalábbis kiírjuk :)
  """
  print( "[[\"{}\"=type{}{}@{}={}]]".format(
    word,
    marktype,
    message,
    level,
    '+'.join( "t{}/{}".format( t, i ) for (t, i) in list( zip( strc, cursor ) ) )
  ), end = ' ' )

for line in sys.stdin:

  for w in line.split():               # w = tokens sep by spaces

    print( w, end = ' ' )

    m = search_pos( w, 0 )             # => w-t keresem mark-ban a 0. helyeken
    if m is not None:                  # adott marktípus 0. azaz első eleme!
      if not strc or strc[-1] != m:    # és nem ua marktípus mint 1-gyel följebb,
                                       # azaz nem "a) pont a) pontja" eset
        level += 1
        strc.append( m )               # XXX tutira a 'level'-edik elem legyen!
        cursor.append( 0 )             # XXX tutira a 'level'-edik elem legyen!
        annotate( w, level, m, "/1st" )
      else:
        annotate( w, level, m, " [sima szó = 'a) a)' eset]" )
                                       # XXX kell: a rossz c) a) eset kezelése

    elif level > NOLEVEL:
      for n in range( 0, level+1 ):  # akt(n=0) v külsőbb szintű köv elemeket nézzük
                                     # jó a 'level+1' :)
                                     # kb. mert 2-es level == 3 db level 
        L = level - n;
        j = search_ser( w, strc[L] ) # => w-t keresem mark adott allistájában
        if j is not None:            # akt(n=0) v külsőbb szintű marktípus többedik eleme
          if j == cursor[L] + 1:     # és konkrétan a következő!
            level -= n               # átállunk a megf külsőbb szintre
            del strc[level+1:]       # belsőbb szinteket nullázzuk
            del cursor[level+1:]
            cursor[level] += 1       # továbblépünk 1-gyel (a külső szinten)
            msg = "/next" if n == 0 else "/next<-up" + str( n )
            annotate( w, level, strc[level], msg )
          else:
            annotate( w, level, strc[level], " [sima szó? kimaradás?]" ) # nem a következő
                                       # XXX kell: kimaradás kezelése
                                       # XXX kell: a rossz c) b) eset kezelése
          break

    else:                              # sima szó
      pass

  print()

# KÉSZ
# #1 verzió: a dok bármely részén bármilyen szerkezetet megengedünk :)
#
# unlimited 'mark': e) f) g) h) ... :)
#    = asszem regkif kell mindenre és vmi fgv-es megoldás!

# TODO XXX  _ITT_T
# akkor van gond, ha:
# * random első elemekre van hivatkozás a szövegben, pl.: "(1)"
# * a köv fejezetre hivatkozik a szöveg -- vagy ilyen sajna
# 
# #2 verzió: ellenőrizzük, h az egész dok-ban ua-e a szerkezet
#    -- kezdetnek: warning, ha ua marktype 2 szinten jön elő! XXX
#    -- kell ez? XXX valszeg igen
#       és a végén output: dok szerkezete
#       = strc + cursor.history <- utóbbi az annotate-kből állhat össze! XXX :)
#         egyszerűen 'sstat annotate output' -- és ennyit! XXX :)
#    -- biztató tipp: ha a strc-t nem vágjuk le:
#       lehet a segítségével kikövetelni az egységes felépítést! XXX :)
#
# #3 verzió: aa) ab) ba) (beszúrt izék) kezelése, ha kell ez a magyarban XXX

