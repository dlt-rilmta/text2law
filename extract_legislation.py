import os
import re
from glob import glob
from pathlib import Path


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


def write_out(list, fname):
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(list))


def extract_titles(p, finp):
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

    pat2 = re.compile(r'<li>(.+?)</li>')
    titles = []
    with open(p+ "/" + finp, "r", encoding="utf-8") as f:
        for line in f:
            s = pat2.search(line)
            if s:
                firstchar = s.group(1)[0]
                if firstchar != "M" and (firstchar.isupper() or firstchar.isdigit()):
                    # print(s.group(1))
                    titles.append(s.group(1))

    # print("\nPDF:", finp, ",CÍMEK SZÁMA: ", len(titles))
    # print("\n###########################################\n")
    return titles


def making_temp_title_dict_and_title_dict(titles):
    temp_title_dict = {}
    title_dict = {}
    for i, title in enumerate(titles):
        temp_title_dict[title.replace(" ", "")] = i
        title_dict[i] = title
    return temp_title_dict, title_dict


def extract_legislations(p, files):
    """

    """
    legislation = []
    Path("legislations").mkdir(parents=True, exist_ok=True)
    pat_non_chars = re.compile(r'\W')
    is_legislation = False
    leg_title = ""
    pat_ptag = re.compile(r'<p>(.+)')
    pat_tags = re.compile(r'< */? *(p|div) *(class="page")?/? *>')
    # check_titles = []
    for fname in files:
        titles = extract_titles(p, fname)
        temp_title_dict, title_dict = making_temp_title_dict_and_title_dict(titles)
        with open(p + "/" + fname, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                nospace_line = line.replace(" ", "")
                ptag_line = pat_ptag.search(nospace_line)
                if "<p>" in nospace_line and ptag_line and ptag_line.group(1) in temp_title_dict.keys():
                    title = title_dict[temp_title_dict[ptag_line.group(1)]]
                    # check_titles.append(title)
                    is_legislation = True
                    if len(legislation) != 0:
                        title_words = leg_title.split("_")
                        endword = title_words[len(title_words)-1]
                        Path("legislations/"+endword).mkdir(parents=True, exist_ok=True)
                        with open("legislations/" + endword + "/" + leg_title + ".txt", "w", encoding="utf-8") as f:
                            f.write("\n".join(legislation))
                    leg_title = remove_accent(pat_non_chars.sub(r'_', title)).lower()
                    legislation = []

                if is_legislation:
                    legislation.append(pat_tags.sub("", line))

    # print("\n".join(check_titles))
    # print("CÍMEK SZÁMA:", len(check_titles))


def main():
    p = 'pdf2text/output/tika-html'
    files = glob(p + "/*txt")
    files = [os.path.basename(x) for x in files]
    extract_legislations(p, files)


if __name__ == "__main__":
    main()
