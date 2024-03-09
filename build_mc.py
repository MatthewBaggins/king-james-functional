from collections import Counter, defaultdict
import json
import pickle

from tqdm import tqdm

from src import (
    PATH_DFP,
    PATH_KJB,
    PATH_MC,
    PATH_TOKSEQS_PRESENT_PER_DOC,
    get_distinct_elements,
    is_list_of_strings,
    MarkovChain,
    TokseqsPresentPerDoc,
)


def load_tokseq(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        tokseq = json.load(f)
    assert is_list_of_strings(tokseq), f"{type(tokseq)=}; {tokseq=}"
    return tokseq


def build_mc(
    path_or_paths: str | list[str], mc_length: int
) -> tuple[MarkovChain, TokseqsPresentPerDoc]:
    paths = [path_or_paths] if isinstance(path_or_paths, str) else path_or_paths
    tokseqs = [load_tokseq(path) for path in paths]
    mc: MarkovChain = defaultdict(Counter)
    tppd: TokseqsPresentPerDoc = [set() for _ in paths]
    for doc_i, (path, tokseq) in enumerate(zip(paths, tokseqs)):
        for tok_i, tok in tqdm(
            enumerate(tokseq[mc_length:], mc_length),
            desc=f"({mc_length=}) Loading Markov chain from path {path!r}",
            leave=False,
        ):
            prev_toks = tuple(tokseq[tok_i - mc_length : tok_i])
            mc[prev_toks][tok] += 1
            tppd[doc_i].add(prev_toks)
    tppd = get_distinct_elements(tppd)
    return mc, tppd


def build_all() -> None:
    paths = [PATH_DFP, PATH_KJB]
    mc_lengths = [3, 4, 5]
    for mc_length in mc_lengths:
        mc, tokseqs_present_per_doc = build_mc(paths, mc_length)
        mc_save_path = PATH_MC.format(mc_length=mc_length)
        with open(mc_save_path, "wb") as f:
            pickle.dump(mc, f)
        tokseqs_present_per_doc_save_path = PATH_TOKSEQS_PRESENT_PER_DOC.format(
            mc_length=mc_length
        )
        with open(tokseqs_present_per_doc_save_path, "wb") as f:
            pickle.dump(tokseqs_present_per_doc, f)


if __name__ == "__main__":
    build_all()
