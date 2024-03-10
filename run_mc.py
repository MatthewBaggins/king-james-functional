from argparse import ArgumentParser
import pickle
import random
import sys
from typing import NamedTuple

from colorama import Fore, Style

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
    seed: float | None
    mc_length: int
    n_seqs: int


def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument("seed", type=float, nargs="?", default=None, help="Random seed")
    parser.add_argument(
        "--mc_length", type=int, default=MC_LENGTH, help="Markov chain length"
    )
    parser.add_argument(
        "--n_seqs",
        type=int,
        default=5,
        help="Number of mixed-book sequences to be generated",
    )
    parsed_args = parser.parse_args()
    return Args(**vars(parsed_args))


def main() -> None:
    # Parse args, initialize random seed
    seed, mc_length, n_seqs = parse_args()
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
            concat_tokseq(
                [Fore.RED, *subchain1, Fore.GREEN, *subchain2, Style.RESET_ALL]
            )
        )


if __name__ == "__main__":
    main()
