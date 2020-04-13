
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

# there must be exactly 1 numberer code '{.}' per marktype!
# the numberer code must be present in 'numberers'!
# marktypes should not contain whitespace!
# (use preproc_marks.sed to achieve this)
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

