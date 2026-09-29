"""Gruppenphase: Zirkelmethode-Struktur, Punktezaehlung, Kollusionsanalyse, historische Cross-Checks."""

import random

import pytest

from gko_group import (
    GROUP_ROUNDS,
    analyse_final_round_collusion,
    final_standings,
    points_delta,
    safe_advancers,
    simulate_group,
    standings_after,
    theoretical_collusion_rates,
)


def test_every_team_plays_every_other_exactly_once():
    seen = set()
    for round_pairs in GROUP_ROUNDS:
        teams_in_round = set()
        for (a, b) in round_pairs:
            assert a not in teams_in_round and b not in teams_in_round
            teams_in_round.add(a)
            teams_in_round.add(b)
            seen.add(frozenset((a, b)))
    assert teams_in_round == {0, 1, 2, 3}
    assert len(seen) == 6  # C(4,2)


@pytest.mark.parametrize("outcome, expected", [("home_win", (3, 0)), ("draw", (1, 1)), ("away_win", (0, 3))])
def test_points_delta(outcome, expected):
    assert points_delta(outcome) == expected


def test_simulate_group_points_sum_is_consistent():
    # ratings ist wie im echten Szenario ueber ALLE Team-IDs indiziert, nicht nur die 4 Gruppenteams
    ratings = tuple(1500.0 for _ in range(14))
    rng = random.Random(1)
    group = simulate_group((10, 11, 12, 13), ratings, rng)
    # 6 Spiele insgesamt, jedes verteilt entweder 3+0 oder 1+1 Punkte -> Gesamtsumme zwischen 12 und 18
    total_points = sum(group.points.values())
    assert 12 <= total_points <= 18


def test_final_standings_orders_by_points_then_team_id():
    ratings = (1500.0,) * 4
    rng = random.Random(2)
    group = simulate_group((0, 1, 2, 3), ratings, rng)
    ranked = final_standings(group)
    pts = [group.points[t] for t in ranked]
    assert pts == sorted(pts, reverse=True)


def test_safe_advancers_conservative_on_full_tie():
    points = {0: 5, 1: 5, 2: 5, 3: 5}
    assert safe_advancers(points, top_k=2) == set()


def test_safe_advancers_clear_case():
    points = {0: 9, 1: 6, 2: 3, 3: 0}
    assert safe_advancers(points, top_k=2) == {0, 1}


def test_safe_advancers_boundary_tie_excludes_tied_teams():
    points = {0: 9, 1: 3, 2: 3, 3: 0}
    # Rang 2 und 3 punktgleich - beide unsicher, Rang 1 weiterhin sicher
    assert safe_advancers(points, top_k=2) == {0}


def test_analyse_final_round_collusion_runs_on_any_group():
    ratings = (1500.0,) * 4
    rng = random.Random(3)
    group = simulate_group((0, 1, 2, 3), ratings, rng)
    analysis = analyse_final_round_collusion(group)
    assert analysis.game_a != analysis.game_b
    assert set(analysis.good_outcomes_for_b) <= {"home_win", "draw", "away_win"}
    # genuine_information_advantage und always_saved schliessen sich gegenseitig aus (0<n<3 vs. n==3)
    assert not (analysis.genuine_information_advantage and analysis.always_saved)


def test_standings_after_zero_rounds_is_all_zero():
    ratings = (1500.0,) * 4
    rng = random.Random(4)
    group = simulate_group((0, 1, 2, 3), ratings, rng)
    assert standings_after(group, 0) == {t: 0 for t in (0, 1, 2, 3)}


def test_theoretical_collusion_rates_sum_to_one_and_match_measured_values():
    genuine, always_saved, none = theoretical_collusion_rates()
    assert genuine == pytest.approx(26 / 243)
    assert always_saved == pytest.approx(17 / 243)
    assert none == pytest.approx(200 / 243)
    assert genuine + always_saved + none == pytest.approx(1.0)
