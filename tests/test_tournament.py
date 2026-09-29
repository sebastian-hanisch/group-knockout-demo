"""Gesamtablauf: Gruppenphase -> Aufsteiger -> K.-o.-Runde."""

import pytest

from gko_scenario import generate_scenario
from gko_tournament import run_tournament, strongest_team_reached_knockout, strongest_team_topped_its_group


@pytest.mark.parametrize("n_groups", [2, 4, 8])
def test_run_tournament_produces_consistent_structure(n_groups):
    scenario = generate_scenario(n_groups, seed=1)
    result = run_tournament(scenario, seed=1)
    assert len(result.groups) == n_groups
    assert len(result.collusion) == n_groups
    assert len(result.seed_to_team) == 2 * n_groups
    assert result.bracket.n_seeds == 2 * n_groups
    assert result.knockout.champion in result.seed_to_team


def test_advancers_are_exactly_the_top_two_of_each_group():
    scenario = generate_scenario(4, seed=1)
    result = run_tournament(scenario, seed=1)
    advancing_teams = set(result.seed_to_team.values())
    for g in result.groups:
        from gko_group import final_standings

        ranked = final_standings(g)
        assert ranked[0] in advancing_teams
        assert ranked[1] in advancing_teams
        assert ranked[2] not in advancing_teams
        assert ranked[3] not in advancing_teams


def test_no_team_appears_twice_as_a_seed():
    scenario = generate_scenario(6, seed=2)
    result = run_tournament(scenario, seed=2)
    teams = list(result.seed_to_team.values())
    assert len(teams) == len(set(teams))


def test_strongest_team_helpers_are_consistent():
    scenario = generate_scenario(4, seed=27)
    result = run_tournament(scenario, seed=27)
    reached = strongest_team_reached_knockout(result)
    topped = strongest_team_topped_its_group(result)
    if topped:
        assert reached  # Gruppensieger ist immer unter den Aufsteigern
    if not reached:
        assert topped is False


def test_deterministic_given_same_scenario_and_seed():
    scenario = generate_scenario(4, seed=5)
    r1 = run_tournament(scenario, seed=9)
    r2 = run_tournament(scenario, seed=9)
    assert r1.knockout.champion == r2.knockout.champion
    assert r1.seed_to_team == r2.seed_to_team
