import pickle
from pprint import pprint
import random
import sys
import time
from typing import cast

from tqdm import tqdm

from constants import PATH_MC, MC_LENGTH, PATH_TOKSEQS_PRESENT_PER_DOC
from build_mc import MarkovChain, TokseqsPresentPerDoc


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


def main() -> None:
    mc_length = sys.argv[1] if sys.argv[1:] else MC_LENGTH
    load_path = PATH_MC.format(mc_length=mc_length)
    with open(load_path, "rb") as f:
        mc: MarkovChain = pickle.load(f)

    key = random.choice(list(mc))
    print(" ".join(key), end=" ")
    for _ in range(300):
        x = sample_mc(mc, key)
        print(x, end=" ")
        key = (*key[1:], x)
    print()


def main_smart() -> None:
    mc_length = (
        int(sys.argv[1])
        if sys.argv[1:] and sys.argv[1].isdigit() and len(sys.argv[1]) == 1
        else MC_LENGTH
    )
    mc, tppd = load_mc_and_tppd(mc_length)
    key = random.choice(list(mc))
    chain = list(key)
    prev_sig = next(
        (i for i, s in enumerate(tppd) if key in s), None
    )  # TODO: rename and change tppd to dict maybe?
    sig_changes: list[int] = []
    for chain_i in tqdm(range(10000), leave=False):
        x = sample_mc(mc, key)
        key = (*key[1:], x)
        chain.append(x)
        sig = next((i for i, s in enumerate(tppd) if key in s), None)
        if sig != prev_sig and None not in (sig, prev_sig):
            sig_changes.append(chain_i)
            prev_sig = sig

    for i, sig_change_i in enumerate(sig_changes):
        print(i)
        print(" ".join(chain[sig_change_i - 50 : sig_change_i + 50]))


if __name__ == "__main__":
    main_smart()
