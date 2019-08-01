#! /usr/bin/env python3

import argparse
import os
import re
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
# from shutil import move


def read(files):
    for finp in files:
        with open(finp, encoding="utf-8") as f:
            fname = os.path.splitext(os.path.basename(finp))[0]
            yield (fname, f.read())


def write(outp, dir, ext):
    Path(dir).mkdir(parents=True, exist_ok=True)
    for legislations in outp:
        for legislation in legislations:
            with open(os.path.join(dir, legislation[0]+ext), "w", encoding="utf-8") as f:
                f.write(legislation[1])


def replace_latin1(text):
    return text.replace("õ", "ő").replace("û", "ű").replace("Õ", "Ő").replace("Û", "Ű")


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


def get_prefix(cat, title, prefix_dict):
    title_for_prefix = re.sub(r'\W', "", title).lower()
    mod = ""
    if "módosítás" in title_for_prefix:
        mod = "mod_"
    if cat in prefix_dict.keys():
        return mod + prefix_dict[cat]
    else:
        return ""


def get_cat(cats, title):
    title_for_cat = re.sub(r'\W', "", title).lower()
    first_cat = (len(title_for_cat)-1, "")

    for cat in cats:
        if cat in title_for_cat:
            start_let = title_for_cat.find(cat)
            if start_let < first_cat[0]:
                first_cat = (start_let, cat)

    return first_cat[1]


def extract_titles(toc, cats=None):
    pat_dots = re.compile(r'((\s+\.)+)|(\.{2,})')
    pat_split = re.compile(r'-\s+')
    pat_page_num = re.compile(r'\s(\d+)$')
    pat_trv = re.compile(r'(\d+[.:](?:\sévi)?)\s(\w+\.)\s(törvény)\s(\w+)')
    pat_rest_leg = re.compile(r'(\d+/\d+\.)\s(\((?:\w+\.?\s)+(?:\d+/)?\d+\.\))\s((?:\w+(?:–|-\w+)?)+\.?)\s(\w+\.?)')
    pat_wspaces = re.compile(r'\s+')

    abbr_dict = {"tv.": "törvény", " h.": " határozat", " r.": " rendelet", " ut.": " utasítás", " e.": " együttes"}
    titles = []
    title = ""
    main_title = None
    current_page = 0

    for cont in toc:
        for key in abbr_dict:
            if key in cont:
                cont = cont.replace(key, abbr_dict[key])
        raw_cont = pat_wspaces.sub(" ", cont).replace("tör vény", "törvény")
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
            cat = ""
            if cats:
                cat = get_cat(cats, title)
            title = pat_dots.sub("", title[title.find(cat):]).strip().split()
            if title:
                page_num = title[-1]
                second_title = pat_split.sub("", " ".join(title[1:-1]))
                titles.append((main_title.replace(":", ".").replace("évi", ""), cat, second_title, page_num))
            title = ""
            main_title = None

    return titles


def is_frag(text):
    stopwords = ["a", "az", "azt", "ez", "ezt", "így", "vagy", "és", "is", "nem", "fog", "több", "mint", "kell",
                 "ahol", "e", "ha", "csak", "erre", "arra", "úgy", "aki", "egy", "kettő", "négy", "öt", "hat",
                 "hét", "tíz", "van", "volt", "meg", "azon", "ezen", "való", "kb", "közé", "rész", "más", "áron", "cikk",
                 "ne"]
    pat_stop = re.compile(r'(\d+)|(\w+\))|(\W+)')
    words = text.lower().split()
    if len(words) < 10:
        return False
    few_char_words = 0
    for word in words:
        if not pat_stop.search(word) and word not in stopwords and len(word) <= 4:
            few_char_words += 1
        else:
            few_char_words = 0
        if few_char_words == 5:
            return True
    return False


def is_hun(langd_p_cont):
    try:
        lang = detect(langd_p_cont.lower())
    except LangDetectException:
        lang = "hu"
    if lang == "hu":
        return True
    return False


def find_leg(page_end, titles, raw_ps, pat_non_chars):
    for i, title in enumerate(titles):
        raw_title = [pat_non_chars.sub("", title_part).lower() for title_part in title[0].split()]
        start_main_title = raw_ps[raw_ps.find(raw_title[0]):]
        if len(raw_title) > 3 \
                and title[-1] in page_end and raw_title[0] in raw_ps \
                and raw_title[1] in raw_ps and raw_title[2] in raw_ps \
                and pat_non_chars.sub("", title[2][-20:]).lower() in start_main_title:
                return titles.pop(i)
    return None


def from_title(ps_cont, title):
    pat_space = re.compile(r'\s+')
    pat_type = re.compile(r'(k *ö *z *l *e *m *é *n *y( *e)?)|'
                          r'(i *n *t *é *z *k *e *d *é *s( *e)?)|'
                          r'(u *t *a *s *í *t *á *s( *a)?)|'
                          r'(p *a *r *a *n *c *s( *a)?)|'
                          r'(t *ö *r *v *é *n *y( *e)?)|'
                          r'(h *a *t *á *r *o *z *a *t( *a)?)|'
                          r'(r *e *n *d *e *l *e *t( *e)?)')

    title_parts = title[0].split()
    start_title = "{} {} {}".format(title_parts[0], title_parts[1], title_parts[2])
    main_title = pat_space.sub(" ", " ".join(ps_cont[-10:]).replace("tör vény", "törvény").replace("évi", ""))
    start = main_title.find(start_title)
    if start == -1:
        return None
    begin = main_title[start:]
    leg_type = pat_type.search(begin)
    leg_type_wo_space = title[1]
    if leg_type:
        leg_type_wo_space = leg_type.group().replace(" ", "")
        begin = begin.replace(leg_type.group(), leg_type_wo_space)
    begin = re.sub(leg_type_wo_space, leg_type_wo_space + "###", begin + ".", count=1)
    return begin


def extract_legislation(titles, prefix_dict, fname, bs_divs, found_legs):
    pat_header = re.compile(r'(közlöny(?:\d+évi)?\d+szám)|(\d+szám\w+?közlöny)')
    pat_page_end = re.compile(r'.{,40}közlöny.{,40}')
    pat_non_chars = re.compile(r'\W')
    pat_space = re.compile(r'\s+')
    pat_sign = re.compile(r's\.\s+k\.,?')
    pat_split = re.compile(r'(\w+)-\s*$', re.M)

    ps_cont = []
    ps_cont_check = []
    raw_ps = []
    legislation = []
    legislations = []
    is_legislation = False
    after_signature = False
    leg_title = ""
    leg_name = ""
    frag = False

    for div in bs_divs:
        page_end = "".join(pat_page_end.findall(pat_non_chars.sub("", div.text.lower())))
        for p in div.find_all('p'):
            p_cont = pat_split.sub(r'\1###', p.text)
            p_cont = p_cont.strip()
            raw_p = pat_non_chars.sub("", p_cont.lower())
            if p_cont == "" or pat_header.search(raw_p):
                continue
            ps_cont.append(p_cont)
            ps_cont_check.append(p_cont)
            raw_ps.append(raw_p)
            title = find_leg(page_end, titles, "".join(raw_ps[-10:]), pat_non_chars)
            if title:
                if len(legislation) != 0 and leg_title and leg_title[0] != "_" and not frag \
                        and after_signature and legislation[0] is not None and leg_name not in found_legs:
                    legislations.append((leg_title, replace_latin1("\n".join(legislation))))
                    found_legs.append(leg_name)

                # legislation = [re.sub(title[1]+r'(\w+)?', title[1]+"###\n", title[0]+" "+title[2]+".", count=1)]
                legislation = [from_title(ps_cont, title)]
                leg_name = pat_non_chars.sub("", " ".join(title[0].split()[:-1]))
                leg_title = remove_accent((get_prefix(title[1], title[0]+title[2], prefix_dict)
                                          + "_" + fname + "_" + leg_name).lower())
                ps_cont = []
                ps_cont_check = []
                raw_ps = []
                is_legislation = True
                after_signature = False
                frag = False

            elif is_legislation and not after_signature and not frag \
                    and legislation[0] is not None and leg_name not in found_legs:
                if "###" in ps_cont_check[-1]:
                    continue
                ps_cont_check_str = pat_space.sub(" ", " ".join(ps_cont_check))
                if pat_sign.search(ps_cont_check_str):
                    after_signature = True
                    legislation.append(ps_cont_check_str.replace("### ", ""))
                    ps_cont = []
                    ps_cont_check = []
                    raw_ps = []
                elif len(ps_cont_check_str.split()) >= 8:
                    hun = is_hun(ps_cont_check_str)
                    if hun:
                        legislation.append(ps_cont_check_str.replace("### ", ""))
                        frag = is_frag(ps_cont_check_str)
                        # if frag:
                        #     with open("0frag_"+fname, "a", encoding="utf-8") as f:
                        #         print("#######\n", fname, "\n", ps_cont_check_str, "\n\n", file=f)
                    ps_cont_check = []
                    # raw_ps = []

    if leg_title and leg_title[0] != "_" and not frag \
            and after_signature and legislation[0] is not None and leg_name not in found_legs:
        legislations.append((leg_title, replace_latin1("\n".join(legislation))))
        found_legs.append(leg_title)
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
    basp = 'legislations'
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
        basp = os.path.abspath(args.directory)

    return {'dir': basp, 'files': files}


def process(inp):
    cats = ["határozat", "rendelet", "törvény", "végzés", "közlemény", "nyilatkozata",
            "utasítás", "állásfoglalás", "helyesbítés", "tájékoztató", "intézkedés", "parancs"]

    prefix_dict = {"határozat": "hat", "rendelet": "rnd", "törvény": "trv",
                   "végzés": "veg", "közlemény": "koz", "nyilatkozata": "nyil",
                   "utasítás": "ut", "állásfoglalás": "all","helyesbítés": "hely",
                   "tájékoztató": "taj", "intézkedés": "int", "parancs": "par"}
    found_legs = []
    for f in inp:
        print(f[0])
        txt = f[1]
        soup = BeautifulSoup(txt, 'lxml')
        # extract table of contents and the content
        divs_toc, divs = get_toc_and_cont(soup.find_all('div'))
        p_parts_toc = [p.text for div in divs_toc for p in div]
        titles = extract_titles(p_parts_toc, cats)
        # for title in titles:
        #     print(title)

        # extract legislations
        legislations = extract_legislation(titles, prefix_dict, f[0], divs, found_legs)
        yield legislations


def main():
    args = get_args()
    inp = read(args['files'])
    outp = process(inp)
    write(outp, args['dir'], ".txt")


if __name__ == "__main__":
    main()
