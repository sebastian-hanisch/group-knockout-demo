"""Sweeps: Kollusions-Haeufigkeit, Rang-Fehlerfortpflanzung."""

from gko_evaluation import collusion_stats, rank_preservation_stats, rank_preservation_sweep


def test_collusion_stats_rates_sum_to_one():
    stats = collusion_stats(200, n_groups=4)
    assert stats.n_groups == 800
    total = stats.genuine_rate + stats.always_saved_rate + stats.none_rate
    assert abs(total - 1.0) < 1e-9


def test_collusion_stats_genuine_rate_is_plausible():
    """Simuliert (Elo-gewichtet) sollte die Rate niedriger liegen als die rein kombinatorische
    Referenz (26/243 ~= 10.7%), da ausgeglichene Punktegleichstaende unter realistischen
    Staerkeunterschieden seltener sind."""
    stats = collusion_stats(1500, n_groups=4)
    assert 0.0 <= stats.genuine_rate < 0.05


def test_rank_preservation_stats_probabilities_in_range():
    stats = rank_preservation_stats(300, n_groups=4)
    assert 0.0 <= stats.p_strongest_reaches_knockout <= 1.0
    assert 0.0 <= stats.p_strongest_tops_group <= 1.0


def test_rank_preservation_sweep_returns_one_entry_per_n():
    results = rank_preservation_sweep([2, 4, 6], n_reps=200)
    assert [s.n_group_sizes for s in results] == [2, 4, 6]
