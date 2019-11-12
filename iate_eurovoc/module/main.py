#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    author: Ágnes Kalivoda
    last update: 2019.10.25.

"""

import csv
import re
import sys
import os


def get_termdict(path):
    """
    - soronként beolvassa a term-öket vagy descriptorokat tartalmazó fájlt
    - a sorokat kettévágja ID-ra és elnevezésre, a felesleges space-eket törli
    - ha az elnevezés még nem szerepel kulcsként a dictionary-ben, akkor létrehozza ezt a kulcsot egy üres listával
      FONTOS: azonos elnevezéshez több ID is tartozhat (legalább is az IATE esetében), ezért kell a lista!
    - a megfelelő kulcshoz hozzáadja az új ID-t
    """

    termdict = {}
    maxlen = 0

    with open(path, encoding='utf-8') as fr:
        for line in fr:
            uid, term = line.strip().split('\t')
            uid = re.sub(r'\s+', '', uid)
            term = re.sub(r'\s+', '', term)
            if term not in termdict.keys():
                termdict[term] = []
            termdict[term].append(uid)
            actlen = term.count('@') + 1
            if maxlen < actlen:
                maxlen = actlen

    return termdict, maxlen


def canonical(ls):
    """
    a token-szekvenciát olyan formájúra alakítja, hogy kereshető legyen a dictionary kulcsai között úgy, hogy:
    - végigmegy egyesével a szekvencia tokenjein
    - ha az utolsóhoz ér, annak a lemmáját őrzi meg
    - ha egyéb token van soron, annak a formját őrzi meg
    - az így létrejött szekvencia elemeit @-cal köti össze
    """

    canonized_ls = []
    for i, item in enumerate(ls):
        if i == len(ls)-1:
            canonized_ls.append(item[2])
        else:
            canonized_ls.append(item[1])
    return '@'.join(canonized_ls)


def add_annotation(act_sent, i, r, hit_counter, ctoken, termdict):
    """
    - beilleszti a részletes annotációt a találat első szavához (ha egyszavas a találat, akkor végzett is)
    - többszavas találat esetén a maradék szavaknál jelzi, hogy ezek hányadik találatnak a részei
    """

    # TODO a × helyére mi kell? ez nem új találat, egyszerűen több ID tartozik ugyanahhoz a term-höz
    act_sent[i][-1] += '{}:{};'.format(hit_counter, '×'.join(termdict[ctoken]))
    if '@' in ctoken:
        for x, token in enumerate(act_sent):
            if x > i and x < r:
                act_sent[x][-1] += '{};'.format(hit_counter)

    return act_sent


def annotate_sent(act_sent, termdict, maxlen):
    """
    - a találat-számlálót 1-re állítja minden új mondat esetén
    - a mondat minden tokenjéhez hozzáad egy új oszlopot (kezdetben csak dummy '_', aztán ez cserélődik valós értékekre, amikor vannak ilyenek)
      FONTOS: ennek mindenképp KÜLÖN kell lennie a következő for-tól!
    - végigmegy a mondat tokenjein:
        - az aktuális tokentől kezdve végigveszi az összes token-szekvenciát, a mondat végével bezárólag, pl.
          'süt a nap' -> 'süt', 'süt a', 'süt a nap'; 'a', 'a nap'; 'nap'
        - minden token-szekvenciát átad egy függvénynek, ami a dictionary-nek megfelelő formátumban hozza ezeket
        - ha az átalakított szekvencia megtalálható a dictionary kulcsai között:
            - meghív egy függvényt, ami a pontos annotációt beilleszti a megfelelő oszlopba
            - növeli eggyel a találat-számlálót
    - végül elvégez pár formai igazítást az utolsó oszlopon
    """

    hit_counter = 1
    all_tokens = len(act_sent)
    if all_tokens < maxlen:
        maxlen = all_tokens

    for i, token in enumerate(act_sent):
        act_sent[i].append('_')

    for i, token in enumerate(act_sent):
        for r in range(1, maxlen + 1):
            ctoken = canonical(act_sent[i:r])
            if ctoken in termdict.keys():
                act_sent = add_annotation(act_sent, i, r, hit_counter, ctoken, termdict)
                hit_counter += 1

        act_sent[i][-1] = act_sent[i][-1].rstrip(';')
        act_sent[i][-1] = re.sub(r'^_(.+)$', r'\1', act_sent[i][-1])
            
    return act_sent


def process_corpus(iate_dict, eurovoc_dict, maxlen_iate, maxlen_eurovoc):
    """
    beolvassa a korpuszt soronként, és a sor típusától függően:
    - ha a sor hossza nulla, akkor egy régi mondat befejeződött, és új kezdődik -> a régi mondatot ezen a ponton dolgozza fel*
    - ha #-es sor, rögtön kiírja a standard outputra
    - egyéb esetben egy mondat közepén jár, és gyűjtögeti a mondat tokenjeit

    * a mondat feldolgozása így történik:
    - kétszer meghívja az annotáló-függvényt: először az IATE term-ök, aztán az Eurovoc descriptorok beillesztéséhez
    - az immár 12 oszlopos, felannotált mondatot soronként kiírja a standard outputra
    - üríti az act_sent listát, hogy tokenenként egy újabb mondat kerülhessen bele
    - kiírja a mondatvéget jelző üres sort a standard outputra
    """

    reader = csv.reader(iter(sys.stdin.readline, ''), delimiter='\t', quoting=csv.QUOTE_NONE)

    act_sent = []

    for line in reader:

        if len(line) == 0:
            if len(act_sent) != 0:
                act_sent = annotate_sent(act_sent, iate_dict, maxlen_iate)
                act_sent = annotate_sent(act_sent, eurovoc_dict, maxlen_eurovoc)
                for item in act_sent:
                    print('\t'.join(item), file=sys.stdout)
                act_sent = []
            print('\t'.join(line), file=sys.stdout)

        elif line[0].startswith('#'):
            print('\t'.join(line), file=sys.stdout)

        else:
            act_sent.append(line)


def main():
    """
    - kétszer meghívja a dictionary-gyártó függvényt: először az IATE term-ök, aztán az Eurovoc descriptorok beolvasásához
    - a két dictionary-t átadja a korpusz-feldolgozó függvénynek
    """
    
    # '../extract_terms/tokterms/{iate|eurovoc}.tsv'
    dir_part = os.path.join(
      os.path.dirname(__file__),
      os.pardir,
      'extract_terms',
      'tokterms'
    )
    iate_path = os.path.join( dir_part, 'iate.tsv')
    eurovoc_path = os.path.join( dir_part, 'eurovoc.tsv')

    iate_dict, maxlen_iate = get_termdict(iate_path)
    eurovoc_dict, maxlen_eurovoc = get_termdict(eurovoc_path)

    process_corpus(iate_dict, eurovoc_dict, maxlen_iate, maxlen_eurovoc)


if __name__ == "__main__":
    main()

