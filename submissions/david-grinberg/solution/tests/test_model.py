import json

import joblib
import numpy as np
import pandas as pd
import pytest

import analytic_base as ab
import model


def test_features_exclude_forbidden_ids_dates_and_labels():
    assert not model.FORBIDDEN & set(model.FEATURES)
    assert not model.NOT_FEATURES & set(model.FEATURES)
    assert "generator_hazard" not in model.FEATURES and "tenure_days" in model.FEATURES


def test_splits_are_ordered_with_purge_and_test_last():
    cutoffs = pd.date_range("2023-01-31", "2024-12-31", freq="ME")
    s = pd.DataFrame({"account_id": "A1", "cutoff_date": cutoffs,
                      model.LABEL: pd.array([False] * len(cutoffs), dtype="boolean")})
    tr, va, te = (model.split(s, n)["cutoff_date"] for n in ("treino", "validação", "teste"))
    gap = pd.Timedelta(days=model.HORIZON_DAYS)
    assert tr.max() + gap <= va.min() and va.max() + gap <= te.min()
    assert te.max() < pd.Timestamp("2024-12-31")  # corte de pontuação nunca entra em avaliação


def test_prioritization_counts_top_k_per_cutoff():
    t1, t2 = pd.Timestamp("2024-01-31"), pd.Timestamp("2024-02-29")
    df = pd.DataFrame({
        "account_id": ["A", "B", "C", "D", "A", "B", "C", "D"],
        "cutoff_date": [t1] * 4 + [t2] * 4,
        model.LABEL: pd.array([True, False, False, True, False, True, False, False], dtype="boolean"),
        "mrr_active": [100, 10, 10, 50, 100, 10, 10, 50],
    })
    churn = pd.DataFrame({"account_id": ["A", "D", "B"],
                          "churn_date": [t1 + pd.Timedelta(days=5), t1 + pd.Timedelta(days=20), t2 + pd.Timedelta(days=9)]})
    score = np.array([0.9, 0.1, 0.2, 0.3, 0.1, 0.8, 0.2, 0.3])
    r = model.prioritization(df, score, capacity=0.25, churn=churn)  # K = 1 por corte
    assert r["true_alerts"] == 2 and r["precision"] == 1.0
    assert r["recall"] == pytest.approx(2 / 3)
    assert r["mrr_covered"] == pytest.approx(110 / 160)
    assert r["median_lead_days"] == pytest.approx(7.0)  # 5 e 9 dias


def test_calibration_rule_flags_biased_probabilities():
    rng = np.random.default_rng(1)
    p = rng.uniform(0.05, 0.4, 5000)
    df = pd.DataFrame({model.LABEL: pd.array(rng.random(5000) < p, dtype="boolean")})
    _, good = model.calibration(df, p)
    _, bad = model.calibration(df, p * 0.5)
    assert good["show_probability"] and not bad["show_probability"]


@pytest.mark.skipif(not (model.MODEL_DIR / f"{model.VERSION}.joblib").exists(), reason="rode model.py antes")
def test_saved_model_reproduces_published_scores():
    meta = json.loads((model.MODEL_DIR / "model_meta.json").read_text(encoding="utf-8"))
    scores = pd.read_csv(model.SCORES_DIR / f"scores_{meta['reference_date']}.csv")
    snaps, end, _ = model.load_snapshots()
    now = snaps[snaps["cutoff_date"] == end].sort_values("account_id", ignore_index=True)
    pipe = joblib.load(model.MODEL_DIR / f"{model.VERSION}.joblib")
    assert scores["account_id"].tolist() == now["account_id"].tolist()
    np.testing.assert_allclose(np.round(pipe.predict_proba(model.X(now))[:, 1], 6), scores["model_score"], atol=1e-6)
    assert set(scores["reference_date"]) == {meta["reference_date"]} and set(scores["model_version"]) == {model.VERSION}
    assert len(scores) == len(ab.eligible_accounts(*(model.clean_data.load_clean(t) for t in ("accounts", "subscriptions")), end))
