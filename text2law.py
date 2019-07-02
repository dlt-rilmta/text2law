#! /usr/bin/env python3

import argparse
import os
import re
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup


def read(files):
    for finp in files:
        with open(finp, encoding="utf-8") as f:
            fname = os.path.splitext(os.path.basename(finp))[0]
            yield (fname, f.read())


def write(outp, dir):
    Path(dir).mkdir(parents=True, exist_ok=True)
    for legislations in outp:
        for legislation in legislations:
            with open(os.path.join(dir, legislation[0]), "w", encoding="utf-8") as f:
                f.write("\n".join(legislation[1]))


def remove_accent(s):
    """
    This function gets a string and switches the accented chars to non accented version:
    öüóőúéáűí -> ouooueaui
    """
    accent_dict = {"á": "a", "ü": "u", "ó": "o", "ö": "o", "ő": "o", "ú": "u", "é": "e", "ű": "u", "í": "i"}

    for key in accent_dict:
        if key in s:
            s = s.replace(key, accent_dict[key])
    return s


def get_prefix(prefix_dict, title):
    title_for_prefix = re.sub(r'\W', "", title).lower()

    if "módosítás" in title_for_prefix:
        return "mod"

    for key in prefix_dict:
        if key in title_for_prefix:
            return prefix_dict[key]
    return ""


def extract_titles(toc, prefix_dict=None):
    abbr_dict = {"tv.": "törvény", " h.": " határozat", " r.": " rendelet", " ut.": " utasítás"}
    pat_page_num = re.compile(r'\s(\d+)$')
    pat_trv = re.compile(r'(\d+[.:](?:\sévi)?)\s(\w+\.)\s(törvény)\s(\w+)')
    pat_rest_leg = re.compile(r'(\d+/\d+\.)\s(\((?:\w+\.?\s)+(?:\d+/)?\d+\.\))\s((?:\w+(?:–|-\w+)?)+\.?)\s(\w+\.?)')
    pat_wspaces = re.compile(r'\s+')

    titles = []
    title = ""
    main_title = None
    current_page = 0

    for cont in toc:
        for key in abbr_dict:
            if key in cont:
                cont = cont.replace(key, abbr_dict[key])
        raw_cont = pat_wspaces.sub(" ", cont.lower())
        title += raw_cont
        if main_title is None:
            main_title = pat_rest_leg.search(title)
            if main_title is None:
                main_title = pat_trv.search(title)
            if main_title:
                title = title[main_title.start():]
                main_title = "{} {} {} {}"\
                    .format(main_title.group(1), main_title.group(2), main_title.group(3), main_title.group(4))

        page = pat_page_num.search(cont)
        if page and current_page <= int(page.group(1)):
            current_page = int(page.group(1))
            if main_title is None:
                main_title = " ".join(raw_cont.strip().split()[0:4])
            prefix = ""
            if prefix_dict:
                prefix = get_prefix(prefix_dict, title)
            title = title.strip().split()
            page_num = title[-1]
            full_title = " ".join(title[0:-1])
            titles.append((main_title, prefix, full_title, page_num))
            title = ""
            main_title = None

    return titles



def extract_legislation(titles, fname, bs_divs):
    pat_page_end = re.compile(r'.{,40}közlöny.{,40}')
    pat_non_chars = re.compile(r'\W')
    pat_sign = re.compile(r's\.\s+k\.,')
    pat_header = re.compile(r'(közlöny(?:\d+évi)?\d+szám)|(\d+szám\w+?közlöny)')

    legislation = []
    legislations = []
    is_legislation = False
    after_signature = False
    leg_title = ""
    for div in bs_divs:
        page_end = "".join(pat_page_end.findall(pat_non_chars.sub("", div.text.lower())))
        for p in div.find_all('p'):
            p_cont = p.text.strip()
            raw_p = pat_non_chars.sub("", p_cont.lower())
            if p_cont == "" or pat_header.search(raw_p):
                continue
            next_p = p.findNext('p')
            if next_p:
                next_p = "" or next_p.text
            for i, title in enumerate(titles):
                raw_title = [pat_non_chars.sub("", title_part).lower() for title_part in title[0].split()]

                if len(raw_title) > 3 and title[-1] in page_end and raw_title[0] in raw_p \
                        and raw_title[1] in raw_p and (raw_title[2] in raw_p or raw_title[2] in next_p):
                    # print(raw_title, "\n", raw_p, "\n", page_end, title[-1])
                    is_legislation = True
                    if len(legislation) != 0:
                        legislations.append((leg_title, legislation))
                    leg_title = remove_accent(title[1] + "_" + fname + "_" + pat_non_chars.sub(r'_', title[0])).lower()
                    legislation = []
                    after_signature = False
                    del titles[i]
                    break
            if pat_sign.search(p_cont) and not after_signature:
                after_signature = True
            if is_legislation and not after_signature:
                legislation.append(p_cont)
    legislations.append((leg_title, legislation))

    return legislations


def get_toc_and_cont(div_tags):
    pat_non_chars = re.compile(r'\W')
    pat_page_num = re.compile(r'\s(\d+)$', re.M)
    pat_page_end = re.compile(r'.{,30}közlöny.{,30}')

    divs_toc = []
    divs = []
    passed_tjegyzek = False
    first_page = None

    for div in div_tags:
        if first_page is None:
            pages = pat_page_num.search(div.text)
            if pages:
                first_page = pages.group(1)
                divs_toc.append(div.find_all('p'))
                continue

        raw_div = pat_non_chars.sub("", div.text).lower()

        if not passed_tjegyzek:
            page = "".join(pat_page_end.findall(raw_div))
            if first_page and first_page in page:
                passed_tjegyzek = True
                divs.append(div)
                continue
            divs_toc.append(div.find_all('p'))
        else:
            divs.append(div)

    return divs_toc, divs


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')
    dir = 'legislations'
    args = parser.parse_args()
    files = []

    if args.filepath:
        for p in args.filepath:
            poss_files = glob(p)
            poss_files = [os.path.abspath(x) for x in poss_files]

            files += poss_files
    else:
        files = glob(os.path.join(os.getcwd(), "*.html"))

    if args.directory:
        dir = os.path.abspath(args.directory)

    return {'dir': dir, 'files': files}


def process(inp):
    prefix_dict = {"határozat": "hat", "rendelet": "rnd", "törvény": "trv",
                   "végzés": "veg", "közlemény": "koz", "nyilatkozata": "nyil",
                   "utasítás": "ut", "állásfoglalás": "all", "hirdetmény": "hir",
                   "helyesbítés": "hely", "tájékoztató": "taj", "intézkedés": "int",
                   "parancs": "par", "pénzügyibeszámoló": "merl"}
    for f in inp:
        txt = f[1]
        soup = BeautifulSoup(txt, 'lxml')
        # extract table of contents and the content
        divs_toc, divs = get_toc_and_cont(soup.find_all('div'))
        p_parts_toc = [p.text for div in divs_toc for p in div]
        titles = extract_titles(p_parts_toc, prefix_dict)
		
        # print(f[0])
 
        # extract legislations
        legislations = extract_legislation(titles, f[0], divs)
        yield legislations


def main():

    args = get_args()
    inp = read(args['files'])
    outp = process(inp)
    write(outp, args['dir'])


if __name__ == "__main__":
    main()
