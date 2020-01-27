#! /usr/bin/env python3

import os
import argparse
from glob import glob


def write(dir, outp, ext):
    os.makedirs(dir, exist_ok=True)
    for outpf in outp:
        with open(os.path.join(dir, os.path.splitext(outpf[0])[0] + ext), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n\n".join(["\n".join(outpf[1][i]) for i, sent in enumerate(outpf[1])]))


def read(files):
    for fl in files:
        with open(fl, encoding="utf-8") as f:
            yield os.path.basename(fl), f.read()


def process(inp, is_with_dep):
    minus_pos = 0 if is_with_dep else 3
    for emtsv_doc in inp:
        sents = emtsv_doc[1].split("\n\n")
        doc = []
        print(emtsv_doc[0])
        for i, sent in enumerate(sents):
            id_count = 0
            out_sent = []
            # from: form, anas, lemma, xpostag, upostag, feats, id, deprel, head, _, _, NP-BIO, NER-BIO
            # to: id, form, lemma, upostag, xpostag, feats, head, deprel, deps, misc, NER-BIO, NP-BIO
            for j, word_attrs in enumerate(sent.split("\n")):
                col = [elem for elem in word_attrs.split('\t')]
                if len(col) < {True: 10, False: 7}[is_with_dep]:
                    continue

                if i+j < 1:
                    # with dep: form, wsafter, anas, lemma, xpostag, upostag, feats, NP-BIO, NER-BIO
                    # without dep: form, wsafter, anas, lemma, xpostag, upostag, feats, id, deprel, head, NP-BIO, NER-BIO
                    iden, form, lemma, upostag, xpostag, feats, head, deprel, deps, misc, ner, np, = \
                        "id", "form", "lemma", "upos", "xpos", "feats", "head", "deprel", \
                        "deps", "misc", "marcell:ne", "marcell:np"
                else:
                    id_count += 1
                    if col[1] == '""':
                        space_after = "SpaceAfter=No"
                    else:
                        space_after = "_"
                    if is_with_dep:
                        iden, head, deprel = col[7], col[9], col[8]
                    else:
                        iden, head, deprel = id_count, "_", "_"

                    form, lemma, upostag, xpostag, feats, deps, misc, ner, np = \
                        col[0], col[3], col[5], col[4], col[6], "_", space_after, col[11-minus_pos], col[10-minus_pos]

                out_sent.append(
                    "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format
                    (iden, form, lemma, upostag, xpostag, feats, head, deprel, deps, misc, ner, np)
                )

            doc.append(out_sent)

        yield emtsv_doc[0], doc


def get_args(basp):
    """
    :param basp: folder of output
    :return: 1: folder of output, 2: folder of input, 3: does the input contains dependency parsing or not
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')
    parser.add_argument('-p', '--dependency', help='Is the input contains output of Dependency parser? [True / False]',
                        default=False, nargs='?', type=bool)
    args = parser.parse_args()
    files = []

    if args.filepath:
        for p in args.filepath:

            poss_files = glob(p)
            poss_files = [os.path.abspath(x) for x in poss_files]
            files += poss_files
            # files += p

    if args.directory:
        basp = os.path.abspath(args.directory)

    return {'dir': basp, 'files': files, 'dep': args.dependency}


def main():
    """
    usage: python3 convert2conll.py <input> -d <output> -p <does the input contains dependency parsing? [True / False (default)]>
    """
    basp = 'convert2conll_output_'  # + strftime("%Y-%m-%d_%H%M%S", gmtime())
    args = get_args(basp)
    inp = read(args['files'])
    outp = process(inp, args['dep'])
    write(args['dir'], outp, ".conll")


if __name__ == '__main__':
    main()
