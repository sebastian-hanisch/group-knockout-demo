"""Regressionstests gegen die konkreten Zahlen aus README.md - reine Python-Simulation (kein Solver),
deterministisch bei festem Seed, daher enge Toleranzen zulaessig."""

import pytest

import gko_constants as C
from gko_evaluation import collusion_stats, rank_preservation_sweep
from gko_group import theoretical_collusion_rates


def test_readme_theoretical_collusion_rate():
    genuine, always_saved, none = theoretical_collusion_rates()
    assert genuine == pytest.approx(26 / 243, abs=1e-9)
    assert always_saved == pytest.approx(17 / 243, abs=1e-9)
    assert none == pytest.approx(200 / 243, abs=1e-9)


def test_readme_simulated_collusion_rate():
    stats = collusion_stats(C.COLLUSION_STATS_REPS, n_groups=4)
    assert stats.genuine_rate == pytest.approx(0.00554, abs=0.002)
    assert stats.always_saved_rate == pytest.approx(0.00167, abs=0.001)
    # Kernbehauptung: simulierte Rate deutlich unter der rein kombinatorischen Referenz
    assert stats.genuine_rate < 26 / 243


def test_readme_rank_preservation_n4():
    sweep = rank_preservation_sweep([4], n_reps=C.SWEEP_REPS)
    stats = sweep[0]
    assert stats.p_strongest_reaches_knockout == pytest.approx(0.916, abs=0.02)
    assert stats.p_strongest_tops_group == pytest.approx(0.676, abs=0.03)


def test_readme_preset_seed_27_group_3_is_genuine_advantage():
    from gko_scenario import generate_scenario
    from gko_tournament import run_tournament

    scenario = generate_scenario(4, seed=27)
    result = run_tournament(scenario, seed=27)
    assert result.collusion[3].genuine_information_advantage


def test_readme_preset_seed_506_group_2_is_always_saved():
    from gko_scenario import generate_scenario
    from gko_tournament import run_tournament

    scenario = generate_scenario(4, seed=506)
    result = run_tournament(scenario, seed=506)
    assert result.collusion[2].always_saved
