import os
import re
from glob import glob
from pathlib import Path


def read_file(finp):
    with open(finp, encoding="utf-8") as f:
        text = f.read()
        return text


def write_out(list, finp, fname):
    Path(finp).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(finp, fname), "w", encoding="utf-8") as f:
        f.write("\n".join(list))


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


def making_temp_title_dict_and_title_dict(titles):
    temp_title_dict = {}
    title_dict = {}
    for i, title in enumerate(titles):
        temp_title_dict[title.replace(" ", "")] = i
        title_dict[i] = title
    return temp_title_dict, title_dict


def extract_titles(text):
    """
    Extracting titles from magyar közlöny's html version.
    1, searching for a line starting with <li> and ending with </li> tag.
        - could not rely on <ul> tags, because the following pattern occured much:
            <ul>	<li>Title</li>
            <ul>	<li>description</li>
            </ul>
    2, the first letter has to be an upper character (except for M) or a number
        - Titles are starts with uppercase, while description starts with lowercase
          most of the time. Some description starts with uppercase, like:
          Magyarország Kormánya és Türkmenisztán Kormánya közötti gazdasági együttműködésről
          szóló Megállapodás kihirdetéséről
    """
    pat_litag = re.compile(r'< *li *>(.+?)< */ *li *>')
    lines = text.split("\n")
    titles = []
    for line in lines:
        s = pat_litag.search(line)
        if s:
            firstchar = s.group(1)[0]
            if firstchar != "M" and (firstchar.isupper() or firstchar.isdigit()):
                # print(s.group(1))
                titles.append(s.group(1))

    # print("\nPDF:", finp, ",CÍMEK SZÁMA: ", len(titles))
    # print("\n###########################################\n")
    return titles


def extract_legislation(titles, splittext):
    pat_non_chars = re.compile(r'\W')
    pat_ptag = re.compile(r'<p>(.+)')
    pat_tags = re.compile(r'<.*?>')
    legislation = []
    legislations = []
    is_legislation = False
    leg_title = ""
    temp_title_dict, title_dict = making_temp_title_dict_and_title_dict(titles)
    for line in splittext:
        line = line.strip()
        raw_line = pat_tags.sub("", line)
        if raw_line == "":
            continue
        ptag_line = pat_ptag.search(line.replace(" ", ""))
        if ptag_line and ptag_line.group(1) in temp_title_dict.keys():
            title = title_dict[temp_title_dict[ptag_line.group(1)]]
            is_legislation = True
            if len(legislation) != 0:
                legislations.append((leg_title.split("_")[-1], leg_title, legislation))
            leg_title = remove_accent(pat_non_chars.sub(r'_', title)).lower()
            legislation = []

        if is_legislation:
            legislation.append(raw_line)
    legislations.append((leg_title.split("_")[-1], leg_title, legislation))

    return legislations


def main():
    p = os.path.join("pdf2text", "output", "tika-html")
    basp = "legislations"
    files = glob(p + "\*txt")
    files = [os.path.basename(x) for x in files]
    # leg_count = []
    Path(basp).mkdir(parents=True, exist_ok=True)
    for finp in files:
        text = read_file(os.path.join(p, finp))
        titles = extract_titles(text)
        legislations = extract_legislation(titles, text.split("\n"))
        for legislation in legislations:
            # leg_count.append(legislation)
            write_out(legislation[2], os.path.join(basp,legislation[0]), legislation[1]+".txt")
    # print(len(leg_count))


if __name__ == "__main__":
    main()
