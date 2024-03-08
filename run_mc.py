import pickle
import random
import sys
from typing import NamedTuple

from colorama import Fore, Style
from tqdm import tqdm

from src import (
    PATH_MC,
    MC_LENGTH,
    PATH_TOKSEQS_PRESENT_PER_DOC,
    concat_tokseq,
    MarkovChain,
    TokseqsPresentPerDoc,
)


def sample_mc(mc: MarkovChain, key: tuple[str, ...]) -> str:

    counter = mc[key]
    population = list(counter.keys())
    counts = list(counter.values())
    return random.sample(population, counts=counts, k=1)[0]


def load_mc_and_tppd(mc_length: int) -> tuple[MarkovChain, TokseqsPresentPerDoc]:
    mc_load_path = PATH_MC.format(mc_length=mc_length)
    tppd_load_path = PATH_TOKSEQS_PRESENT_PER_DOC.format(mc_length=mc_length)
    with open(mc_load_path, "rb") as f:
        mc: MarkovChain = pickle.load(f)
    with open(tppd_load_path, "rb") as f:
        tppd: TokseqsPresentPerDoc = pickle.load(f)
    return mc, tppd


class Args(NamedTuple):
    mc_length: int = MC_LENGTH
    n_seqs: int = 5
    seed: int | float | None = None


def parse_args() -> Args:
    match len(sys.argv):
        case 1:
            return Args()
        case 2:
            return Args(int(sys.argv[1]))
        case 3:
            return Args(int(sys.argv[1]), int(sys.argv[2]))
        case _:
            return Args(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))


def main() -> None:
    # Parse args, initialize random seed
    mc_length, n_seqs, seed = parse_args()
    random.seed(seed)

    # Load data, run chain
    mc, tppd = load_mc_and_tppd(mc_length)
    key = random.choice(list(mc))
    chain = list(key)
    prev_sig = next((i for i, s in enumerate(tppd) if key in s), None)
    sig_changes: list[int] = []
    chain_i = 0
    while len(sig_changes) < n_seqs or chain_i - 50 < sig_changes[-1]:
        x = sample_mc(mc, key)
        key = (*key[1:], x)
        chain.append(x)
        sig = next((i for i, s in enumerate(tppd) if key in s), None)
        if sig != prev_sig and None not in (sig, prev_sig):
            sig_changes.append(chain_i)
            prev_sig = sig
        chain_i += 1

    # Pring
    for i, sig_change_i in enumerate(sig_changes):
        print(i)
        subchain1 = chain[sig_change_i - 50 : sig_change_i]
        subchain2 = chain[sig_change_i : sig_change_i + 50]
        print(
            Fore.RED,
            concat_tokseq(subchain1),
            Fore.GREEN,
            concat_tokseq(subchain2),
            Style.RESET_ALL,
        )


if __name__ == "__main__":
    main()
