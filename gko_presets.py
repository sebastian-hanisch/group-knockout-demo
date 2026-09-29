"""SETTING_SPECS-Permalink-Muster (Standardmuster aus dem OR-Demo-Portfolio, s. drr_presets.py)."""

import math
from dataclasses import dataclass
from typing import Callable, Optional

import streamlit as st

import gko_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: Optional[float] = None
    hi: Optional[float] = None


SETTING_SPECS = {
    "n_groups_slider": SettingSpec("n", int, C.DEFAULT_N_GROUPS, C.N_GROUPS_MIN, C.N_GROUPS_MAX),
    "seed_slider": SettingSpec("seed", int, C.DEFAULT_SEED, C.SEED_MIN, C.SEED_MAX),
    "focus_group_select": SettingSpec("group", int, C.DEFAULT_FOCUS_GROUP, 0, None),
}


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
                if isinstance(value, float) and not math.isfinite(value):
                    continue
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    st.session_state["permalink_loaded"] = True


def sync_query_params(n_groups, seed, focus_group):
    try:
        st.query_params["n"] = str(int(n_groups))
        st.query_params["seed"] = str(int(seed))
        st.query_params["group"] = str(int(focus_group))
    except Exception:
        pass


def apply_preset(name):
    p = C.PRESETS[name]
    st.session_state["n_groups_slider"] = p["n_groups"]
    st.session_state["seed_slider"] = p["seed"]
    st.session_state["focus_group_select"] = p["focus_group"]
