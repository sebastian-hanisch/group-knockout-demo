"""Szenario-Generator: n_groups*4 Teams mit Elo-Ratings, in Gruppen zu je 4 eingeteilt (Snake-Draft nach
Rating - ein starkes, ein mittleres, ein schwaechere Paar je Gruppe, wie ein vereinfachtes Lostopf-
Verfahren; echte Turniere ziehen komplexer nach Kontinentalverband, hier bewusst vereinfacht)."""

from __future__ import annotations

import random
from dataclasses import dataclass

GROUP_SIZE = 4
BASE_RATING = 1500.0
RATING_SPREAD = 400.0


@dataclass(frozen=True)
class Scenario:
    n_groups: int
    seed: int
    ratings: tuple[float, ...]  # Index = Team-ID (0..n_teams-1)
    groups: tuple[tuple[int, ...], ...]  # je Gruppe eine Liste von 4 Team-IDs


def generate_scenario(n_groups: int, seed: int) -> Scenario:
    if n_groups < 2:
        raise ValueError("n_groups muss mindestens 2 sein")
    n_teams = n_groups * GROUP_SIZE
    rng = random.Random(seed)
    ratings = [round(BASE_RATING + rng.uniform(-RATING_SPREAD, RATING_SPREAD), 1) for _ in range(n_teams)]

    order = sorted(range(n_teams), key=lambda t: -ratings[t])
    pots = [order[i * n_groups:(i + 1) * n_groups] for i in range(GROUP_SIZE)]
    for pot in pots[1:]:
        rng.shuffle(pot)

    groups = [tuple(pots[p][g] for p in range(GROUP_SIZE)) for g in range(n_groups)]
    return Scenario(n_groups=n_groups, seed=seed, ratings=tuple(ratings), groups=tuple(groups))
