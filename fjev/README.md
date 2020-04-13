## fjev = "formális jogi egységekre vagdosás" = "splitting text into formal legal units"

This script explores the structure of hierarchical documents (e.g. law).

### getting started in 5 minutes

Usage: type `make`. A file called `out` is produced
processing `hu-*` files in this directory.
Take a look at `out`!

It contains two main kinds of annotation:
 * "type" = `[[T:...` (only types)
 * "full" = `[[F:...` (full description)

Tested on Debian 8.11, works maybe on other linuxes or linux-like environments.

### concepts

This script attempts to reveal the hierarchical structure of texts.
This is something like identifying
what kind of parts, chapters, sections, subsections are there. 
It is based mainly on the idea that individual units have
_consecutive_ numbering. That means, in practice,
if we have had `Article_1` yet, so we are inside the first article,
the coming `Article_2` will mark the next article,
but if `Article_42` is encountered in the text,
that is probably something else, usually a reference to another unit. 
The motivation for creating this script was to analyse legislation.

A _mark_ is a token which marks the beginning of a structural unit.
In law, it can be `Article_1`, `1._§`, or `a)` or something like that.
Marks should not contain whitespaces, we use underscores.

A _numberer_ is a kind of counter which numbers the particular units,
e.g. "1 2 3 4 ..." (referred to as `{D}`) or
"I II III IV ..." (referred to as `{R}`).

A _marktype_ is the formal description of the mark
which separates variable (i.e. numberer) part and fixed part of it.
It is `Article {D}`, `{D}. §` and `{L})` for the above examples respectively.
(Guess what `{L}` means.)

### annotations

Marks get "full" and "type" annotation both,
plain words looking like a mark gets a "simple" annotation.

Everything are numbered from zero.

#### "type" annotation

 * `[[T:t0+t1+t2]]`
i.e. a `T:` = "type" description that says
that we are currently at a point in the document which is 
inside a type 2 mark (`t2`)
which is inside a type 1 mark (`t1`)
which is inside a type 0 mark (`t0`) at last.
E.g. `1._§ / (1) / a)` or `4._§ / (3) / e)`.

Main message:
_A freqency list of `[[T:...` descriptions
shows the hierarchical structure of the document quite well._

To create this list type: `make freq` and see `out.types.freq`.

#### "full" annotation

 * `[[F:"b)"=type2/next@2=t0/1+t1/0+t2/1]]`
i.e. a `F:` = "full" description that says
that `b)` is a `type2` mark, a non-first item (`next`)
at nested level 2 (`@2`)
and that we are currently at a point in the document which is
inside a #1 item of type 2 mark (`t2/1`) -- this particular `b)` -- at level 2,
which is inside a #0 item of type 1 mark (`t1/0`) at level 1,
which is inside a #1 item of type 0 mark (`t0/1`) at level 0.
Concretely: `2._§ / (1) / b)`.

 * `[[F:"3._§"=type0/next<-up2@0=t0/2]]`
This annotaton exemplifies "level change".
`<-up2` means that here we come outer by 2 levels
compared to the previous mark in the document.
Concretely: e.g. `3._§` which comes after
a mark having `2._§ / ({D}) / {L})` format.

#### "simple" annotation

 * `[[X:"word"message]]`
where `word` is the word being annotated
and `message` can be one of the following:
   * `mayberef<-nextword` = based on the next word
this is not considered a mark (it is likely a legal reference instead)
   * `mt1st2x` = this is a #0 item of a marktype
which is the same as the outer marktype (the "a) a)" case)
   * `mt:ok_+_m!ok` = marktype OK but mark not OK,
i.e. not immediately subsequent
   * `mt!first!occur` = a mark which is non-first
and does not fit into an existing marktype

### configuration

You have to edit `fjev_config.py`.

To modify `marktypes` (using existing numberers)
just edit / add / remove some lines.

To add a new numberer is somewhat more complicated.
You should add it to the `numberer` dict,
and also add the corresponding `get_num` and `get_index` functions.

To modify `mayberef_if_nextword` which contains "next words"
-- which render current word a plain word
even if it looks like a mark -- just edit this set.

