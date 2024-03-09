from functools import reduce
from operator import or_
from typing import Hashable, TypeGuard, TypeVar


def is_list_of_strings(x) -> TypeGuard[list[str]]:
    """Check whether `x` is a list of strings."""
    return isinstance(x, list) and all(isinstance(x_, str) for x_ in x)


T = TypeVar("T", bound=Hashable)


def get_distinct_elements(sets: list[set[T]]) -> list[set[T]]:
    """For each set, get elements that are distinct for this set."""
    return [
        s.difference(reduce(or_, sets[:i] + sets[i + 1 :], set()))
        for i, s in enumerate(sets)
    ]


# TODO: fix concatenation of quotation marks
def concat_prev_toks_and_next_tok(prev_toks: str, next_tok: str) -> str:
    if not prev_toks:
        return next_tok
    whitespace_followed_chars = ",.:;"
    if prev_toks[-1] in whitespace_followed_chars:
        return prev_toks + " " + next_tok
    non_whitespace_chars = "()[]{}'\"‘’'“”"
    if prev_toks[-1] in non_whitespace_chars or next_tok in non_whitespace_chars:
        return prev_toks + next_tok
    if next_tok in whitespace_followed_chars:
        return prev_toks + next_tok
    return prev_toks + " " + next_tok
    # return (
    #     prev_toks
    #     + (
    #         " "
    #         if ((prev_toks and prev_toks[-1].isalnum()) or next_tok[0].isalnum())
    #         and next_tok not in non_whitespace_chars
    #         and (prev_toks and prev_toks[-1] not in non_whitespace_chars)
    #         else ""
    #     )
    #     + next_tok
    # )


def concat_tokseq(tokseq: list[str]) -> str:
    return reduce(concat_prev_toks_and_next_tok, tokseq, "")
