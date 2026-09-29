"""Rauchtests der Streamlit-Oberflaeche per AppTest: Standard, jedes Preset, Randgroessen, Regler."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import gko_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    if setup is not None:
        setup(at)
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("K.-o." in t.value for t in at.title)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders(name):
    p = C.PRESETS[name]

    def setup(at):
        at.session_state["n_groups_slider"] = p["n_groups"]
        at.session_state["seed_slider"] = p["seed"]
        at.session_state["focus_group_select"] = p["focus_group"]

    _run(setup)


def test_extreme_group_counts_render():
    def small(at):
        at.session_state["n_groups_slider"] = C.N_GROUPS_MIN

    _run(small)

    def large(at):
        at.session_state["n_groups_slider"] = C.N_GROUPS_MAX

    _run(large)


def test_focus_group_selectable_and_bounded_by_n_groups():
    def setup(at):
        at.session_state["n_groups_slider"] = 3
        at.session_state["focus_group_select"] = 2

    at = _run(setup)
    assert not at.exception


def test_round_slider_resets_when_focus_group_changes():
    at = _run()
    at.session_state["gko_round_slider"] = 1
    at.run()
    assert at.session_state["gko_round_slider"] == 1
    at.session_state["focus_group_select"] = 1
    at.run()
    assert not at.exception
    assert at.session_state["gko_round_slider"] == 3
