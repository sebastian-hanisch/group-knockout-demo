"""Kennzahlen: Kollusions-Haeufigkeit (theoretisch ueber alle Kombinationen vs. tatsaechlich simuliert
unter realistischen Elo-Staerkeunterschieden), Rang-Fehlerfortpflanzung durch Gruppenphase + K.-o."""

from __future__ import annotations

from dataclasses import dataclass

from gko_scenario import generate_scenario
from gko_tournament import run_tournament, strongest_team_reached_knockout, strongest_team_topped_its_group


@dataclass(frozen=True)
class CollusionStats:
    n_groups: int
    genuine_rate: float
    always_saved_rate: float
    none_rate: float


def collusion_stats(n_reps: int, n_groups: int = 4, seed_offset: int = 0) -> CollusionStats:
    genuine = always = none = total = 0
    for i in range(n_reps):
        sc = generate_scenario(n_groups, seed=seed_offset + 1000 + i)
        res = run_tournament(sc, seed=seed_offset + 2000 + i)
        for c in res.collusion:
            total += 1
            if c.genuine_information_advantage:
                genuine += 1
            elif c.always_saved:
                always += 1
            else:
                none += 1
    return CollusionStats(
        n_groups=total,
        genuine_rate=genuine / total,
        always_saved_rate=always / total,
        none_rate=none / total,
    )


@dataclass(frozen=True)
class RankPreservationStats:
    n_group_sizes: int
    p_strongest_reaches_knockout: float
    p_strongest_tops_group: float


def rank_preservation_stats(n_reps: int, n_groups: int, seed_offset: int = 0) -> RankPreservationStats:
    reached = topped = applicable = 0
    for i in range(n_reps):
        sc = generate_scenario(n_groups, seed=seed_offset + 5000 + i)
        res = run_tournament(sc, seed=seed_offset + 6000 + i)
        if strongest_team_reached_knockout(res):
            reached += 1
        t = strongest_team_topped_its_group(res)
        if t is not None:
            applicable += 1
            if t:
                topped += 1
    return RankPreservationStats(
        n_group_sizes=n_groups,
        p_strongest_reaches_knockout=reached / n_reps,
        p_strongest_tops_group=topped / applicable,
    )


def rank_preservation_sweep(n_groups_values: list[int], n_reps: int, seed_offset: int = 0):
    return [rank_preservation_stats(n_reps, n, seed_offset=seed_offset) for n in n_groups_values]
