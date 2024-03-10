from functools import reduce
from operator import or_
import re
from typing import Hashable, TypeGuard, TypeVar

from colorama import Fore


def is_list_of_strings(x, /) -> TypeGuard[list[str]]:
    """Check whether `x` is a list of strings."""
    return isinstance(x, list) and all(isinstance(y, str) for y in x)


T = TypeVar("T", bound=Hashable)


def get_distinct_elements(sets: list[set[T]]) -> list[set[T]]:
    """For each set, get elements that are distinct for this set."""
    return [
        s.difference(reduce(or_, sets[:i] + sets[i + 1 :], set()))
        for i, s in enumerate(sets)
    ]


WHITESPACE_FOLLOWED_CHARS = ",.:;)]}’”"
NON_WHITESPACE_CHARS = "([{‘“"
QUOTATION_MARKS = "'\""
COLOR_CHARS = f"{Fore.RED}{Fore.GREEN}"

PAT_START_QUOTE = re.compile(r'"\w')
PAT_END_QUOTE = re.compile(r'\w"')


def get_tok_concat_sep(prev_toks: str, next_tok: str) -> str:
    """Get the string that concatenates previous tokens to the next token."""
    # If next_tok is a colorama color char
    if next_tok in COLOR_CHARS:
        return ""

    # If next_tok is the first token
    if not prev_toks:
        return ""

    last_tok = prev_toks[-1]
    snd_last_tok = prev_toks[-2] if len(prev_toks) >= 1 else ""

    # Always just append '
    if next_tok == "'":
        return ""

    # If [\d+:\d+] (Bible chapter numberings)
    if last_tok == ":" and snd_last_tok.isdigit() and next_tok.isdigit():
        return ""

    # If last token is a single quote and it looks like English '-phrase
    if last_tok == "'" and next_tok in "snt":
        return ""

    # If last token was a double quote, determine whether it's a starting or ending quote
    if last_tok == '"':
        match_start = PAT_START_QUOTE.search(prev_toks)
        match_end = PAT_END_QUOTE.search(prev_toks)
        start_pos = match_start.start() if match_start is not None else 0
        end_pos = match_end.start() if match_end is not None else 0
        if start_pos < end_pos:
            return ""
        return " "
        # match (match_start, match_end):
        #     case (None, _):
        #         return ""
        #     case (_, None):
        #         return " "
        #     case (_, _):
        #         if match_start.start() < match_end.start():
        #             return ""
        #         return " "

        # if match_start is None and match_end is not None:
        #     return ""
        # if match_start and match_end is None:
        #     return " "

    # If next_tok is one always followed by whitespace
    if next_tok in WHITESPACE_FOLLOWED_CHARS:
        return ""

    # If last_tok is one always followed by whitespace
    if last_tok in WHITESPACE_FOLLOWED_CHARS:
        return " "

    # If a character that should heuristically never be followed by whitespace
    if last_tok in NON_WHITESPACE_CHARS:
        return ""

    # If standard quotation mark
    if last_tok in QUOTATION_MARKS:
        if snd_last_tok.isspace():
            return " "
        return ""
    return " "


def concat_tokseq(tokseq: list[str]) -> str:
    """ "Intelligently" concatenate a sequence of tokens."""
    return reduce(
        lambda prev_toks, next_tok: prev_toks
        + get_tok_concat_sep(prev_toks, next_tok)
        + next_tok,
        tokseq,
        "",
    )
