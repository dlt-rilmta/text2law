
# explore the structure of hierarchical docummens (e.g. law)

import sys
import re

# (count everything from zero!)

NOLEVEL = -1
level = NOLEVEL              # at what level we are

strc = []                    # marktype at level 'l'

cursor = []                  # we are at which item of marktype at level 'l'

DEBUG = False
#DEBUG = True

# ----- "CONFIG" PART

# generating / querying numberers
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
    return "{{letter#{}}}".format( n ) # TODO general solution needed

def get_Li( m ):
  if m.isalpha(): # TODO maybe this allows other than [a-z]
    return ord( m ) - ord( 'a' )
  else:
    return "{{letter#{}}}".format( m ) # TODO general solution needed

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
  return "{{roman#{}}}".format( n ) # TODO general solution needed

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
  return "{{roman#{}}}".format( m ) # TODO general solution needed

def get_T( n ): # ELSŐ MÁSODIK ... (Hungarian for: FIRST SECOND ...)
  n += 1
  if n ==  1: return 'ELSŐ'
  if n ==  2: return 'MÁSODIK'
  if n ==  3: return 'HARMADIK'
  if n ==  4: return 'NEGYEDIK'
  if n ==  5: return 'ÖTÖDIK'
  if n ==  6: return 'HATODIK'
  if n ==  7: return 'HETEDIK'
  if n ==  8: return 'NYOLCADIK'
  if n ==  9: return 'KILENCEDIK'
  if n == 10: return 'TIZEDIK'
  return "{{text#{}}}".format( n ) # TODO general solution needed

def get_Ti( m ):
  if m == 'ELSŐ':       return 0
  if m == 'MÁSODIK':    return 1
  if m == 'HARMADIK':   return 2
  if m == 'NEGYEDIK':   return 3
  if m == 'ÖTÖDIK':     return 4
  if m == 'HATODIK':    return 5
  if m == 'HETEDIK':    return 6
  if m == 'NYOLCADIK':  return 7
  if m == 'KILENCEDIK': return 8
  if m == 'TIZEDIK':    return 9
  return "{{text#{}}}".format( m ) # TODO general solution needed

# key ('code'): a '{.}' pattern which represents the given numberer
# 'regex':      format of the numberer -- always enclosed in '(...)'!
# 'get_num:     return "number" based on index, e.g. "IV" <- 3 
# 'get_index:   return index based on "number", e.g. 3 <- "IV"
numberers = {
  '{D}': { 'regex': '([0-9]{1,3})',     'get_num': get_D, 'get_index': get_Di },
  '{L}': { 'regex': '([a-z]{1})',       'get_num': get_L, 'get_index': get_Li },
  '{R}': { 'regex': '([CDILMVX]{1,8})', 'get_num': get_R, 'get_index': get_Ri },
  '{T}': { 'regex': '((?:TIZEN|HUSZON|HARMINC|NEGYVEN)?(?:ELSŐ|EGYEDIK|MÁSODIK|KETTEDIK|HARMADIK|NEGYEDIK|ÖTÖDIK|HATODIK|HETEDIK|NYOLCADIK|KILENCEDIK|TIZEDIK))',
                                        'get_num': get_T, 'get_index': get_Ti }
}
# {D} = arabic number -- 3 digit is enough (years will not be included)
# {L} = letter -- maybe this will be: {1,2}
# {R} = roman number -- several digits may be needed
# {T} = Hungarian numbers written in letters (TODO full solution)

# there should be exactly 1 numberer code '{.}' per marktype!
# marktypes should not contain whitespace! (use preproc_marks.sed to achieve this)
marktypes = [
  '{D}._§',        # 0 '1._§'
  '({D})',         # 1 '(1)'
  '{L})',          # 2 'a)'
  '{R}.',          # 3 'I.'
  '{D}.',          # 4 '1.'
  '{D}._cikk',     # 5 '1._cikk'
  '{R}._FEJEZET',  # 6 'I._FEJEZET'
#  '{T}_RÉSZ'       # 7 'ELSŐ_RÉSZ'
  # ...
  # TODO more marktypes to come
]

# filtering
# if next word is in this list then ignore it even if it is formally a mark
# in this case the word looking like a mark is usually a legal reference
# Hungarian words
mayberef_if_nextword = {
  'és',
  'napjától',
  'számú',
  'bekezdés.*',
  'pont.*',
  'alpont.*',
  'melléklet.*',
  'fejezet.*',
  'törvény.*',
  'cikk.*'
}

# ----- END OF "CONFIG" PART

# util
def dprint(*args, **kwargs):
  if DEBUG:
    print(*args, **kwargs)

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

# identify corresponding numberer for each marktype
marktype_numberers = []
for mt in marktypes:
  for code in numberers:
    if code in mt: # e.g. '{D}' in '({D})' -- cool! :)
      marktype_numberers.append( code )
      break
# compiling regexes

def fsc( regex ):
  """
  Compile a regex with adding anchors to use for matching whole string.
  """
  return re.compile( '^' + regex + '$' )

# regexes for 'marktypes', e.g. {L}) -> ([a-z]{1})\)
rxptn_marktypes = []
for ( i, ptn ) in enumerate( marktypes ):
  rxptn = re.escape( ptn )
  # change back '{' and '}' as they are part of numberer codes
  rxptn = rxptn.replace( "\\{", "{" )
  rxptn = rxptn.replace( "\\}", "}" )

  code = marktype_numberers[i]
  rxptn = rxptn.replace( code, numberers[code]['regex'] ) 
 
  rxptn_marktypes.append( fsc( rxptn ) )

# regexes for 'mayberef_if_nextword'
rxptn_mayberef_if_nextword = list( map( fsc, mayberef_if_nextword ) )

# functions

def get_mark( index, pos ):            # e.g. 1, 2
  """
  Returns: a mark = item at 'pos' in 'marktypes[index]'.
  """
  mt = marktypes[index]                # e.g. "({D})"
  code = marktype_numberers[index]     # e.g. "{D}"

  mark = mt.replace( code, numberers[code]['get_num']( pos ) )
                                       # e.g. "(3)" <= get_D( 2 ) = 3

  return mark
# TODO put this into search_pos() or something

def search_pos( stuff, pos ):
  """
  Search for 'stuff' in all marktypes, but only at position 'pos'.
  Returns: index of marktype (or None)
  """

  for mti in range( len( marktypes ) ): 
    mark = get_mark( mti, pos )
    if mark == stuff:
      return mti
  return None

def search_ser( stuff, index ):               # e.g. "(3)", 1
  """
  Search for 'stuff' in one marktype, i.e. 'marktype[index]'.
  Returns: pos (=index) of mark (or None)
  """

  # task: get "number" from marktype + stuff:
  #  marktype           stuff      ->        "number"
  #  '({D})'            '(3)'                3
  #  '({D})'            '(71)'               71
  #  'zaz{R}._FEJEZET'  'zazXVIII._FEJEZET'  XVIII

  code = marktype_numberers[index]            # e.g. "{D}"

  # compiled regex! :)
  res = rxptn_marktypes[index].match( stuff ) # e.g. ^\(([0-9]{1,3})\)$ to "(3)"

  if res is not None:
    number = res.groups()[0]                  # e.g. 3
    return numberers[code]['get_index']( number )
                                              # e.g. 2 <= get_Di( 3 )
    # that means "(3)" is at index 2 in marktype 1

  return None

def annotate( word, level, marktype, message, mode='full' ):
  """
  Put some [[.:...] codes into text.
  If a token is considered real mark
    then full description '[[F:...]' and type '[[T:...]' are included,
  else
    an simple '[[X:...]' annotation is provided.
  """
  if mode == 'full':
    print( "[[F:\"{}\"=type{}{}@{}={}]]".format( # F = full
      word,
      marktype,
      message,
      level,
      '+'.join( "t{}/{}".format( t, i ) for (t, i) in list( zip( strc, cursor ) ) )
    ), end = ' ' )
    print( "[[T:{}]]".format(                    # T = only types at levels
      '+'.join( "t{}".format( t ) for (t, i) in list( zip( strc, cursor ) ) )
    ), end = ' ' )
  elif mode == 'simple':
    print( "[[X:\"{}\"{}]]".format(              # X = only word + message
      word,
      message
    ), end = ' ' )

for line in sys.stdin:

  # iterate over bigrams to be able to look at "next word"
  ws = line.split()                    # ws = tokens separated by spaces
  i = -1

  while i < len(ws)-1:

    i += 1
    w = ws[i]

    print( w, end = ' ' )

    nextw = ''
    if i+1 < len(ws):
      nextw = ws[i+1]

    is_mark = False
    if any( ptn.match( w ) for ptn in rxptn_marktypes ):
      is_mark = True

    # https://stackoverflow.com/questions/3040716
    # cond "next word implies that this is probably a legal reference"
    if any( ptn.match( nextw ) for ptn in rxptn_mayberef_if_nextword ):

      # TODO ugly code repetition -- se end of script
      # cond "... and this is a mark"
      # -> it is likely a legal reference
      if( is_mark ):
        annotate( w, None, None, 'mayberef<-nextword', mode="simple" )

      # cond "... and this is not a mark"
      # -> it is likely a plain word
      else:
        pass
        #annotate( w, None, None, '!mt', mode="simple" )

      continue

    found = False

    m = search_pos( w, 0 )           # => search for 'w' as a mark in pos=0
    # cond "mark@pos=0"
    if m is not None:                # first (0.) item of a given marktype
      found = True
      # cond "mark@pos=0 and not the same marktype as 1 level outer"
      if not strc or strc[-1] != m:  # so not the "a) / a)" case
        level += 1
        strc.append( m )             # TODO ensure to be level_th item
        cursor.append( 0 )           # TODO ensure to be level_th item
        annotate( w, level, m, "/1st" )
      # cond "mark@pos=0 but the same as 1 level outer (the 'a) a)' case)"
      else:
        annotate( w, None, None, "mt1st2x", mode="simple" )
                                     # TODO handling "c) a)" case

    # cond "not mark@pos=0 and level>-1"
    elif level > NOLEVEL:
      for n in range( 0, level+1 ):  # look at next item
                                     # at current level (n=0) and outer levels
                                     # 'level+1' ok as 2nd level means 3 level
        L = level - n;
        j = search_ser( w, strc[L] ) # => search for 'w' in a given marktype
        # cond "found in the given marktype"
        if j is not None:            # notfirst item of current/outer levels
          found = True
          # cond "... and OK: the subsequent mark"
          if j == cursor[L] + 1:
            level -= n               # go to appropriate outer level
            del strc[level+1:]       # delete inner levels
            del cursor[level+1:]
            cursor[level] += 1       # proceed to next item @ this outer level
            msg = "/next" if n == 0 else "/next<-up" + str( n )
            annotate( w, level, strc[level], msg )
          # cond "... and not OK: not the subsequent mark and level>-1"
          # -> probably a legal reference / TODO maybe a gap
          else:
            annotate( w, None, None, "mt:ok_+_m!ok", mode="simple" )
                                     # TODO handle gap, i.e. "a) c)"
                                     # TODO handle "c) b)" case
          break

    # TODO can be the below part handled by for/else more elegantly?

    # cond "not mark@pos=0 and not in existing marktypes"
    if not found:

      # cond "... and this is a mark"
      # -> it is likely a legal reference
      if is_mark:
        annotate( w, None, None, 'mt!first!occur', mode="simple" )

      # cond "... and this is not a mark"
      # -> it is likely a plain word
      else:
        pass
        #annotate( w, None, None, '!mt', mode="simple" ) # sima szó

  print()

