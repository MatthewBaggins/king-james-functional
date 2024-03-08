from collections import Counter, defaultdict
from functools import reduce
import json
from operator import or_
import pickle
from typing import Hashable, TypeGuard, TypeVar

from tqdm import tqdm
from constants import PATH_DFP, PATH_KJB, PATH_MC, PATH_TOKSEQS_PRESENT_PER_DOC


def is_list_of_strings(x) -> TypeGuard[list[str]]:
    return isinstance(x, list) and all(isinstance(x_, str) for x_ in x)


# TODO: rename this etc
MarkovChain = defaultdict[tuple[str, ...], Counter[str]]


def load_tokseq(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        tokseq = json.load(f)
    assert is_list_of_strings(tokseq), f"{type(tokseq)=}; {tokseq=}"
    return tokseq


T = TypeVar("T", bound=Hashable)


def get_distinct_elements(sets: list[set[T]]) -> list[set[T]]:
    """For each set, get elements that are distinct for this set."""
    return [
        s.difference(reduce(or_, sets[:i] + sets[i + 1 :], set()))
        for i, s in enumerate(sets)
    ]


TokseqsPresentPerDoc = list[set[tuple[str, ...]]]


def build_mc(
    path_or_paths: str | list[str], mc_length: int
) -> tuple[MarkovChain, TokseqsPresentPerDoc]:
    paths = [path_or_paths] if isinstance(path_or_paths, str) else path_or_paths
    mc: MarkovChain = defaultdict(Counter)
    tokseqs = [load_tokseq(path) for path in paths]
    max_n_toks = max(len(tokseq) for tokseq in tokseqs)
    tokseq_weights = [max_n_toks // len(tokseq) for tokseq in tokseqs]
    tokseqs_present_per_doc: TokseqsPresentPerDoc = [set() for _ in paths]
    for doc_i, (path, tokseq, weight) in enumerate(zip(paths, tokseqs, tokseq_weights)):
        for tok_i, tok in tqdm(
            enumerate(tokseq[mc_length:], mc_length),
            desc=path,
            leave=False,
        ):
            prev_toks = tuple(tokseq[tok_i - mc_length : tok_i])
            mc[prev_toks][tok] += weight
            tokseqs_present_per_doc[doc_i].add(prev_toks)
    tokseqs_present_per_doc = get_distinct_elements(tokseqs_present_per_doc)
    return mc, tokseqs_present_per_doc


def build_all() -> None:
    paths = [PATH_DFP, PATH_KJB]
    mc_lengths = [3, 4, 5]
    for mc_length in mc_lengths:
        mc, tokseqs_present_per_doc = build_mc(paths, mc_length)
        mc_save_path = PATH_MC.format(mc_length=mc_length)
        # save_path = constants.PATH_MC.replace("mc.", f"mc{mc_length}.")
        with open(mc_save_path, "wb") as f:
            pickle.dump(mc, f)
        tokseqs_present_per_doc_save_path = PATH_TOKSEQS_PRESENT_PER_DOC.format(
            mc_length=mc_length
        )
        with open(tokseqs_present_per_doc_save_path, "wb") as f:
            pickle.dump(tokseqs_present_per_doc, f)


if __name__ == "__main__":
    build_all()
