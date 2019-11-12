import requests
import bs4
from pathlib import Path
import os

URLS = []


def walkpage(r, url, issues):
    soup = bs4.BeautifulSoup(r.text, "lxml")
    for ref in soup.find_all('a', href=True):
        ref = ref['href']
        if ref not in URLS and ref not in issues:
            URLS.append(ref)
            if ref.startswith("index.php"):
                if "nkonline" not in url:
                    # mire ide elér a progi, az url-ben valszeg benne van az nkonline.
                    url = "http://www.kozlonyok.hu/kozlonyok/"
                    walkpage(requests.get(url+ref), url, issues)
                elif "pageindex=0600" not in ref:
                    url = "http://www.kozlonyok.hu/nkonline/"
                    walkpage(requests.get(url+ref), url, issues)
            elif ref.startswith("../nkonline"):
                url = "http://www.kozlonyok.hu/nkonline/"
                walkpage(requests.get("http://www.kozlonyok.hu/" + ref[2:]), url, issues)
                url = "http://www.kozlonyok.hu/kozlonyok/"
            if ref.endswith(".pdf") and not ref.startswith("http"):
                issues.append(ref)
                print("talált közlöny:", ref)
                try:
                    link = requests.get(url+ref)
                    kozlonyurl = ref.split("/")
                    pth = os.path.join("d:", "Asztal", "ltk", *kozlonyurl[:-1])
                    Path(pth).mkdir(parents=True, exist_ok=True)

                    with open(os.path.join(pth, kozlonyurl[-1]), "wb") as f:
                        f.write(link.content)
                except MemoryError:
                    print("memória hiba:", ref)
                with open("downloaded_issues.txt", "a", encoding="utf-8") as f:
                    f.write(ref+"\n")
        URLS.append(ref)


def main():
    # with open("downloaded_issues.txt", "r", encoding="utf-8") as f:
    #     issues = ".pdf\n".join(f.read().split(".pdf")).replace("\n\n", ".pdf\n")
    #
    # with open("downloaded_issues.txt", "w", encoding="utf-8") as f:
    #     f.write(issues)
    try:
        with open("downloaded_issues.txt", "r", encoding="utf-8") as f:
            issues = f.read().split("\n")
    except FileNotFoundError:
        issues = []
    url = "http://kozlonyok.hu/kozlonyok/valaszt.htm"
    r = requests.get(url)
    walkpage(r, url, issues)


if __name__ == "__main__":
    main()
