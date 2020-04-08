
import sys
import re

# mindent 0-tól számolunk!!! :)

# jogszabályok (hierarchikus dokumentumok) szerkezetének feltárása

mark = []
# XXX csak 1 token lehet => preproc_marks.sed alak0tja ilyenre
mark.append( ['1._§', '2._§', '3._§', '4._§'] )
mark.append( ['(1)', '(2)', '(3)', '(4)'] )
mark.append( ['a)', 'b)', 'c)', 'd)'] )
mark.append( ['I.', 'II.', 'III.', 'IV.'] )
mark.append( ['1.', '2.', '3.', '4.'] )
mark.append( ['1._cikk', '2._cikk', '3._cikk', '4._cikk'] )
mark.append( ['I._FEJEZET', 'II._FEJEZET', 'III._FEJEZET', 'IV._FEJEZET'] )
# XXX egyéb mark-típusok
# XXX megoldani, hogy bármeddig mehessenek ezek -- gondolom fgv kell

NOLEVEL = -1
level = NOLEVEL                        # hányadik szinten vagyunk

strc = []                              # l-edik szinten milyen mark van

cursor = []                            # l-edik szinten lévő marktípus
                                       # hányadik eleménél tartunk

def search_pos( stuff, pos ):
  """
  'stuff'-ot keressük 'mark' (list of lists) allistáinak 'pos' pozíciójában
  return: az allista indexe (vagy None)
  """
  for ( m, sublist ) in enumerate( mark ):
    if sublist[pos] == stuff:
      return m
  return None

def search_subl( stuff, index ):
  """
  'stuff'-ot keressük 'mark' (list of lists) 'index'-edik allistájában
  return: az elem indexe (vagy None)
  """
  if mark[index] is not None:
    for ( j, elem ) in enumerate( mark[index] ):
      if elem == stuff:
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
        j = search_subl( w, strc[L] ) # => w-t keresem mark adott allistájában
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
# #1 verzió: bárhol bármilyen szerkezetet megengedünk :)

# TODO XXX
# unlimited 'mark: e) f) g) h) ... :)
# #2 verzió: ellenőrizzük, h az egész dok-ban ua-e a szerkezet
#    -- kezdetnek: warning, ha ua marktype 2 szinten jön elő! XXX
#    -- kell ez? XXX valszeg igen
#       és a végén output: dok szerkezete
#       = strc + cursor.history <- utóbbi az annotate-kből állhat össze! XXX :)
#         egyszerűen 'sstat annotate output' -- és ennyit! XXX :)
#    -- biztató tipp: ha a strc-t nem vágjuk le:
#       lehet a segítségével kikövetelni az egységes felépítést! XXX :)
# #3 verzió: aa) ab) ba) (beszúrt izék) kezelése, ha kell ez a magyarban XXX

