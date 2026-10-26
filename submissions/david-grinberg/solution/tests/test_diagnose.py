import numpy as np
import pandas as pd
import pytest

import diagnose as dg


def frame(groups):
    """groups: lista de (account_id, grupo, rótulo)."""
    return pd.DataFrame(groups, columns=["account_id", "group", dg.LABEL])


@pytest.mark.parametrize("intervals, kind, two_sided, expected", [
    ([(1.2, 2.0), (1.1, 1.8)], "rr", False, "apoiada"),
    ([(0.5, 0.8), (0.4, 0.9)], "rr", False, "refutada (direção oposta)"),
    ([(0.5, 0.8), (0.4, 0.9)], "rr", True, "apoiada (direção inversa)"),
    ([(0.95, 1.05), (0.93, 1.08)], "rr", False, "refutada (efeito nulo)"),
    ([(1.2, 2.0), (0.8, 1.3)], "rr", False, "inconclusiva"),
    ([(0.0, 0.9), (0.0, 0.8)], "rr", False, "refutada (direção oposta)"),  # limite inferior 0 em grupo pequeno
    ([(0.55, 0.65), (0.52, 0.70)], "auc", False, "apoiada"),
    ([(0.48, 0.52), (0.475, 0.525)], "auc", False, "refutada (efeito nulo)"),
    ([(0.43, 0.53), (0.41, 0.55)], "auc", False, "inconclusiva"),
])
def test_status_rule_matches_pre_registration(intervals, kind, two_sided, expected):
    assert dg.status(intervals, kind, two_sided) == expected


def test_rate_contrast_point_estimates_and_interval():
    rows = [(f"A{i}", "g", i < 5) for i in range(20)] + [(f"B{i}", "r", i < 2) for i in range(20)]
    df = frame(rows)
    r = dg.rate_contrast(df, df["group"] == "g", b=500)
    assert r["rate"] == pytest.approx(0.25) and r["rate_rest"] == pytest.approx(0.10)
    assert r["rr"] == pytest.approx(2.5)
    assert r["rr_lo"] < r["rr"] < r["rr_hi"]
    assert (r["n"], r["accounts"], r["positives"]) == (20, 20, 5)


def test_rate_contrast_counts_accounts_not_rows():
    rows = [("A1", "g", True), ("A1", "g", False), ("A1", "g", False), ("A2", "r", False), ("A3", "r", True)]
    r = dg.rate_contrast(frame(rows), frame(rows)["group"] == "g", b=50)
    assert (r["n"], r["accounts"]) == (3, 1)


def test_auc_ci_recovers_perfect_and_random_signals():
    rng = np.random.default_rng(0)
    n = 400
    y = rng.random(n) < 0.3
    df = pd.DataFrame({"account_id": [f"A{i}" for i in range(n)], dg.LABEL: y,
                       "perfect": y.astype(float), "noise": rng.random(n)})
    assert dg.auc_ci(df, "perfect", b=50)["auc"] == pytest.approx(1.0)
    noise = dg.auc_ci(df, "noise", b=100)
    assert noise["auc_lo"] < 0.5 < noise["auc_hi"]


def test_partitions_never_touch_the_reserved_test_period():
    cutoffs = pd.date_range("2023-01-31", "2024-12-31", freq="ME")
    s = pd.DataFrame({"account_id": "A1", "cutoff_date": cutoffs,
                      dg.LABEL: pd.array([True] * len(cutoffs), dtype="boolean")})
    used = pd.concat([dg.part(s, name) for name in dg.PARTS])["cutoff_date"]
    assert not used.between(*dg.TEST).any()
    assert used.max() + pd.Timedelta(days=30) <= pd.Timestamp(dg.TEST[0])  # purga com H = 30
    dev_last = dg.part(s, "desenvolvimento")["cutoff_date"].max()
    assert dev_last + pd.Timedelta(days=30) <= dg.part(s, "validação")["cutoff_date"].min()
