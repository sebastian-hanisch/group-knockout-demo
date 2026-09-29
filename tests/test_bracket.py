"""K.-o.-Setzliste (identischer Mechanismus wie bracket-seeding-demo) und Turnierbaum-Simulation."""

import random

import pytest

from gko_bracket import build_bracket, next_power_of_two, simulate_knockout, standard_seed_order


def test_standard_seed_order_matches_known_16_table():
    assert standard_seed_order(16) == [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]


def test_standard_seed_order_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        standard_seed_order(6)


@pytest.mark.parametrize("n, expected", [(1, 1), (2, 2), (3, 4), (16, 16), (17, 32)])
def test_next_power_of_two(n, expected):
    assert next_power_of_two(n) == expected


def test_build_bracket_byes_go_to_top_seeds_when_not_power_of_two():
    bracket = build_bracket(12)
    assert bracket.bracket_size == 16
    real_slots = [s for s in bracket.round1_slots if s is not None]
    # alle 12 echten Setzplaetze sind vertreten (Reihenfolge folgt der Setzliste, nicht aufsteigend)
    assert set(real_slots) == set(range(1, 13))
    # die 4 Freilose (Setzplaetze > 12) treffen automatisch die obersten Setzplaetze
    phantom_opponents = []
    for i in range(0, len(bracket.round1_slots), 2):
        a, b = bracket.round1_slots[i], bracket.round1_slots[i + 1]
        if a is None:
            phantom_opponents.append(b)
        elif b is None:
            phantom_opponents.append(a)
    assert sorted(phantom_opponents) == [1, 2, 3, 4]


def test_simulate_knockout_produces_a_champion_and_full_elimination_record():
    bracket = build_bracket(8)
    ratings = {s: 1500.0 + (8 - s) * 20 for s in range(1, 9)}
    rng = random.Random(1)
    result = simulate_knockout(bracket, ratings, rng)
    assert result.champion in range(1, 9)
    assert set(result.elimination_round.keys()) == set(range(1, 9)) - {result.champion}


def test_top_seed_wins_most_often_with_large_rating_gap():
    bracket = build_bracket(8)
    ratings = {s: (2000.0 if s == 1 else 1000.0) for s in range(1, 9)}
    wins = 0
    for trial in range(200):
        rng = random.Random(trial)
        result = simulate_knockout(bracket, ratings, rng)
        if result.champion == 1:
            wins += 1
    assert wins > 180  # weit ueberlegen -> fast immer Sieger
