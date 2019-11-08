#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    author: Noémi Vadász
    last update: 2019.10.18.

"""
import sys
import xml.etree.ElementTree as ET


def read_xml():

    tree = ET.parse(sys.stdin)

    return tree


def print_terms(terms):

    for id, term in terms.items():
        print(id + '-' + term[0], term[1], sep='\t')


def extract_terms(tree):

    terms = {}

    root = tree.getroot()

    for term in root.iter('termEntry'):

        iate = term.get('id').split('IATE-')[1]
        for data in term.iter('descrip'):
            if data.get('type') == 'subjectField':
                eurovoc = data.text
        for data in term.iter('term'):
            terms[iate] = (eurovoc, data.text)

    return terms


def main():

    tree = read_xml()
    terms = extract_terms(tree)
    print_terms(terms)


if __name__ == "__main__":
    main()
