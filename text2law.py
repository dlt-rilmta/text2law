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
    Path(dir).mkdir(parents=True, exist_ok=True)
    for legislations in outp:
        for legislation in legislations:
            with open(os.path.join(dir, legislation[0]+ext), "w", encoding="utf-8") as f:
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
    title_for_cat = re.sub(r'\W', "", title).lower()
    # creating tuple which contains the index of the beggining of a category (to find first occuring category in
    # the title) and the found category itself
    first_cat = (len(title_for_cat)-1, "")

    for cat in cats:
        if cat in title_for_cat:
            start_index = title_for_cat.find(cat)
            if start_index < first_cat[0]:
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
    title_for_prefix = re.sub(r'\W', "", title).lower()
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
    pat_dots = re.compile(r'((\s+\.)+)|(\.{2,})')
    #
    pat_split = re.compile(r'-\s+')
    # regex to find page number for titles
    pat_page_num = re.compile(r'\s(\d+)$')
    # regex to find laws
    pat_trv = re.compile(r'(\d+[.:](?:\sévi)?)\s(\w+\.)\s(törvény)\s(\w+)')
    # regex to find all the other legislations than laws
    pat_rest_leg = re.compile(r'(\d+/\d+\.)\s(\((?:\w+\.?\s)+(?:\d+/)?\d+\.\))\s((?:\w+(?:–|-\w+)?)+\.?)\s(\w+\.?)')
    # regex to find multiple whitespaces
    pat_wspaces = re.compile(r'\s+')

    # abbrievation dict to restore original forms
    abbr_dict = {"tv.": "törvény", " h.": " határozat", " r.": " rendelet", " ut.": " utasítás", " e.": " együttes"}
    titles = []
    title = ""
    main_title = None
    current_page = 0

    for cont in toc:
        # replacing specified abbrievations to its original form
        for key in abbr_dict:
            if key in cont:
                cont = cont.replace(key, abbr_dict[key])
        # replacing multiple spaces and sometimes splitted "tör vény" to "törvény"
        raw_cont = pat_wspaces.sub(" ", cont).replace("tör vény", "törvény")
        title += raw_cont
        if main_title is None:
            # if there was no legislations found yet, then try it again in current parts of title
            main_title = pat_rest_leg.search(title)
            if main_title is None:
                main_title = pat_trv.search(title)
            if main_title:
                # if a title was found the title will be the text from the index of found title in the gathered text
                title = title[main_title.start():]
                main_title = "{} {} {} {}"\
                    .format(main_title.group(1), main_title.group(2), main_title.group(3), main_title.group(4))

        page = pat_page_num.search(cont)
        if page and current_page <= int(page.group(1)):
            current_page = int(page.group(1))
            if main_title is None:
                # if no title found by regex, then the title will be the current line's first for words
                main_title = " ".join(raw_cont.strip().split()[0:4])
            cat = ""
            # determin the category of the legislation
            if cats:
                cat = get_cat(cats, title)
            # separate title from main title
            title = pat_dots.sub("", title[title.find(cat):]).strip().split()
            if title:
                page_num = title[-1]
                second_title = pat_split.sub("", " ".join(title[1:-1]))
                titles.append((main_title.replace(":", ".").replace("évi", ""), cat, second_title, page_num))
            title = ""
            main_title = None

    return titles


def is_frag(text):
    """
    Determin wether the given text is fragmented or not.

    :param text: the text to analyze
    :return: if the text is fragmented -->True else -->False
    """

    # TODO: should use a better stopwords list and may get it as param
    # stopwords which won't be count while counting the words less then 5 chars in a raw
    stopwords = ["a", "az", "azt", "ez", "ezt", "így", "vagy", "és", "is", "nem", "fog", "több", "mint", "kell",
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
        if not pat_stop.search(word) and word not in stopwords and len(word) <= 4:
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


def find_leg(page_end, titles, raw_ps, pat_non_chars=re.compile(r'\W')):
    """
    Searching for title in given text with the title list extracted from the table of contents.

    :param page_end: list of texts which can contain the page number
    :param titles: list of legislation titles
    :param raw_ps: text to be analyzed without special characters
    :param pat_non_chars: regex pattern to found special characters
    :return: a legislation title what was found
    """

    for i, title in enumerate(titles):

        # splitting and replacing non word characters to "" in main title
        raw_title = [pat_non_chars.sub("", title_part).lower() for title_part in title[0].split()]
        # cutting the extra text from raw_ps so it will start from the main title
        start_main_title = raw_ps[raw_ps.find(raw_title[0]):]
        if len(raw_title) > 3 \
           and title[-1] in page_end and raw_title[0] in raw_ps \
           and raw_title[1] in raw_ps and raw_title[2] in raw_ps \
           and pat_non_chars.sub("", title[2][-20:]).lower() in start_main_title:
                # if the main title have at least 4 elements and the first 3 is in the raw text and the last 20 chars
                # of second title is in the raw text, then it should be the beggining of a legislation
                # so return the title and also delete it from the list
                return titles.pop(i)
    return None


def from_title(ps_cont, title):
    """
    Finds the begin of a title in the given content and also replace it with title+"###"+second title+"."
    to annotate main title and separete from second title and prepare it to be analyzed by the emtsv_to_conll_with_ud.py.

    :param ps_cont: content to find the title in
    :param title: title to find
    :return: text starting from the main title
    """

    pat_space = re.compile(r'\s+')
    # regex to find broken legislation types
    pat_type = re.compile(r'(k *ö *z *l *e *m *é *n *y( *e)?\b)|'
                          r'(i *n *t *é *z *k *e *d *é *s( *e)?\b)|'
                          r'(u *t *a *s *í *t *á *s( *a)?)\b|'
                          r'(p *a *r *a *n *c *s( *a)?)\b|'
                          r'(t *ö *r *v *é *n *y( *e)?)\b|'
                          r'(h *a *t *á *r *o *z *a *t( *a)?)\b|'
                          r'(r *e *n *d *e *l *e *t( *e)?\b)')
    title_parts = title[0].split()
    start_title = "{} {} {}".format(title_parts[0], title_parts[1], title_parts[2])
    # must replacing "évi" to "" in the text, because its not part of the toc title but it can be part of the text
    main_title = pat_space.sub(" ", " ".join(ps_cont[-10:]).replace("tör vény", "törvény").replace("évi", ""))
    start = main_title.find(start_title)
    if start == -1:
        return None
    # finding the beginning of the legislation title
    begin = main_title[start:]
    leg_type = pat_type.search(begin)
    leg_type_wo_space = title[1]
    # replacing the potentially broken legislation tipe to nonbroken form
    if leg_type:
        leg_type_wo_space = leg_type.group().replace(" ", "")
        begin = begin.replace(leg_type.group(), leg_type_wo_space)
    # replacing legislation type to legislation type + "###" and put "." to the end of the whole title
    begin = re.sub(leg_type_wo_space, leg_type_wo_space + "###", begin + ".", count=1)
    return begin


def is_needed(legislation, leg_title, frag, after_signature, leg_name, legislations, found_legs):
    """
    Keeps the legislation if:
        1, it's not broken,
        2, it has a signature in the end
        3, it has got a type of legislations
        4, it has a proper title described by regex
        5, it's not found yet
    """

    if len(legislation) != 0 and leg_title and not re.match(r'_|int|all|koz|mod|par|ut|veg', leg_title) \
            and not re.search(r'ovb$|ab$|ke$', leg_title) and "kuria" not in leg_title and \
            not frag and after_signature and legislation[0] is not None and leg_name not in found_legs:
        legislations.append((leg_title, replace_latin1("\n".join(legislation))))
        found_legs.append(leg_name)


def extract_legislation(titles, prefix_dict, fname, bs_divs, found_legs):
    # TODO: found_legs should rather be a dictionary
    # TODO: iam not sure that ps_cont_check is needed, it could be replaced with ps_cont only
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

    # regex to find the header of a page
    pat_header = re.compile(r'(közlöny(?:\d+évi)?\d+szám)|(\d+szám\w+?közlöny)')
    # regex to find text part which possibly contains the page number
    pat_page_end = re.compile(r'.{,40}közlöny.{,40}')
    # regex to found non word chars
    pat_non_chars = re.compile(r'\W')
    pat_space = re.compile(r'\s+')
    # regex to find signature which implies the end of the legislation
    pat_sign = re.compile(r's\.\s+k\.,?')
    # regex to find split words in the end of a line
    pat_split = re.compile(r'(\w+)-\s*$', re.M)

    # list of p tag contents
    ps_cont = []
    ps_cont_check = []
    # list of p tag contents without special chars
    raw_ps = []
    legislation = []
    legislations = []
    is_legislation = False
    after_signature = False
    frag = False
    leg_title = ""
    leg_name = ""

    for div in bs_divs:
        # put text parts in list which can have the page number in it
        page_end = "".join(pat_page_end.findall(pat_non_chars.sub("", div.text.lower())))
        for p in div.find_all('p'):
            # if there is a word split in the end of the text, marks it with "###"
            p_cont = pat_split.sub(r'\1###', p.text)
            p_cont = p_cont.strip()
            raw_p = pat_non_chars.sub("", p_cont.lower())
            # if the content is empty string or it's a header -->skip
            if p_cont == "" or pat_header.search(raw_p):
                continue
            ps_cont.append(p_cont)
            ps_cont_check.append(p_cont)
            raw_ps.append(raw_p)
            title = find_leg(page_end, titles, "".join(raw_ps[-10:]), pat_non_chars)
            if title:
                # if a title found in the text and its not the first one and it has a type and it's not fragmented
                # and it has a signature and it has a title and also it's not found yet, then save it
                is_needed(legislation, leg_title, frag, after_signature, leg_name, legislations, found_legs)

                # # legislation = [re.sub(title[1]+r'(\w+)?', title[1]+"###\n", title[0]+" "+title[2]+".", count=1)]

                # saving the start of the legislation
                legislation = [from_title(ps_cont, title)]
                # determining its name and title
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

                # if there is a split word in the last portion of text, then skip
                if "###" in ps_cont_check[-1]:
                    continue
                ps_cont_check_str = pat_space.sub(" ", " ".join(ps_cont_check))
                # searching for signature
                if pat_sign.search(ps_cont_check_str):
                    after_signature = True
                    legislation.append(ps_cont_check_str.replace("### ", ""))
                    ps_cont = []
                    ps_cont_check = []
                    raw_ps = []
                # if didn't find, then check if its hungarian and if it's fragmented
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

    # appending the last legislation
    is_needed(legislation, leg_title, frag, after_signature, leg_name, legislations, found_legs)
    return legislations


def get_toc_and_cont(div_tags):
    """
    Separates the table of content and the content from each other.

    :param div_tags: texts in div tags found by bs4
    :return: table of content and the content
    """

    # regex to find non word chars
    pat_non_chars = re.compile(r'\W')
    # regex to find first page number of the content in the table of content
    pat_page_num = re.compile(r'\s(\d+)$', re.M)
    # regex to find texts which possibly contain page number
    pat_page_end = re.compile(r'.{,30}közlöny.{,30}')

    divs_toc = []
    divs = []
    passed_tjegyzek = False
    first_page = None

    for div in div_tags:
        if first_page is None:
            # searching for the firs page number of the content
            pages = pat_page_num.search(div.text)
            if pages:
                first_page = pages.group(1)
                # append all of div to the list of table of contents
                divs_toc.append(div.find_all('p'))
                continue

        raw_div = pat_non_chars.sub("", div.text).lower()

        if not passed_tjegyzek:
            page = "".join(pat_page_end.findall(raw_div))
            if first_page and first_page in page:
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
    # the default folder where the output files will be written.
    basp = 'legislations'
    args = parser.parse_args()
    # list of filepathes that will be read
    files = []

    if args.filepath:
        # save the locacion(s) of input files
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

        # for checking titles
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
