import argparse
import os
import re
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup


def read_file(finp):
    with open(finp, encoding="utf-8") as f:
        text = f.read()
        return text


def write_out(ls, finp, fname):
    Path(finp).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(finp, fname), "w", encoding="utf-8") as f:
        f.write("\n".join(ls))


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


def extract_titles(toc):
    prefix_dict = {"határozat": "hat", "rendelet": "rnd", "törvény": "trv",
                   "végzése": "veg", "közleménye": "koz", "nyilatkozata": "nyil"}

    abbr_dict = {"tv.": "törvény", " h.": " határozat", " r.": " rendelet"}

    pat_page_num = re.compile(r'\d+$')
    titles = []
    title = ""
    prefix = ""
    for cont in toc:
        for key in abbr_dict:
            if key in cont:
                cont = cont.replace(key, abbr_dict[key])
        title += cont.replace("\n", " ")
        raw_cont = cont.lower().replace(" ", "")
        if "tartalomjegyzék" in raw_cont or "magyarközlöny" in raw_cont:
            title = ""
            continue
        if pat_page_num.search(cont):
            title_for_prefix = title.replace(" ", "").lower()
            if "módosítás" in title_for_prefix:
                prefix = "mod"
            else:
                for key in prefix_dict:
                    if key in title_for_prefix:
                        prefix = prefix_dict[key]
                        break
            title = title.strip().split()
            page_num = title[-1]
            main_title = " ".join(title[0:4])
            full_title = " ".join(title[0:-1])
            titles.append((main_title, prefix, full_title, page_num))
            title = ""
            prefix = ""
    return titles


def extract_legislation(titles, bs_divs):
    pat_page_end = re.compile(r'.{,10}magyarközlöny.{,30}')
    pat_non_chars = re.compile(r'\W')
    legislation = []
    legislations = []
    is_legislation = False
    leg_title = ""

    for div in bs_divs:
        page_end = "".join(pat_page_end.findall(pat_non_chars.sub("", div.text.lower())))
        for p in div.find_all('p'):
            p = p.text.strip()
            if p == "":
                continue
            raw_p = pat_non_chars.sub("", p.lower())
            for i, title in enumerate(titles):
                raw_title = [pat_non_chars.sub("", title_part).lower() for title_part in title[0].split()]
                if title[-1] in page_end and raw_title[0] in raw_p \
                        and raw_title[1] in raw_p and raw_title[2] in raw_p:
                    is_legislation = True
                    if len(legislation) != 0:
                        legislations.append((leg_title, legislation))
                    leg_title = remove_accent(title[1]+"_"+pat_non_chars.sub(r'_', title[0])).lower()
                    legislation = []
                    del titles[i]
                    break
            if is_legislation:
                legislation.append(p)
    legislations.append((leg_title, legislation))
    return legislations


def get_args_inpfi_outfo(basp):
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="*")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')
    args = parser.parse_args()
    files = []
    if args.filepath:
        for p in args.filepath:
            poss_files = glob(p)
            new_files = [os.path.abspath(x) for x in poss_files]
            files += new_files
    else:
        files = glob(os.path.join(os.getcwd(), "*html"))

    if args.directory:
        basp = os.path.abspath(args.directory)
    return basp, files


def main():
    basp = 'legislations'
    basp, files = get_args_inpfi_outfo(basp)
    pat_non_chars = re.compile(r'\W')

    for finp in files:
        txt = read_file(finp)
        # extract conts in TOC in the if block and conts after TOC in the else block
        soup = BeautifulSoup(txt, 'lxml')
        divs_toc = []
        divs = []
        passed_tjegyzek = False
        passed_first_tjegyzek = False

        for div in soup.find_all('div'):
            raw_div = pat_non_chars.sub("", div.text).lower()
            if passed_first_tjegyzek and passed_tjegyzek:
                divs.append(div)
                continue
            if "tartalomjegyzék" in raw_div:
                divs_toc.append(div.find_all('p'))
                passed_first_tjegyzek = True
            elif "tartalomjegyzék" not in raw_div:
                passed_tjegyzek = True
                divs.append(div)

        p_parts_toc = [p.text for div in divs_toc for p in div]
        titles = extract_titles(p_parts_toc)

        # extract legislations
        legislations = extract_legislation(titles, divs)
        for legislation in legislations:
            write_out(legislation[1], basp, legislation[0]+".txt")


if __name__ == "__main__":
    main()
