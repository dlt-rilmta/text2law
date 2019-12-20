import re
import os
from text2law import get_args


def read(inp):
    for fl in inp:
        with open(fl, encoding='utf-8') as f:
            return f.read().replace(u'\xa0', u' ').replace("  ", " "), os.path.basename(fl)


def tokmod(ls):
    newls = [ls[0]]
    for i, sent in enumerate(ls[1:]):
        if sent and (sent[0].islower() or sent[0] == "§"):
            newls[-1] += "\n" + sent
        else:
            newls.append(sent)
    return newls


def process(forparse, fl):
    pat_num_listing = re.compile(r'(\n *\d{,3}\. +[^§])', re.M)
    pat_abc_listing = re.compile(r'((?:: *a|(?:\n *[a-z]+)) *\) +(?!pontja).*?[,;.]) *\n', re.M | re.DOTALL)

    txtls = [sent.split("\n") for sent in tokmod([sent for sent in forparse.split("\n\n")])]
    new_txtls = []
    for i, sent in enumerate(txtls):
        if i == 0:
            new_txtls.append([sent.pop(0)])
        forparse = last_line = ""
        if len(sent) == 0:
            continue
        new_sent = []
        new_sents = []
        for j in range(len(sent)-1, -1, -1):
            line = sent[j]
            new_sent.insert(0, line)
            elems = line.split("\t")
            if len(elems) != 2:
                continue
            last_part = elems[0] + elems[1].replace("\\n", "\n").replace("\"", "")
            forparse = last_part + forparse
            # 50 <
            # TODO át kell majd adni paraméterben, hogy hány szónál hosszabb mondatokat szedjen szét
            num_list = pat_num_listing.search(forparse)
            abc_list = pat_abc_listing.search(forparse)
            if num_list or abc_list:
                new_sent.append(last_line)
                last_line = new_sent.pop(0)
                new_sents.insert(0, new_sent)
                new_sent = []
                forparse = last_part
            elif j == 0:
                new_txtls.append(new_sent)
                new_txtls.extend(new_sents)

    # csak teszteléshez
    # count = 0
    # for sent in new_txtls:
    #     forparse = ""
    #     for line in sent:
    #         count += 1
    #         elems = line.split("\t")
    #         if len(elems) == 2:
    #             forparse += elems[0] + elems[1].replace("\"", "")
    #     count += 1
    #     print("\n", count, forparse)
    # csak teszteléshez - vége

    with open("anl_simple_" + fl, "w", encoding="utf-8", newline="\n") as f:
        for sent in new_txtls:
            f.write("\n".join(sent).strip() + "\n\n")


def main():
    args = get_args()
    inp = read(args['files'])
    process(inp[0], inp[1])


if __name__ == "__main__":
    main()
