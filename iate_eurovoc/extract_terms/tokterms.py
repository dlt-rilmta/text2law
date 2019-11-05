#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    author: Noémi Vadász
    last update: 2019.10.18.

"""

from os import path
import sys
sys.path.append(path.abspath('/home/vadasz/ownCloud/emtsv/emtokenpy/'))
from io import StringIO
import quntoken.quntoken as q


def read_tsv():

    terms = dict()

    for line in sys.stdin:
        split_line = line.strip().split('\t')
        terms[split_line[0]] = split_line[1]

    return terms


def tokenize(terms):

    cmd = ['preproc', 'snt', 'sntcorr', 'sntcorr', 'token', 'convtsv']

    for id_, term in terms.items():
        toprint = list()
        for line in q.tokenize(cmd, StringIO(term)):
            if line.strip():
                toprint.append(line.strip())
        print(id_ , '\t', '@'.join(toprint))


def main():

    terms = read_tsv()
    tokenize(terms)

if __name__ == "__main__":
    main()