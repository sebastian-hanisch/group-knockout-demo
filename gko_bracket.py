"""K.-o.-Runde: Setzlisten-Algorithmus (identischer Mechanismus wie bracket-seeding-demo, hier ohne
Cross-Repo-Import selbststaendig portiert) plus Turnierbaum-Simulation. Anders als die Gruppenphase gibt
es im K.-o. kein Remis (Verlaengerung/Elfmeterschiessen erzwingen einen Sieger) - reiner Elo-Munzwurf."""

from __future__ import annotations

import random
from dataclasses import dataclass

from gko_elo import expected_score


def standard_seed_order(size: int) -> list[int]:
    if size < 1 or size & (size - 1) != 0:
        raise ValueError("size muss eine Zweierpotenz sein")
    seeds = [1]
    while len(seeds) < size:
        m = 2 * len(seeds) + 1
        seeds = [x for s in seeds for x in (s, m - s)]
    return seeds


def next_power_of_two(n: int) -> int:
    size = 1
    while size < n:
        size *= 2
    return size


@dataclass(frozen=True)
class Bracket:
    n_seeds: int
    bracket_size: int
    round1_slots: tuple[int | None, ...]  # Setzplatz (1-indiziert) je Slot, None = Freilos-Phantom


def build_bracket(n_seeds: int) -> Bracket:
    if n_seeds < 2:
        raise ValueError("n_seeds muss mindestens 2 sein")
    bracket_size = next_power_of_two(n_seeds)
    order = standard_seed_order(bracket_size)
    slots = [seed if seed <= n_seeds else None for seed in order]
    return Bracket(n_seeds=n_seeds, bracket_size=bracket_size, round1_slots=tuple(slots))


def simulate_match(rating_a: float, rating_b: float, rng: random.Random) -> bool:
    """True, wenn Team A gewinnt (kein Remis moeglich - Verlaengerung/Elfmeter erzwingen einen Sieger)."""
    return rng.random() < expected_score(rating_a, rating_b)


@dataclass(frozen=True)
class KnockoutResult:
    champion: int  # Setzplatz
    rounds: tuple[tuple[int | None, ...], ...]  # Belegung je Runde, rounds[-1] = [Sieger]
    elimination_round: dict  # Setzplatz -> Runde, in der er ausschied


def simulate_knockout(bracket: Bracket, ratings_by_seed: dict, rng: random.Random) -> KnockoutResult:
    slots: list[int | None] = list(bracket.round1_slots)
    rounds: list[tuple[int | None, ...]] = [tuple(slots)]
    elimination_round: dict = {}
    round_number = 1
    while len(slots) > 1:
        next_slots: list[int | None] = []
        for i in range(0, len(slots), 2):
            a, b = slots[i], slots[i + 1]
            if a is None:
                next_slots.append(b)
                continue
            if b is None:
                next_slots.append(a)
                continue
            a_wins = simulate_match(ratings_by_seed[a], ratings_by_seed[b], rng)
            winner, loser = (a, b) if a_wins else (b, a)
            elimination_round[loser] = round_number
            next_slots.append(winner)
        slots = next_slots
        rounds.append(tuple(slots))
        round_number += 1
    return KnockoutResult(champion=slots[0], rounds=tuple(rounds), elimination_round=elimination_round)
