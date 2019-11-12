#! /usr/bin/env python3
import requests
import os
from glob import glob
import argparse
from pathlib import Path
from shutil import move

def write(outp, dir):
    # Path(dir).mkdir(parents=True, exist_ok=True)
    os.makedirs(dir, exist_ok=True)
    for out in outp:
        with open(os.path.join(dir, 'out_' + out[0]), 'w') as f:
            f.write(out[1])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='Path to file', nargs="+")
    parser.add_argument('-d', '--directory', help='Path of output file(s)', nargs='?')
    basp = 'emtsv_outp'
    args = parser.parse_args()
    files = []

    if args.filepath:
        for p in args.filepath:

            poss_files = glob(p)
            poss_files = [os.path.abspath(x) for x in poss_files]
            files += poss_files
            # files += p
    else:
        files = glob(os.path.join(os.getcwd(), "*.txt"))

    if args.directory:
        basp = os.path.abspath(args.directory)

    return {'dir': basp, 'files': files}


def parse_with_emtsv(fls):
    count = 0
    for fl in fls:
        with open(fl) as inp:
            # tok/morph/pos/conv-morph/dep/chunk/ner later
            try:
                # /chunk/ner'
                # /conll'
                response = requests.post('http://oliphant.nytud.hu:10001/tok/morph/pos/conv-morph/dep/chunk/ner', files={'file':inp})
                # print(response.text)
                count += 1
                print(fl, str(count))
                fname = os.path.basename(fl)
                #os.makedirs("analyzed_w_emtsv", exist_ok=True)
                #move(fl, "analyzed_w_emtsv/"+fname) 
                yield (fname, response.text)
                
            except UnicodeEncodeError:
                print("hibás fájl")
                continue
            


def main():
    args = get_args()
    outp = parse_with_emtsv(args['files'])
    write(outp, args['dir'])


if __name__ == "__main__":
    main()


