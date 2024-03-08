import json
import os
import tempfile

from bs4 import BeautifulSoup
import git
from nltk.tokenize import wordpunct_tokenize
from pylatexenc.latex2text import LatexNodes2Text
import requests

import constants


def fname_sort_key(fname: str) -> int:
    """Sorting comparison function for DFP filenames"""
    if "-" not in fname:
        assert fname == "DaoFP.tex" or not fname.endswith(".tex"), f"{fname = }"
        return 0
    return int(fname.split("-")[0])


def fetch_dfp() -> None:
    """Fetch The Dao of Functional Programming, tokenize, and save into JSON.

    First two lines of code from this [StackOverflow question/answer](https://stackoverflow.com/questions/51239168/how-to-download-single-file-from-a-git-repository-using-python).
    """
    # Create temporary dir
    t = tempfile.mkdtemp()
    # Clone into temporary dir
    git.Repo.clone_from(constants.URL_DFP, t, branch="master", depth=1)
    # Parse LaTeX, tokenize
    l = LatexNodes2Text()
    tokseqs = []
    for fname in sorted(os.listdir(t), key=fname_sort_key):
        if fname.endswith(".tex"):
            with open(f"{t}/{fname}", "r", encoding="utf-8") as f:
                file_text = l.latex_to_text(f.read())
                tokseqs.extend(wordpunct_tokenize(file_text))
    # Save
    with open(constants.PATH_DFP, "w", encoding="utf-8") as f:
        json.dump(tokseqs, f)


def fetch_kjb() -> None:
    """Fetch King James Bible, tokenize, and save into JSON."""
    # Fetch, get text
    url = constants.URL_KJB
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    text = soup.get_text()
    # Select proper text
    start_text = "The Old Testament"
    end_text = "*** END OF THE PROJECT GUTENBERG EBOOK"
    text = text[text.find(start_text) : text.find(end_text)]
    # Tokenize
    tokseqs = wordpunct_tokenize(text)
    # Save
    with open(constants.PATH_KJB, "w", encoding="utf-8") as f:
        json.dump(tokseqs, f)


def fetch_all() -> None:
    """Fetch both, save into JSONs."""
    fetch_dfp()
    fetch_kjb()


if __name__ == "__main__":
    fetch_all()
