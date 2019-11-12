#! /usr/bin/env python3

import argparse
import os
import re
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from time import gmtime, strftime
# from shutil import move

pat_wspace = re.compile(r'(\s+)')

# regex to find text part which possibly contains the page number and also to find the header of a page)

pat_header = re.compile(r'\d+\.szám[^#]{,30}?(\d+)(?:$|###)|'
                        r'(\d+)[^#]{,30}?\d+\.szám(?:$|###)|'
                        r'\d+\.szám(\d+)(?:$|###)', re.I)

pat_header_wo_pg = re.compile(r'.{,20}?\.szám\w+?(?:értesítő|közlöny|figyelő|tára|határozatai)|'
                              r'\w+?(?:értesítő|közlöny|figyelő|tára|határozatai).{,20}?\.szám', re.I)
# pat_header_wo_pg = re.compile(r'.{,10}?\d+\.szám\w+?(?:értesítő|közlöny|figyelő|tára|határozatai)|'
#                               r'\w+?(?:értesítő|közlöny|figyelő|tára|határozatai).{,10}?\d+\.szám', re.I)

# regex to found non word chars
pat_non_chars = re.compile(r'\W')

# regex to find first page number of the content in the table of content
pat_page_num = re.compile(r'[^0-9:]\s+(\d+)\s*$')
# pat_page_num = re.compile(r'[^0-9:]\s+(\d+)$')


def read(files):
    """
    Generator function.

    :param files: list of filepaths
    :yield: file name and text in tuple
    """

    for finp in files:
        with open(finp, encoding="utf-8") as f:
            fname = os.path.splitext(os.path.basename(finp))[0]
            yield (fname, f.read())


def write(outp, dir, ext):
    """
    :param outp: generator with legislations from an issue
    :param dir: path to write files
    :param ext: extension of the files to write
    """
    os.makedirs(dir, exist_ok=True)
    # Path(dir).mkdir(parents=True, exist_ok=True)
    for legislations in outp:
        for legislation in legislations:
            with open(os.path.join(dir, legislation[0]+ext), "w", encoding="utf-8", newline="\n") as f:
                f.write(legislation[1])


def replace_latin1(text):
    return text.replace("õ", "ő").replace("û", "ű").replace("Õ", "Ő").replace("Û", "Ű")


def remove_accent(s):
    """
    Replacing accented chars to non accented chars in a string:
    öüóőúéáűí -> ouooueaui

    :param s: string
    :return: string without accented chars
    """
    accent_dict = {"á": "a", "ü": "u", "ó": "o", "ö": "o", "ő": "o", "ú": "u", "é": "e", "ű": "u", "í": "i"}

    for key in accent_dict:
        if key in s:
            s = s.replace(key, accent_dict[key])
    return s


def get_cat(cats, title):
    """
    Finds the category of a legislation by the title.

    :param cats: list of categories to find in titles
    :param title: the title itself to find the legislation category by
    :return: category of the legislation
    """
    # replacing non word chars to empty string
    title_for_cat = pat_non_chars.sub("", title).lower()

    # creating tuple which contains the index of the beggining of a category (to find first occuring category in
    # the title) and the found category itself
    first_cat = (len(title_for_cat)-1, "")

    for cat in cats:
        start_index = title_for_cat.find(cat)
        if start_index != -1 and start_index < first_cat[0]:
            if cat == "alapítóokirat":
                cat = "Alapító Okirat"
            # if the index of the current category is lower then the last then cat=current category
            first_cat = (start_index, cat)

    return first_cat[1]


def get_prefix(cat, title, prefix_dict):
    """
    Getting the prefix of filename by category of the legislation. If "módosítás" is in the title, then
    the prefix will be "mod"_+cat, else it will be just the abbreviation of the category.

    :param cat: the category of the legislation
    :param title: the title of the legislation
    :param prefix_dict: dictonary with prefixes to find
    :return: prefix for the output filename
    """

    # replacing non word chars to empty string
    title_for_prefix = pat_non_chars.sub("", title).lower()
    mod = ""
    if "módosítás" in title_for_prefix:
        mod = "mod_"
    if cat in prefix_dict.keys():
        return mod + prefix_dict[cat]
    else:
        return ""


def extract_titles(toc, cats=None):
    """
    Extract the titles from table of contents.

    :param toc: table of contents to extract titles from
    :param cats: list of categories to sort title by
    :return: list of titles
    """

    # regex to find extra dots in the title
    pat_dots = re.compile(r'((\s+[-.])+)|([-.]{2,})|([-.]+ *$)')
    # backup pat_dots = re.compile(r'((\s+\.)+)|(\.{2,})|(\.+ *$)')
    pat_split = re.compile(r'-\s+')
    # regex to find laws
    pat_trv = re.compile(r'(\d+[.:])\s+(\w+\.)\s+(törvény)\s+(\w+)')
    # regex to find all the other legislations than laws
    pat_rest_leg = re.compile(r'(\d+/\w/\d+\.|(?:\d+/\d+\.)\s(?:\((?:\w+\.?\s)+(?:\d+/)?\d+\.\)))'
                              r'\s((?:\w+(?:–|-\w+)?)+\.?)\s(\w+\.?)')


    # abbrievation dict to restore original forms
    abbr_dict = {"tv.": "törvény", " h.": " határozat", " r.": " rendelet", " ut.": " utasítás", " e.": " együttes",
                 " közl.": "közlemény", " v.": " végzés"}
    titles = []
    title = ""
    main_title = None
    current_page = 0

    for cont in toc:
        # replacing specified abbrievations to its original form
        for key in abbr_dict:
            if key in cont:
                cont = cont.replace(key, abbr_dict[key])
        # print("\n###cont:", cont)
        # replacing multiple spaces and sometimes splitted "tör vény" to "törvény"
        raw_cont = pat_wspace.sub(" ", cont.replace("-\n", ""))
        title += raw_cont

        if main_title is None:
            # if there was no legislations found yet, then try it again in current parts of title
            main_title = pat_rest_leg.search(title)
            if not main_title:
                main_title = pat_trv.search(title.replace("évi ", ""))
            if main_title:
                # if a title was found the title will be the text from the index of found title in the gathered text
                title = title[main_title.start():]
                main_title = "{} {} {}".format(main_title.group(1), main_title.group(2), main_title.group(3))
            # print("\n###title:", title)

        page = pat_page_num.search(cont)
        if page and current_page <= int(page.group(1)):
            # print("##\n", title)
            current_page = int(page.group(1))
            cat = ""
            # determin the category of the legislation
            if cats:
                cat = get_cat(cats, title)
            # separate title from main title
            title_parts = pat_dots.sub("", title[title.find(cat):]).strip().split()

            if title_parts:
                # print(main_title)
                page_num = title_parts[-1]
                if main_title:
                    second_title = pat_dots.sub("", pat_split.sub("", " ".join(title_parts[1:-1])))
                else:
                    second_title = ""
                    # if no title found by regex, then the title will be the current line's first words
                    main_title = pat_dots.sub("", pat_split.sub("", " ".join(title.split()[:-1])))
                titles.append((main_title.replace(":", "."), cat, second_title, page_num))
            title = ""
            main_title = None

    return titles


def is_frag(text):
    """
    Determin wether the given text is fragmented or not.

    :param text: the text to analyze
    :return: if the text is fragmented
    """

    # TODO: should use a better stopwords list and may get it as param
    # stopwords which won't be count while counting the words less then 5 chars in a raw
    stopwords = ["az", "azt", "ez", "ezt", "így", "vagy", "és", "is", "nem", "fog", "több", "mint", "kell",
                 "ahol", "e", "ha", "csak", "erre", "arra", "úgy", "aki", "egy", "kettő", "négy", "öt", "hat", "hét",
                 "tíz", "van", "volt", "meg", "azon", "ezen", "való", "kb", "közé", "rész", "más", "áron", "cikk", "ne"]

    # regex to find parts that don't count while counting the less then 5 chars words
    pat_stop = re.compile(r'(\d+)|(\w+\))|(\W+)')
    words = text.lower().split()
    # passing back texts smaller than 10 words
    if len(words) < 10:
        return False
    few_char_words = 0
    for word in words:
        if not pat_stop.search(word) and word not in stopwords and 4 >= len(word) > 1:
            few_char_words += 1
        else:
            few_char_words = 0
        if few_char_words == 5:
            # if the program finds 5 words which contain less then 5 chars in a raw, then return True
            return True
    return False


def is_hun(langd_p_cont):
    """
    Determin if a given text is not hungarian.

    :param langd_p_cont: the text to be analyzed
    :return: if the text is hungarian -->True, else -->False
    """

    try:
        lang = detect(langd_p_cont.lower())
    except LangDetectException:
        lang = "hu"
    if lang == "hu":
        return True
    return False


def find_leg(page_num, titles, raw_ps, next_page):
    """
    Searching for title in given text with the title list extracted from the table of contents.

    :param page_num: current page number
    :param titles: list of legislation titles
    :param raw_ps: text to be analyzed without special characters
    :param next_page: beggining page number of the next legislation
    :return: is a tuple: a legislation title what was found, exact match of second title or not, next leg page number
    """
    for i, title in enumerate(titles):

        # splitting and replacing non word characters to "" in main title
        raw_main_title = [title_part.lower().replace(" ", "") for title_part in title[0].split()]
        # cutting the extra text from raw_ps so it will start from the main title
        raw_ps = raw_ps.replace("évi", "")
        start_main_title = raw_ps.find("".join(raw_main_title[0:len(raw_main_title)-1]))
        from_main_title = raw_ps[start_main_title:]
        leg_type = title[1].lower().replace(" ", "")

        # if the main title have at :least 4 elements and the first 3 is in the raw text
        # then it should be the beggining of a legislation

        if title[-1] == page_num and start_main_title != -1 and leg_type in from_main_title:
            # print("####\n", raw_main_title)
            # print("from:", from_main_title)
            # print("rawps:", re.sub(r'\s', "", raw_ps))
            if title[2] != "":
                try:
                    next_page = titles[i+1][-1]
                except IndexError:
                    next_page = 0
                from_subtitle = pat_non_chars.sub("", from_main_title[len("".join(raw_main_title)):])
                raw_subtitle = pat_non_chars.sub("", title[2].replace("évi", "",).lower())
                if raw_subtitle[1:] in from_subtitle:
                    return titles.pop(i), True, next_page
                elif len(from_subtitle) >= len(raw_subtitle):
                    return titles.pop(i), False, next_page
            else:
                return titles.pop(i), False, next_page
    return None, 0, next_page


def from_title(ps_cont, title, exact_match):
    """
    Finds the begin of a title in the given content and also replace it with title+"###"+second title+"."
    to annotate main title and separete from second title and prepare it to be analyzed by the emtsv_to_conll_with_ud.py.

    :param ps_cont: content to find the title in
    :param title: title to find
    :param exact_match: if the exaxt second title was found or not
    :return: text starting from the main title
    """

    # regex to find broken legislation types
    pat_type = re.compile(r'(k *ö *z *l *e *m *é *n *y( *e)?\b)|'
                          r'(i *n *t *é *z *k *e *d *é *s( *e)?\b)|'
                          r'(á *l *l *á *s *f *o *g *l *a *l *á* s( *a)?\b)|'
                          r'(u *t *a *s *í *t *á *s( *a)?)\b|'
                          r'(p *a *r *a *n *c *s( *a)?)\b|'
                          r'(t *ö *r *v *é *n *y( *e)?)\b|'
                          r'(h *a *t *á *r *o *z *a *t( *a)?)\b|'
                          r'(r *e *n *d *e *l *e *t( *e)?)\b|'
                          r'(v *é *g *z *é *s( *e)?)\b')
    title_parts = title[0].split()
    # print(title_parts) # 1
    if len(title_parts) < 3:
        return None
    start_title = "{} {} {}".format(title_parts[0], title_parts[1], title_parts[2])
    # must replacing "évi" to "" in the text, because its not part of the toc title but it can be part of the text
    main_title = pat_wspace.sub(" ", ps_cont.replace("évi", ""))
    start = main_title.find(start_title)
    # print("######\nmain:", main_title, "\nstart:", start_title) # 2
    if start == -1:
        return None
    # finding the beginning of the legislation title
    begin = main_title[start:]
    leg_type = pat_type.search(begin)
    leg_type_wo_space = title[1]
    # replacing the potentially broken legislation tipe to nonbroken form
    if leg_type:
        temp_leg_type_wo_space = leg_type.group().replace(" ", "")
        if leg_type_wo_space in temp_leg_type_wo_space:
            leg_type_wo_space = temp_leg_type_wo_space
        begin = begin.replace(leg_type.group(), leg_type_wo_space)
    # replacing legislation type to legislation type + "###" and put "." to the end of the whole title
    if exact_match:
        begin = begin + "."
    else:
        begin = re.sub(leg_type_wo_space, leg_type_wo_space + "###.", begin, count=1)
    # print("\n####", re.sub(r'###[.](\w+ *)?', ". ", begin)) # 3
    return re.sub(r'###[.](\w+ *)?', ". ", begin)


def is_needed(legislation, leg_title, frag, after_signature, leg_name, found_legs, strict=True):
    """
    Keeps the legislation if:
        1, it's not broken,
        2, it has a signature in the end
        3, it has got a type of legislations
        4, it has a proper title described by regex
        5, it's not found yet
    """
    # print(leg_title)

    if len(legislation) != 0 and not frag and after_signature and legislation[0] is not None and\
            leg_name not in found_legs and not re.match(r'mod', leg_title):
        # print("almost accepted:", leg_name)
        if not strict:
            return True
        elif leg_title and "kuria" not in leg_title and \
                re.match(r'hat|rnd|trv', leg_title) and not re.search(r'(ovb|ab|ke|me)$', leg_title):
            return True
    # print("refused:", leg_name)
    return False


def extract_legislation(titles, prefix_dict, fname, bs_divs, found_legs):
    # TODO: found_legs should rather be a dictionary
    """
    Finds and separates legislations in a közlöny.
    Keeps the legislation if:
        see is_needed documentation

    Only the hungarian parts of a legislation is kept.

    :param titles: extracted titles from toc
    :param prefix_dict: possible prefixes to give to the output fname
    :param fname: input fname
    :param bs_divs: texts in div tags found by bs4
    :param found_legs: list of the title of already found legislations avoiding find a legisaltion twice
    :return: a list of tuples. one tuple contains a legislation title and its content
    """

    # regex to find signature which implies the end of the legislation
    pat_sign = re.compile(r's\.\s+k\.,?')
    # list of p tag contents
    # list of p tag contents without whitespaces
    ps_cont = []
    raw_ps = []
    leg = []
    legs = []

    is_leg = after_sign = frag = False
    leg_title = leg_name = ""
    next_page = "-1"

    for div in bs_divs:
        # put text parts in list which can have the page number in it
        header = pat_header.search(pat_wspace.sub("", div.text.replace("\n", "###")))
        if header:
            page_num = header.group(1) or header.group(2) or header.group(3) or "-1"
            # print("\n######", header, page_num)

        if after_sign and int(page_num) < int(next_page):
            continue
            # print(page_num, next_page)
            # print(page_num)

        for p in div.find_all('p'):
            # print(header)
            p_cont = p.text.strip()
            raw_p = pat_wspace.sub("", p_cont.lower())
            # if the content is empty string or it's a header -->skip
            if p_cont == "" or pat_header.search(raw_p):
                continue
            # print("\n####",p.text)
            ps_cont.append(p_cont)
            raw_ps.append(raw_p)
            title, exact_match, next_page = find_leg(page_num, titles, "".join(raw_ps[-10:]), next_page)
            if title:
                # saving the beggining of the legislation
                text_from_title = from_title(" ".join(ps_cont[-10:]), title, exact_match)
                leg = [text_from_title]
                # print("\n###", legislation, title) #4
                # determining its name and title
                if title[2] != "":
                    leg_name = pat_non_chars.sub("", " ".join(title[0].split()[:-1]))
                    leg_title = ""
                else:
                    leg_name = pat_non_chars.sub("", title[0][-20:])
                    leg_title = "0"
                leg_title += remove_accent((get_prefix(title[1], title[0]+title[2], prefix_dict)
                                            + "_" + fname + "_" + leg_name).lower())
                is_leg = True
                after_sign = False
                frag = is_frag(text_from_title) if text_from_title is not None else False
                ps_cont = []
                raw_ps = []

            elif is_leg and not after_sign and not frag and leg[0] is not None and leg_name not in found_legs:
                # if there is a split word in the last portion of text, then skip
                ps_cont_str = " ".join(ps_cont).replace("  ", " ")
                # searching for signature
                if pat_sign.search(ps_cont_str):
                    after_sign = True
                    leg.append(ps_cont_str)

                    if is_needed(leg, leg_title, frag, after_sign, leg_name, found_legs, False):
                        legs.append((leg_title, "\n".join(leg)))
                        found_legs.append(leg_name)
                    if len(titles) == 0:
                        return legs
                    ps_cont = []
                    raw_ps = []

                # if signature was not found, then check if its hungarian and if it's fragmented
                elif len(ps_cont_str.split()) >= 8:
                    hun = is_hun(ps_cont_str)
                    if hun:
                        leg.append(ps_cont_str)
                        frag = is_frag(ps_cont_str)
                    ps_cont = []

    return legs


def get_toc_and_cont(div_tags):
    """
    Separates the table of content and the content from each other.

    :param div_tags: texts in div tags found by bs4
    :return: table of content and the content
    """
    div_count = 0
    divs_toc = []
    divs = []
    passed_tjegyzek = False
    first_page = None

    for div in div_tags:
        div_count += 1

        if first_page is None:
            if div_count == 3:
                return None, None
            for p in div.find_all('p'):
                # searching for the firs page number of the content
                pages = pat_page_num.search(p.text)

                if not pat_header_wo_pg.search(pat_wspace.sub("", p.text)) and pages:
                    first_page = pages.group(1)
                    divs_toc.append(div.find_all('p'))
                    # print("\n\np:####", p)
                    break
            continue

        raw_div = pat_wspace.sub("", div.text.replace("\n", "###"))

        if not passed_tjegyzek:
            page = pat_header.search(raw_div)
            if page:
                page = page.group(1) or page.group(2) or page.group(3) or "-1"
                if page != -1 and first_page and int(first_page) <= int(page):
                    # if the number of the first page is found, it's end of the toc
                    # so append div to the list of contents
                    passed_tjegyzek = True
                    divs.append(div)
                    continue
            # if toc is not over then append div to the list of table of contents
            divs_toc.append(div.find_all('p'))
        else:

            divs.append(div)

    return divs_toc, divs


def get_args():
    """
    Getting argumentums from terminal.

    :return: dictionary wich contains the path of output folder and the input folder(s)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')
    parser.add_argument('-s', '--strict', help='To extract only enactment type documents, default is true')
    # the default folder where the output files will be written.
    basp = 'text2law_output_'  + strftime("%Y-%m-%d_%H%M%S", gmtime())
    args = parser.parse_args()
    # list of filepathes that will be read
    files = []

    if args.filepath:
        # saving the locacion(s) of input files
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
    """

    :param inp:
    :return:
    """
    cats = ["határozat", "rendelet", "törvény", "végzés", "közlemény", "nyilatkozat", "mérleg",
            "utasítás", "állásfoglalás", "helyesbítés", "tájékoztató", "intézkedés", "parancs",
            "alapítóokirat"]

    prefix_dict = {"határozat": "hat", "rendelet": "rnd", "törvény": "trv", "végzés": "veg",
                   "közlemény": "koz", "nyilatkozat": "nyil", "utasítás": "ut", "mérleg":"merl",
                   "állásfoglalás": "all","helyesbítés": "hely", "tájékoztató": "taj",
                   "Alapító Okirat": "ao", "intézkedés": "int", "parancs": "par"}

    # regex to find split words in the end of a line
    pat_split = re.compile(r'(\w+)-\s*?[\n]')
    found_legs = []
    for fl in inp:
        print(fl[0])
        txt = pat_split.sub(r'\1', replace_latin1(fl[1]).replace("*", "")
                            .replace("•", "").replace("tör vény", "törvény"))
        # soup = BeautifulSoup(txt, 'lxml')
        soup = BeautifulSoup(txt, "html.parser")
        # extract table of contents and the content
        divs_toc, divs = get_toc_and_cont(soup.find_all('div'))
        if divs_toc is None or divs is None:
            with open("withouttoc.txt", "a", encoding="utf-8") as f:
                f.write(fl[0] + "\n")
            continue
        p_parts_toc = [p.text for div in divs_toc for p in div]
        titles = extract_titles(p_parts_toc, cats)
        # print(p_parts_toc)

        # for checking titles
        # for title in titles:
        #     print(title)
        # print(divs[:5])

        # extract legislations
        legislations = extract_legislation(titles, prefix_dict, fl[0], divs, found_legs)
        if legislations:
            yield legislations


def main():
    args = get_args()
    inp = read(args['files'])
    outp = process(inp)
    write(outp, args['dir'], ".txt")


if __name__ == "__main__":
    main()

