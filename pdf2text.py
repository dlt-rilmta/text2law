#! /usr/bin/env python3

from pathlib import Path
import tika
import re
from tika import parser
from bs4 import BeautifulSoup
import argparse
from glob import glob
from time import gmtime, strftime
import os


tika.initVM()


def write_output(output, module, ext, fname, wa):
    Path(module).mkdir(parents=True, exist_ok=True)
    path = os.path.basename(fname)
    path = os.path.splitext(path)[0] + f'.{ext}'
    path = os.path.join(module, path)
    with open(path, wa, encoding="utf-8") as f:
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


def get_issuedate(tags):
    print(tags)
    pat_ws = re.compile(r'\s+')
    pat_idate = re.compile(r'(\d{4})\.(?:január|február|március|április|május|június|július|'
                           r'augusztus|szeptember|október|november|december)', re.IGNORECASE)
    for t in tags:
        rawp = pat_ws.sub("", t.text)
        if rawp and not rawp[-1].isdigit():
            issuedate = pat_idate.search(rawp)
            if issuedate:
                print(issuedate)
                return issuedate.group(1)


def extract_name(htmltext):
    soup = BeautifulSoup(htmltext.lower().replace("•", "").replace("\t", " "), "lxml")
    divs = soup.find_all('div')
    issuedate = get_issuedate([p for div in divs[:5] for p in div.find_all('p')])

    if not issuedate:
        print("There's no issuedate")
        return None

    docname = [None, None, None]
    docname[1] = issuedate[2:]

    pat_kozl_tp = re.compile(r'((?:[a-zöüóőúűáéí]+ +)+?)'
                             r'(\w*é *r *t *e *s *í *t *ő|'
                             r'k *ö *z *l *ö *n *y|'
                             r'f *i *g *y *e *l *ő|'
                             r't *á *r *a|'
                             r'h *a *t *á *r *o *z *a *t *a *i)')

    pat_kozl_iss = re.compile(r'(\d+ *[.] +s *z *á *m)')

    pat_header = re.compile(r'^(\d+)\s+(.+?$)|(^.+?)\s+(\d+)$', re.M)
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
                docname[0] = remove_accent(kozl_tp.groups()[0].replace("szám ", "").replace(" ", "")\
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


def get_args():
    """
    Getting argumentums from terminal.

    :return: dictionary wich contains the path of output folder and the input folder(s)
    """
    prsr = argparse.ArgumentParser()
    prsr.add_argument('filepath', help='Path to file', nargs=1, type=str)
    prsr.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?',
                      default='./output_' + strftime("%Y-%m-%d_%H%M%S", gmtime()))
    # the default folder where the output files will be written.
    args = prsr.parse_args()
    # list of filepathes that will be read

    return {'dir': args.directory, 'files': args.filepath[0]}


def process(inp, outp):
    print(inp)
    try:
        processed_files = load_processed_files()
    except FileNotFoundError:
        processed_files = []
    for root, dirs, files in os.walk(inp):
        for fl in files:
            if os.path.join(root, fl).endswith(".pdf") and fl not in processed_files:
                print("\n###", os.path.join(root, fl))
                html = tika_html(os.path.join(root, fl))
                name = extract_name(replace_latin1(html))

                if html is not None and name is not None and name + ".pdf" not in processed_files:
                    print(os.path.join(root, fl), "-->", os.path.join(root, name + ".pdf"))
                    write_output(html, outp, 'html', name, "w")
                    processed_files.append(name + ".pdf")
                    write_output(os.path.join(root, fl), outp, 'txt', "processed_files", "a")

                elif name is None:
                    print("Could not extract a name", os.path.join(root, fl))
                    write_output(os.path.join(root, fl), outp, 'txt', "noname", "a")
                elif html is None:
                    print("HTML is None", os.path.join(root, fl))
                elif name + ".pdf" in processed_files:
                    print("Already processed")
                    write_output(os.path.join(root, fl), outp, 'txt', "nameduplicate", "a")


def main():
    args = get_args()
    process(args['files'], args['dir'])


if __name__ == "__main__":
    main()
