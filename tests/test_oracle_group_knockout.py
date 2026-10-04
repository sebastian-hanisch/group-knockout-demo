"""Unabhängiges Orakel für Gruppenphase + K.-o.: (1) "sicher unter den ersten zwei" gegen Aufzählung aller Tiebreak-Reihenfolgen; (2) die 243-Vorgeschichten-Referenz
(26 / 17 / 200) und die Kollusionsanalyse einer simulierten Gruppe mit eigener Aufzählung; (3) Meisterwahrscheinlichkeiten des K.-o.-Baums (auch mit Freilosen) gegen exakte
Rekursion über den Baum; (4) Gruppensieg- und Aufstiegswahrscheinlichkeit des Stärksten gegen die exakte Aufzählung aller 3^6 Gruppenergebnisse."""

import itertools
import math
import random
from collections import Counter

import pytest

import gko_bracket as B
import gko_elo
import gko_group as G

PAIRS = [[(0, 3), (1, 2)], [(0, 2), (3, 1)], [(0, 1), (3, 2)]]
PT = {"home_win": (3, 0), "draw": (1, 1), "away_win": (0, 3)}
OUT = tuple(PT)


def guaranteed_top2(points):
    """Teams, die bei JEDER mit den Punkten verträglichen Tabellenreihenfolge unter den ersten zwei stehen."""
    teams = list(points)
    ok = set(teams)
    for perm in itertools.permutations(teams):
        pts = [points[t] for t in perm]
        if pts == sorted(pts, reverse=True):
            ok &= set(perm[:2])
    return ok


def test_safe_advancers_against_all_tiebreak_orders():
    for pts in itertools.product(range(10), repeat=4):
        d = dict(enumerate(pts))
        assert G.safe_advancers(d, 2) == guaranteed_top2(d), pts


def test_theoretical_collusion_rates_against_independent_enumeration():
    gen = alw = non = 0
    for r1, r2 in itertools.product(itertools.product(OUT, repeat=2), repeat=2):
        for a in OUT:
            pts = [0] * 4
            for (x, y), o in list(zip(PAIRS[0], r1)) + list(zip(PAIRS[1], r2)) + [(PAIRS[2][0], a)]:
                pts[x] += PT[o][0]
                pts[y] += PT[o][1]
            good = 0
            for b in OUT:
                q = pts[:]
                x, y = PAIRS[2][1]
                q[x] += PT[b][0]
                q[y] += PT[b][1]
                good += {x, y} <= guaranteed_top2(dict(enumerate(q)))
            gen, alw, non = gen + (0 < good < 3), alw + (good == 3), non + (good == 0)
    assert (gen, alw, non) == (26, 17, 200)
    assert [round(x * 243) for x in G.theoretical_collusion_rates()] == [26, 17, 200]


@pytest.mark.parametrize("seed", range(40))
def test_collusion_analysis_of_a_simulated_group_against_enumeration(seed):
    rng = random.Random(seed)
    ratings = tuple(rng.uniform(1100, 1900) for _ in range(8))
    ids = tuple(rng.sample(range(8), 4))
    g = G.simulate_group(ids, ratings, random.Random(seed))
    pts = {t: 0 for t in ids}
    for rnd in g.rounds[:2]:
        for m in rnd:
            pts[m.home] += PT[m.outcome][0]
            pts[m.away] += PT[m.outcome][1]
    a, b = g.rounds[2]
    pts[a.home] += PT[a.outcome][0]
    pts[a.away] += PT[a.outcome][1]
    good = []
    for o in OUT:
        q = dict(pts)
        q[b.home] += PT[o][0]
        q[b.away] += PT[o][1]
        if {b.home, b.away} <= guaranteed_top2(q):
            good.append(o)
    c = G.analyse_final_round_collusion(g)
    assert c.good_outcomes_for_b == tuple(good) and c.genuine_information_advantage == (0 < len(good) < 3) and c.always_saved == (len(good) == 3)
    assert G.final_standings(g) == sorted(ids, key=lambda t: (-g.points[t], t))


def exact_champion_probabilities(n, ratings):
    br = B.build_bracket(n)

    def rec(lo, hi):
        if hi - lo == 1:
            s = br.round1_slots[lo]
            return {} if s is None else {s: 1.0}
        mid = (lo + hi) // 2
        left, right = rec(lo, mid), rec(mid, hi)
        if not left or not right:
            return left or right
        out = {}
        for x, px in left.items():
            for y, py in right.items():
                e = gko_elo.expected_score(ratings[x], ratings[y])
                out[x] = out.get(x, 0.0) + px * py * e
                out[y] = out.get(y, 0.0) + px * py * (1 - e)
        return out

    return rec(0, br.bracket_size)


@pytest.mark.parametrize("n", [3, 5, 6, 8, 12])
def test_knockout_champion_distribution_against_exact_recursion(n):
    rng = random.Random(n)
    ratings = {s: 1500 + rng.uniform(-300, 300) for s in range(1, n + 1)}
    exact = exact_champion_probabilities(n, ratings)
    assert sum(exact.values()) == pytest.approx(1.0)
    br = B.build_bracket(n)
    reps = 8000
    wins = Counter(B.simulate_knockout(br, ratings, random.Random(i)).champion for i in range(reps))
    for s in range(1, n + 1):
        p = exact[s]
        assert abs(wins[s] / reps - p) < 5 * math.sqrt(max(p * (1 - p), 1e-6) / reps)


def test_seed_order_and_byes():
    assert B.standard_seed_order(16) == [1, 16, 8, 9, 4, 13, 5, 12, 2, 15, 7, 10, 3, 14, 6, 11]
    for n in range(2, 34):
        br = B.build_bracket(n)
        size = br.bracket_size
        assert sorted(s for s in br.round1_slots if s is not None) == list(range(1, n + 1))
        for i in range(0, size, 2):
            a, b = br.round1_slots[i], br.round1_slots[i + 1]
            if a is None or b is None:
                assert (a if b is None else b) <= size - n          # nur die obersten Setzplätze haben ein Freilos


def exact_group(ids, ratings):
    """Exakt über alle 3^6 Gruppenergebnisse: (P(Stärkster wird Erster), P(Stärkster unter den ersten zwei)); Gleichstand wie in der Demo nach Team-ID."""
    games = [p for r in PAIRS for p in r]
    probs = {g: G.outcome_probabilities(ratings[ids[g[0]]], ratings[ids[g[1]]]) for g in games}
    strongest = max(range(4), key=lambda i: ratings[ids[i]])
    top = reach = 0.0
    for outs in itertools.product(range(3), repeat=6):
        p, pts = 1.0, [0] * 4
        for g, o in zip(games, outs):
            p *= probs[g][o]
            pts[g[0]] += PT[OUT[o]][0]
            pts[g[1]] += PT[OUT[o]][1]
        order = sorted(range(4), key=lambda i: (-pts[i], ids[i]))
        top += p * (order[0] == strongest)
        reach += p * (strongest in order[:2])
    return top, reach


@pytest.mark.parametrize("seed", range(3))
def test_group_simulation_against_exact_enumeration(seed):
    rng = random.Random(100 + seed)
    ratings = tuple(1500 + rng.uniform(-400, 400) for _ in range(4))
    ids = (0, 1, 2, 3)
    top_p, reach_p = exact_group(ids, ratings)
    strongest = max(ids, key=lambda t: ratings[t])
    reps = 15000
    top = reach = 0
    for i in range(reps):
        order = G.final_standings(G.simulate_group(ids, ratings, random.Random(i)))
        top += order[0] == strongest
        reach += strongest in order[:2]
    for got, p in ((top, top_p), (reach, reach_p)):
        assert abs(got / reps - p) < 5 * math.sqrt(p * (1 - p) / reps)
