"""Elo-Erwartungswert-Formel (Arpad Elo, USCF/FIDE-Standard) - identischer Mechanismus wie
bracket-seeding-demo (bs_elo.py), hier ohne Cross-Repo-Import selbststaendig portiert.

E_A = 1 / (1 + 10^((R_B - R_A) / 400)) - der Erwartungswert (= Gewinnwahrscheinlichkeit bei binärem
Ausgang) für Team A gegen Team B. Referenzwert: 200 Rating-Punkte Unterschied entsprechen rund 76 %
Gewinnwahrscheinlichkeit für den Favoriten.
"""

from __future__ import annotations


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
