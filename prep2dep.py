import re
import os
from text2law import get_args


def read(inp):
    for fl in inp:
        with open(fl, encoding='utf-8') as f:
            yield f.read().replace(u'\xa0', u' ').replace("  ", " "), os.path.basename(fl)


def tokmod(txt):
    txtls = [sent.split("\n") for sent in [sent for sent in txt.split("\n\n")]]
    newls = [txtls[0]]
    for i, sent in enumerate(txtls[1:]):
        # print("sent:", sent)
        # first_word = sent[0].split("\t")[0]
        for char in sent[0]:
            # sent[0][0] in "§(" ez nem jó, mert ( -vel kezdődik a bekezdés is
            # (len(first_word) > 1 and first_word.isupper()) or ... -> out_ut_... "ÖTM utasítása" gond
            if char and (sent[0][0].islower() or sent[0][0] == "§"):
                newls[-1].extend(sent)
                break
        else:
            newls.append(sent)
    return "\n\n".join(["\n".join(sent) for sent in newls])


def replmatch(match):
    punct = match.group(1)
    replwith = match.group(2)[1:] if match.group(2)[0] == "\n" else match.group(2)
    return punct + "\n\n"+replwith


def process(inps, outp):
    txtlists = []  # ellenőrzéshez

    pat_paragraph = re.compile(r"""
    ([^\n])(\n\d+\.\t.+?\n
    §\t.+?\n
    (?:\(\t.+?\n
    \d+\)\t.+?\n)?
    [A-ZÖÜÓŐÚÉÁŰÍ])
    """, re.VERBOSE)

    pat_num_listing = re.compile(r"""
    ("\s*\\n\s*")\n
    (\d{1,3}\.\t.+?\n
    [^§)])
    """, re.VERBOSE)

    pat_abc_listing = re.compile(r"""
    ([^\n])(\n[a-z]{1,3}
    (?:(?:\)\t.+?\n)|(?:\t.+?\n\)\t.+?\n))
    (?!pont))
    """, re.VERBOSE)

    pat_rom_w_dot = re.compile(r"""
    ([^\n]\n[;:.,]\t.+?)\n
    ([IVXLCDM]+\.\t.+?\n
    [A-ZÖÜÓŐÚÉÁŰÍa-zöüóőúéáűí])
    """, re.VERBOSE)

    pat_dot_col = re.compile(r"""
    ([^\n]\n[;]\t.+?)\n
    ([a-zöüóőúéáűí]+[^.)])
    """, re.VERBOSE | re.IGNORECASE)

    for inp in inps:
        forparse, fl = tokmod(inp[0]), inp[1]

        forparse = pat_paragraph.sub(replmatch, forparse)
        forparse = pat_num_listing.sub(replmatch, forparse)
        forparse = pat_abc_listing.sub(replmatch, forparse)
        forparse = pat_rom_w_dot.sub(replmatch, forparse)
        forparse = pat_dot_col.sub(replmatch, forparse)

        with open(os.path.join(outp, fl), "w", encoding="utf-8", newline="\n") as f:
            f.write(forparse)

    # teszt ellenőrzés: maradék hosszú mondatok
        txtls = [sent.split("\n") for sent in [sent for sent in forparse.split("\n\n")]]
        txtlists.append(txtls)
    with open("long_sents2.txt", "w", encoding="utf-8") as f:
        for txtls in txtlists:
            for sent in txtls:
                if len(sent) > 100:
                    print("###################\n", "\n".join(sent), file=f)
    # teszt ellenőrzés vége


def main():
    args = get_args()
    inp = read(args['files'])
    os.makedirs(args['dir'], exist_ok=True)
    process(inp, args['dir'])


if __name__ == "__main__":
    main()
