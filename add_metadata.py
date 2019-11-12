#! /usr/bin/env python3

import os
import re
from convert2conll import get_args
from time import gmtime, strftime


DOC_TYPES_HUN = {"határozat": "decree",
                 "törvény": "law",
                 "állásfoglalás": "position",
                 "rendelet": "regulation",
                 "intézkedés": "act",
                 "közlemény": "notice",
                 "nyilatkozat": "declaration",
                 "parancs": "order",
                 "utasítás": "ordinance",
                 "szakutasítás": "ordinance",
                 "végzés": "judgment",
                 "tájékoztató": "notification",
                 "UNDEFINED": "UNDEFINED"}

DOC_TYPES_ENG = {"decree": "határozat",
                 "law": "törvény",
                 "position": "állásfoglalás",
                 "regulation": "rendelet",
                 "act": "intézkedés",
                 "notice": "közlemény",
                 "declaration": "nyilatkozat",
                 "order": "parancs",
                 "ordinance": "utasítás",
                 "judgment": "végzés",
                 "notification": "tájékoztató",
                 "UNDEFINED": "UNDEFINED"}


def read(files):
    for fl in files:
        with open(fl, encoding="utf-8") as f:
            yield os.path.basename(fl), f.read()


def write(dir, outp, ext):
    os.makedirs(dir, exist_ok=True)
    # file_id.split()[-1][:-4] + ".conll"
    for outpf in outp:
        with open(os.path.join(dir, os.path.splitext(outpf[0])[0] + ext), "w", encoding="utf-8", newline="\n") as f:
            f.write(outpf[1] + "".join(outpf[2]))


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


def get_eng_type(word):
    if is_huntype(word):
        return DOC_TYPES_HUN[word]
    return "UNKNOWN"


def get_hun_type(word):
    if is_engtype(word):
        return DOC_TYPES_ENG[word]
    return "ISMERETLEN"


def is_huntype(word):
    if word in DOC_TYPES_HUN.keys():
        return True
    return False


def is_engtype(word):
    if word in DOC_TYPES_ENG.keys():
        return True
    return False


# def index_of(alist, elem):
#     # print("\n###\n", elem + "\n", alist)
#     for i, item in enumerate(alist):
#         if elem in item:
#             return i


def get_meta(topic, identifier, lemmas, cols, title):
    entp = get_eng_type(lemmas[-1])
    huntp = get_hun_type(entp)

    if entp != "law":
        issuer = "# issuer = " + title[-2]
    else:
        issuer = "# issuer = parlament"
    title = "# title = " + " ".join(title)
    newdoc_id = "# newdoc id = hu-" + identifier
    d = "# date = " + lemmas[0].split("/")[-1].replace(".", "")
    huntp = "# type = " + huntp
    entp = "# entype = " + entp
    if topic:
        topic = "# topic = " + topic
        return "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(cols, newdoc_id, d, title, huntp, entp, issuer, topic)
    else:
        return "{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(cols, newdoc_id, d, title, huntp, entp, issuer)


def process(inp):
    pat_pgraph = re.compile(r'^\d+[.] *§')
    for doc in inp:
        print(doc[0])
        textlist = [sent.split("\n") for sent in doc[1].strip().split("\n\n")]
        fname_wo_out = "_".join(os.path.basename(doc[0]).split("_")[1:])
        identifier = os.path.splitext(fname_wo_out)[0]

        lemmas = []
        pgraph_num = "-p1"
        is_topic = False
        title_end = False
        doc_type = ""
        title = ""
        topic = ""
        """
        ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC MARCELL:NE MARCELL:NP MARCELL:IATE MARCELL:EUROVOC
        """
        cols = "# global.columns = " + " ".join(textlist[0].pop(0).split("\t")).upper() + " MARCELL:IATE MARCELL:EUROVOC"

        for i, sent in enumerate(textlist):
            lines = []
            orig_sent = []
            for line in sent:
                elements = line.split("\t")
                space = " " if elements[9] == "_" else ""
                orig_sent.append(elements[1] + space)

                if is_topic:
                    if elements[1].replace("*", "") != ".":
                        topic += elements[1] + space
                    else:
                        is_topic = False

                elif not title_end:
                    lemmas.append(elements[2])
                    if is_huntype(elements[2]):
                        doc_type = elements[2]
                        title += doc_type
                        title_end = True
                        is_topic = True
                    else:
                        title += elements[1] + space
                if len(elements) > 1:
                    lines.append(elements[1])
            sentence = "".join(orig_sent)

            if doc_type == "törvény" or doc_type == "rendelet":
                pgraph = pat_pgraph.match(sentence)
                if i > 0 and pgraph:
                    pgraph_num = "-p" + pgraph.group().split(".")[0]
                    if pgraph_num != "-p1":
                        par_id = "# newpar id = " + identifier + pgraph_num + "\n"
                    else:
                        par_id = ""
                elif i == 0:
                    par_id = "# newpar id = " + identifier + pgraph_num + "\n"
                else:
                    par_id = ""
                textlist[i] = par_id + "# sent_id = " + identifier + "-s" + str(i+1) + pgraph_num + "\n" \
                                + "# text = " + sentence + "\n" + "\n".join(textlist[i]) + "\n\n"
            else:
                textlist[i] = "# sent_id = " + identifier + "-s" + str(i + 1) + \
                              "\n" + "# text = " + sentence + "\n" + "\n".join(textlist[i]) + "\n\n"

        file_id = "# file id = " + fname_wo_out

        meta = get_meta(topic, identifier, lemmas, cols, title.split())

        yield file_id.split()[-1][:-4], meta, textlist


def main():
    basp = 'corpus_'  # + strftime("%Y-%m-%d_%H%M%S", gmtime())
    args = get_args(basp)
    os.makedirs(args['dir'], exist_ok=True)
    inp = read(args['files'])
    outp = process(inp)
    write(args['dir'], outp, ".conllup")


if __name__ == "__main__":
    main()
