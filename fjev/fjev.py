
import sys
import re

# jogszabályok (hierarchikus dokumentumok) szerkezetének feltárása

# mindent 0-tól számolunk!!! :)

NOLEVEL = -1
level = NOLEVEL                        # hányadik szinten vagyunk

strc = []                              # l-edik szinten milyen mark van

cursor = []                            # l-edik szinten lévő marktípus
                                       # hányadik eleménél tartunk

DEBUG = False
#DEBUG = True

# util
def dprint(*args, **kwargs):
  if DEBUG:
    print(*args, **kwargs)

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

# számozók elemeinek lekérdezése/generálása
def get_D( n ): # 1 2 3 4 ...
  n += 1
  return str( n )

def get_Di( m ):
  m = int( m )
  m -= 1
  return m

def get_L( n ): # a b c d ...
  n += 1
  if n <= 26:
    return chr( ord( 'a' ) + n - 1 )
  else:
    return "{{letter#{}}}".format( n ) # XXX jobban? '{{' => '{'

def get_Li( m ):
  if m.isalpha(): # XXX ez lehet, h [a-z]-n kívül mást is megenged
    return ord( m ) - ord( 'a' )
  else:
    return "{{letter#{}}}".format( m ) # XXX jobban? '{{' => '{'

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

def get_Ri( m ):
  if m == 'I':    return 0
  if m == 'II':   return 1
  if m == 'III':  return 2
  if m == 'IV':   return 3
  if m == 'V':    return 4
  if m == 'VI':   return 5
  if m == 'VII':  return 6
  if m == 'VIII': return 7
  if m == 'IX':   return 8
  if m == 'X':    return 9
  return "{{roman#{}}}".format( m ) # XXX jobban? '{{' => '{'

# számozók: get index -> szám ; get szám -> index
# mindig legyen benne '(...)', mert csoportként akarjuk felismerni!
numberers = {
  '{D}': { 'regex': '([0-9]{1,3})',     'get_mark': get_D, 'get_index': get_Di },
  '{L}': { 'regex': '([a-z]{1})',       'get_mark': get_L, 'get_index': get_Li },
  '{R}': { 'regex': '([CDILMVX]{1,8})', 'get_mark': get_R, 'get_index': get_Ri }
}
# {D} = arab szám, 3 számjegy sztem elég, így évszám nem kerül bele :)
# {L} = betű -- esetleg majd {1,2}
# {R} = római szám -- sok számjegy kellhet!

# '[(]' -- így tudom escape-elni, mert a '\' vmiért megduplázódik XXX
# feltesszük, h csak 1 db '{.}' kód van ezekben!
marktypes = [
  '{D}._§',      # 0 '1._§'
  '({D})',       # 1 '(1)'
  '{L})',        # 2 'a)'
  '{R}.',        # 3 'I.'
  '{D}.',        # 4 '1.'
  '{D}._cikk',   # 5 '1._cikk'
  '{R}._FEJEZET' # 6 'I._FEJEZET'
  # ...
]
# XXX csak 1 token lehet => preproc_marks.sed alakítja ilyenre
# XXX egyéb mark-típusok jöhetnének...

# megfelelő regexek belőle: '{L})' -> ([a-z]{1})\)
rxptn_marktypes = []
for ptn in marktypes:
  rxptn = re.escape( ptn )
  # a kódok (marktypes) miatt ezek visszacseréljük...
  rxptn = rxptn.replace( "\\{", "{" )
  rxptn = rxptn.replace( "\\}", "}" )
  for ( code, regex ) in [( k, v['regex']) for ( k, v ) in numberers.items()]:
    rxptn = rxptn.replace( code, regex )
  rxptn_marktypes.append( re.compile( '^' + rxptn + '$' ) )

def get_mark( m, n ):
  """
  visszaad egy konkrét 'mark'-ot: az 'm' indexű marktype 'n'-edik elemét
  """
  mark = marktypes[m]
  for ( code, func ) in [( k, v['get_mark']) for ( k, v ) in numberers.items()]:
    mark = mark.replace( code, func( n ) )
  return mark

# pl.: "(1)"
def search_pos( stuff, pos ):
  """
  'stuff'-ot keressük 'mark' (list of lists) allistáinak 'pos' pozíciójában
  return: az allista indexe (vagy None)
  """

  for ( m, c ) in enumerate( marktypes ): 
    mark = get_mark( m, pos )
    if mark == stuff:
      return m
  return None

# pl.: "(1)"
def search_ser( stuff, index ): # XXX XXX XXX
  """
  'stuff'-ot keressük 'mark' (list of lists) 'index'-edik allistájában
  return: az elem indexe (vagy None)
  """

  # task: get 'mark_number' from ptn + stuff:
  #  ptn                stuff      ->        mark_number
  #  '({D})'            '(1)'                1
  #  '({D})'            '(72)'               72
  #  'zaz{R}._FEJEZET'  'zazXVIII._FEJEZET'  XVIII

  ptn = marktypes[index]

  # compiled regex! :)
  res = re.match( rxptn_marktypes[index], stuff ) # pl.: ^\(([0-9]{1,3})\)$ -> (2)

  if res is not None:
    mark_number = res.groups()[0]

    for ( code, func ) in [( k, v['get_index']) for ( k, v ) in numberers.items()]:
      if ptn.find( code ) > -1: # pl.: "({D})".find( "{D}" )
        # feltesszük, h csak 1 db kód van benne!!!
        return func( mark_number )

  return None

def annotate( word, level, marktype, message, mode='full' ):
  """
  megjelöljük a szövegben a cuccot / vagy legalábbis kiírjuk :)
  """
  if mode == 'full':
    print( "[[F:\"{}\"=type{}{}@{}={}]]".format( # F = full
      word,
      marktype,
      message,
      level,
      '+'.join( "t{}/{}".format( t, i ) for (t, i) in list( zip( strc, cursor ) ) )
    ), end = ' ' )
    print( "[[T:{}]]".format( # T = only types at levels
      '+'.join( "t{}".format( t ) for (t, i) in list( zip( strc, cursor ) ) )
    ), end = ' ' )
  elif mode == 'empty':
    print( "[[X:\"{}\"{}]]".format(
      word,
      message
    ), end = ' ' )

for line in sys.stdin:

  for w in line.split():               # w = tokens sep by spaces

    print( w, end = ' ' )

    found =False

    m = search_pos( w, 0 )             # => keres w @ mark-ok 0. helyein
    # "0-s jelölő"
    if m is not None:                  # adott marktípus 0. azaz első eleme!
      found = True
      # "0-s jelölő és nem ua mint 1-gyel följebb"
      if not strc or strc[-1] != m:    # és nem ua marktípus mint 1-gyel följebb,
                                       # azaz nem "a) pont a) pontja" eset
        level += 1
        strc.append( m )               # XXX tutira a 'level'-edik elem legyen!
        cursor.append( 0 )             # XXX tutira a 'level'-edik elem legyen!
        annotate( w, level, m, "/1st" )
      # "0-s jelölő, de ua mint 1-gyel följebb"
      else:
        annotate( w, None, None, "mt1st2x", mode="empty" )
                                       # XXX kell: a rossz c) a) eset kezelése

    # "nem 0-s jelölő és level>-1"
    elif level > NOLEVEL:
      for n in range( 0, level+1 ):  # akt(n=0) v külsőbb szintű köv elemeket nézzük
                                     # jó a 'level+1' :)
                                     # kb. mert 2-es level == 3 db level 
        L = level - n;
        j = search_ser( w, strc[L] ) # => keres w @ mark-ok adott típusán belül
        # "megvan az adott mt-ben"
        if j is not None:            # akt(n=0) v külsőbb szintű marktípus többedik eleme
          found = True
          # "... és stimmel is: konkrétan a következő!"
          if j == cursor[L] + 1:
            level -= n               # átállunk a megf külsőbb szintre
            del strc[level+1:]       # belsőbb szinteket nullázzuk
            del cursor[level+1:]
            cursor[level] += 1       # továbblépünk 1-gyel (a külső szinten)
            msg = "/next" if n == 0 else "/next<-up" + str( n )
            annotate( w, level, strc[level], msg )
          # "ez a marktípus előfordult már, de az akt nem stimmel és level>-1"
          # -> valszeg vmi ref lesz / esetleg gap
          else:
            annotate( w, None, None, "mt:ok_+_m!ok", mode="empty" ) # nem a következő
                                       # XXX kell: kimaradás kezelése
                                       # XXX kell: a rossz c) b) eset kezelése
          break


    # alábbit esetleg szebben for/else -zel XXX

    # "nem 0-s jelölő és nincs az előfordult mt-k között"
    if not found:
      for ptn in rxptn_marktypes:
        # "... és mt"
        # -> valszeg vmi ref lesz XXX
        if re.match( ptn, w ):
          annotate( w, None, None, 'mt!first!occur', mode="empty" ) # sima szó??? XXX XXX XXX
          break
      # "... és nem is mt"
      # -> valszeg sima szó lesz XXX
      else:
        pass
        #annotate( w, None, None, '!mt', mode="empty" ) # sima szó

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

