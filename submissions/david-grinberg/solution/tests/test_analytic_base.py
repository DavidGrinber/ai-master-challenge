import hashlib
import json

import pandas as pd
import pytest

import analytic_base as ab
import clean_data
import raw_data

LABELS = [f"churn_next_{h}d" for h in ab.HORIZONS]
END = pd.Timestamp("2024-04-01")  # última data do fixture (evento C2)


def ts(s):
    return pd.Timestamp(s)


def row(snap, account):
    return snap.set_index("account_id").loc[account]


def test_eligibility_needs_signup_and_active_subscription(clean_tables):
    assert ab.snapshot_at(clean_tables, ts("2024-01-12"), END)["account_id"].tolist() == ["A2"]
    assert ab.snapshot_at(clean_tables, ts("2024-01-31"), END)["account_id"].tolist() == ["A1", "A2"]


def test_exact_copies_count_as_legitimate_subscriptions(clean_tables):
    # DEC-018: o candidato decidiu tratar as cópias exatas como assinaturas legítimas.
    a1 = row(ab.snapshot_at(clean_tables, ts("2024-02-29"), END), "A1")
    assert a1["n_active_subs"] == 3 and a1["mrr_active"] == 500  # S1 + S2 + S3 (cópia de S2)


def test_labels_look_forward_and_are_null_when_censored(clean_tables):
    feb = row(ab.snapshot_at(clean_tables, ts("2024-02-29"), END), "A1")
    assert feb["churn_next_30d"] == True  # noqa: E712 - evento C1 em 2024-03-01
    assert pd.isna(feb["churn_next_60d"]) and pd.isna(feb["churn_next_90d"])
    assert feb["prior_churn_events"] == 0 and pd.isna(feb["days_since_last_churn"])

    mar = row(ab.snapshot_at(clean_tables, ts("2024-03-31"), END), "A1")
    assert mar["prior_churn_events"] == 1 and mar["days_since_last_churn"] == 30
    assert pd.isna(mar["churn_next_30d"])


def test_features_ignore_everything_after_the_cutoff(clean_tables):
    t = ts("2024-02-29")
    before = ab.snapshot_at(clean_tables, t, END).drop(columns=LABELS)
    future = {name: df.copy() for name, df in clean_tables.items()}
    fu = future["feature_usage"]
    extra = fu.iloc[[0]].assign(usage_row_id="UR-99999", usage_date=ts("2024-03-01"), usage_count=999, error_count=99)
    future["feature_usage"] = pd.concat([fu, extra], ignore_index=True)
    tk = future["support_tickets"]
    late = tk.iloc[[0]].assign(ticket_id="T9", submitted_at=ts("2024-03-01"), closed_at=ts("2024-03-02"))
    future["support_tickets"] = pd.concat([tk, late], ignore_index=True)
    sub = future["subscriptions"]
    new = sub.iloc[[1]].assign(subscription_id="S9", start_date=ts("2024-03-01"), mrr_amount=5000)
    future["subscriptions"] = pd.concat([sub, new], ignore_index=True)

    after = ab.snapshot_at(future, t, END).drop(columns=LABELS)
    pd.testing.assert_frame_equal(before, after)


def test_windows_split_recent_and_previous_usage(clean_tables):
    a1 = row(ab.snapshot_at(clean_tables, ts("2024-02-29"), END), "A1")
    # uso de A1: 01-05 (3), 02-10 (4), 02-11 (0); 03-05 fica no futuro.
    # (t-30, t] = 01-31..02-29; (t-60, t-30] = 01-01..01-30, que contém 01-05.
    assert a1["usage_rows_30d"] == 2 and a1["usage_count_30d"] == 4
    assert a1["usage_count_prev_30d"] == 3 and a1["usage_rows_to_date"] == 3
    assert a1["days_since_last_usage"] == 18


def test_reconciliation_holds_on_fixture(clean_tables):
    cutoffs = list(pd.date_range("2024-01-31", END, freq="ME"))
    profile = ab.build_profile(clean_tables, END)
    snaps = ab.build_snapshots(clean_tables, cutoffs, END)
    # Último corte do fixture é 2024-03-31; reconcile compara o corte final com o fim dos dados.
    checks = ab.reconcile(clean_tables, profile, snaps, END)
    profile_checks = [c for c in checks if c["check"].startswith("perfil")]
    assert all(c["ok"] for c in profile_checks), profile_checks


@pytest.mark.skipif(raw_data.check(raw_data.RAW_DIR, raw_data.load_manifest()["files"]) != [],
                    reason="originais ausentes; rode raw_data.py fetch")
def test_real_base_reconciles_and_is_deterministic(tmp_path):
    raw = clean_data.read_raw(raw_data.RAW_DIR)
    tables, _ = clean_data.clean(raw)
    end = clean_data.data_end(raw)
    runs = [ab.build_all(tables, end, tmp_path / d / "p", tmp_path / d / "o", tmp_path / d / "dict.md", {})
            for d in ("a", "b")]
    (manifest, checks), (manifest_b, _) = runs
    assert all(c["ok"] for c in checks), [c for c in checks if not c["ok"]]
    assert manifest == manifest_b
    assert {n: t["rows"] for n, t in manifest["tables"].items()} == {"snapshots": 5254, "accounts_retrospective": 500}

    counts = pd.read_csv(tmp_path / "a" / "o" / "label_counts.csv").set_index("cutoff_date")
    assert counts.loc["2024-11-30", ["eligible", "positives_30d"]].tolist() == [475, 75]
    assert counts.loc["2024-10-31", ["eligible", "positives_30d", "positives_60d"]].tolist() == [439, 48, 97]

    snaps = clean_data.read_typed(tmp_path / "a" / "p" / "snapshots.csv", manifest["tables"]["snapshots"]["columns"])
    open_mrr = tables["subscriptions"].query("end_date.isna()")["mrr_amount"].sum()
    assert snaps.loc[snaps["cutoff_date"] == end, "mrr_active"].sum() == open_mrr == 10159608
    assert hashlib.sha256((tmp_path / "a" / "p" / "snapshots.csv").read_bytes()).hexdigest() == manifest["tables"]["snapshots"]["sha256"]
    json.dumps(manifest)
