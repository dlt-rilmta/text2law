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


def making_temp_title_dict(titles):
    pat_non_chars = re.compile(r'\W')
    temp_title_dict = {}
    for title in titles:
        temp_title_dict[pat_non_chars.sub("", title).lower()] = title
    return temp_title_dict

def extract_titles(text):
    """
    Extracting titles from magyar közlöny's html version.
    1, searching for a line starting with <li> and ending with </li> tag.
        - could not rely on <ul> tags, because the following pattern occured much:
            <ul>	<li>Title</li>
            <ul>	<li>description</li>
            </ul>
    2, the first letter has to be an upper character or a number
        - Titles are starts with uppercase, while description starts with lowercase
          most of the time. Some description starts with uppercase, like:
          Magyarország Kormánya és Türkmenisztán Kormánya közötti gazdasági együttműködésről
          szóló Megállapodás kihirdetéséről
    """

    keywords = ["határozata", "rendelete", "törvény", "végzése", "helybenhagyásáról",
                "közleménye", "követelmények", "rendelkezések", "rendelet", "állásfoglalása",
                "határozat", "módosítása", "nyilatkozata", "nyivánításáról"]
    pat_litag = re.compile(r'< *li *>(.+?)< */ *li *>')
    li_conts = pat_litag.findall(text)
    titles = []
    for cont in li_conts:
        cont = cont.strip()
        if len(cont) < 1:
            continue
        firstchar = cont[0]
        if firstchar.isupper() or firstchar.isdigit():
            for keyword in keywords:
                if keyword in cont:
                    titles.append(cont)
                    break
    return titles


def extract_legislation(titles, splittext):
    pat_non_chars = re.compile(r'\W')
    pat_tags = re.compile(r'<.*?>')
    legislation = []
    legislations = []
    is_legislation = False
    leg_title = ""
    temp_title_dict = making_temp_title_dict(titles)

    for line in splittext:
        line = line.strip()
        line = pat_tags.sub("", line)
        if line == "":
            continue
        raw_line = pat_non_chars.sub("", line.lower())
        for raw_title in temp_title_dict:
            if raw_title in raw_line or raw_line in raw_title:
                title = temp_title_dict[raw_title]
                is_legislation = True
                if len(legislation) != 0:
                    legislations.append((leg_title.split("_")[-1], leg_title, legislation))
                leg_title = remove_accent(pat_non_chars.sub(r'_', title)).lower()
                legislation = []
                del temp_title_dict[raw_title]
                break

        if is_legislation:
            legislation.append(line)
    legislations.append((leg_title.split("_")[-1], leg_title, legislation))
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
    prefix_dict = {"hatarozata": "hat", "rendelete": "rnd", "torveny": "trv",
                   "vegzese": "veg", "kozlemenye": "koz","rendelet": "rnd",
                   "hatarozat": "hat", "modositasa": "mod", "nyilatkozata": "nyil"}

    for finp in files:
        text = read_file(finp)
        titles = extract_titles(text)
        legislations = extract_legislation(titles, text.split("<p>"))
        for legislation in legislations:
            prefix = ""
            if legislation[0] in prefix_dict.keys():
                prefix = prefix_dict[legislation[0]]
            write_out(legislation[2], basp, prefix+"_"+legislation[1]+".txt")


if __name__ == "__main__":
    main()
