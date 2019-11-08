#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    author: Noémi Vadász
    last update: 2019.10.17.

"""
import sys
import xml.etree.ElementTree as ET


def read_xml():

    tree = ET.parse(sys.stdin)

    return tree


def print_terms(terms):

    for id, term in terms.items():
        print(id, term, sep='\t')


def extract_terms(tree):

    terms = {}

    root = tree.getroot()

    for record in root:
        value = ''
        key = ''
        for term in record:
            if term.tag == 'LIBELLE':
                value = term.text
            elif term.tag == 'DESCRIPTEUR_ID':
                key = term.text

        terms[key] = value

    return terms


def main():

    tree = read_xml()
    terms = extract_terms(tree)
    print_terms(terms)


if __name__ == "__main__":
    main()
