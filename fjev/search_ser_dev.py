
import re

# task: get '1' from two peices of info below:

data = [
  ( "({D})", "(72)" ),
  ( "zaz{R}._FEJEZET", "zazXVIII._FEJEZET" )
]

for ( ptn, stf ) in data:
  print( ptn )
  print( stf )
  ptn = re.escape( ptn )
  ptn = re.sub( "\\\\{[^}]*\\\\}", "(.*)", ptn )
  res = re.match( ptn, stf )
  print ( res.groups()[0] )

exit( 0 )

B = '{'
E = '}'

pb = 0
sb = 0
while True:
  if ptn[pb] != B and stf[sb] != B:
    print( ptn[pb] )
    print( stf[sb] )
    pb += 1
    sb += 1
  else:
    print( pb )
    print( sb )
    # here: pb = sb
    break

pe = len(ptn)-1
se = len(stf)-1
while True:
  if ptn[pe] != E and stf[se] != E:
    print( ptn[pe] )
    print( stf[se] )
    pe -= 1
    se -= 1
  else:
    print( pe )
    print( se )
    # here: len(ptn)-pe = len(stf)-se
    break

print( "'" + stf[sb:se+1] + "'" )

