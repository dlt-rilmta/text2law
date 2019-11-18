#! /usr/bin/env python3

from pathlib import Path
import os.path
import tika
import re
from tika import parser
from bs4 import BeautifulSoup

tika.initVM()


def write_output(output, module, ext, fname):
    mydir = f'output/{module}/'
    Path(mydir).mkdir(parents=True, exist_ok=True)
    path = os.path.basename(fname)
    path = os.path.splitext(path)[0] + f'.{ext}'
    path = os.path.join(mydir, path)
    with open(path, 'w', encoding="utf-8") as f:
        print(output, file=f)


def tika_html(inp):
    try:
        parsed = parser.from_file(inp, xmlContent=True)
        return parsed['content']
    except KeyError:
        print("Could not extract HTML:", inp)


def replace_latin1(text):
    return text.replace("õ", "ő").replace("û", "ű").replace("Õ", "Ő").replace("Û", "Ű")


def load_processed_files():
    with open(os.path.join(os.getcwd(), "processed_files.txt"), "r", encoding="utf-8") as f:
        return f.read().split(",")


def remove_accent(s):
    accent_dict = {"á": "a", "ü": "u", "ó": "o", "ö": "o", "ő": "o", "ú": "u", "é": "e", "ű": "u", "í": "i"}

    for key in accent_dict:
        if key in s:
            s = s.replace(key, accent_dict[key])
    return s


def extract_name(htmltext):
    soup = BeautifulSoup(htmltext.lower().replace("•", "").replace("\t", " "), "lxml")
    titlepone = soup.find("meta", {"name": "date"})

    if not titlepone:
        return None

    docname = [None, None, None]
    issuedate = str(titlepone).split()[1]
    issuedate = issuedate[issuedate.find('"')+1: issuedate.find("-")]
    docname[1] = issuedate[-2:]

    pat_kozl_tp = re.compile(r'((?:[a-zöüóőúűáéí]+ +)+?)'
                             r'(\w*é *r *t *e *s *í *t *ő|'
                             r'k *ö *z *l *ö *n *y|'
                             r'f *i *g *y *e *l *ő|'
                             r't *á *r *a|'
                             r'h *a *t *á *r *o *z *a *t *a *i)')

    pat_kozl_iss = re.compile(r'(\d+ *[.] +s *z *á *m)')

    pat_header = re.compile(r'^(\d+)\s+(.+?$)|(^.+?)\s+(\d+)$', re.M)
    divs = soup.find_all('div')
    for div in divs:
        frstlstp = div.find_all('p')
        if len(frstlstp) < 2 or len(pat_header.findall(div.text)) > 1:
            continue
        j = 1
        header = pat_header.search(frstlstp[0].text or frstlstp[1].text)
        while header is None and len(frstlstp) >= j:
            header = pat_header.search(frstlstp[-j].text)
            j += 1
        if header:
            header = header.groups()[1] or header.groups()[2]
            kozl_iss = pat_kozl_iss.search(header)
            if kozl_iss:
                docname[2] = kozl_iss.group().split(".")[0]
            kozl_tp = pat_kozl_tp.search(header)
            if kozl_tp:
                docname[0] = remove_accent(kozl_tp.groups()[0].replace("szám ", "").replace(" ", "") \
                             + kozl_tp.groups()[1].replace(" ", "")[:3])
            if all(docname):
                break

    if not all(docname):
        return None
    issuenum = docname[2]
    converted_issuenum = ["0", "0", "0"]
    i_converted_issuenum = len(converted_issuenum)-1
    i_issuenum = len(issuenum)-1
    while i_issuenum > -1:
        converted_issuenum[i_converted_issuenum] = issuenum[i_issuenum]
        i_converted_issuenum -= 1
        i_issuenum -= 1
        docname[2] = "".join(converted_issuenum)
    return "".join(docname)


def process():
    try:
        processed_files = load_processed_files()
    except FileNotFoundError:
        processed_files = []
    for root, dirs, files in os.walk("./"):
        for fl in files:
            if os.path.join(root, fl).endswith(".pdf") and fl not in processed_files:
                print("\n###", os.path.join(root, fl))
                html = tika_html(os.path.join(root, fl))
                name = extract_name(replace_latin1(html))

                if html is not None and name is not None and name + ".pdf" not in processed_files:
                    print(os.path.join(root, fl), "-->", os.path.join(root, name + ".pdf"))
                    write_output(html, 'new_mellek_kozlonyok_outp', 'html', name)
                    processed_files.append(name + ".pdf")
                    with open(os.path.join(os.getcwd(), "processed_files.txt"), "a", encoding="utf-8") as f:
                        f.write(name + ".pdf,")

                elif name is None:
                    print("Could not extract a name", os.path.join(root, fl))
                elif html is None:
                    print("HTML is None", os.path.join(root, fl))
                elif name + ".pdf" in processed_files:
                    print("Already processed")


def main():
    process()


if __name__ == "__main__":
    main()
