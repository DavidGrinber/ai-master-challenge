import hashlib

import pandas as pd
import pytest

import clean_data
import raw_data


def run_build(raw_dir, out):
    return clean_data.build(raw_dir, out / "clean", out / "quality", out / "report.md")


def file_hashes(directory):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.iterdir())}


def cleaned(raw_dir):
    return clean_data.clean(clean_data.read_raw(raw_dir))


def test_flags_on_known_cases(raw_dir):
    tables, _ = cleaned(raw_dir)
    acc = tables["accounts"].set_index("account_id")
    sub = tables["subscriptions"].set_index("subscription_id")
    fu = tables["feature_usage"].set_index("usage_row_id")
    tk = tables["support_tickets"].set_index("ticket_id")
    ce = tables["churn_events"].set_index("churn_event_id")

    assert acc["q_churn_flag_conflict"].to_dict() == {"A1": True, "A2": True}
    assert sub.loc["S3", "q_duplicate_of"] == "S2" and not sub.loc["S2", "q_is_duplicate"]
    assert sub.loc["S1", "q_upgrade_and_downgrade"]
    assert sub.loc[["S1", "S2", "S3"], "q_overlaps_other_subscription"].all()
    assert not sub.loc["S4", "q_overlaps_other_subscription"]

    assert fu.index.is_unique
    assert fu["q_usage_id_reused"].tolist() == [True, True, False, False]
    assert fu.loc["UR-00001", ["q_before_account_signup", "q_before_subscription_start"]].all()
    assert fu.loc["UR-00004", "q_after_subscription_end"]
    assert fu.loc["UR-00003", "q_on_duplicate_subscription"]
    assert fu["account_id"].tolist() == ["A1", "A1", "A1", "A1"]

    assert tk.loc["T1", "q_before_account_signup"] and not tk.loc["T2", "q_before_account_signup"]
    assert pd.isna(tk.loc["T1", "satisfaction_score"]) and tk.loc["T2", "satisfaction_score"] == 4

    assert ce["event_seq"].to_dict() == {"C1": 1, "C2": 2}
    assert ce.loc["C1", "q_reactivation_on_first_event"]
    assert ce.loc["C2", "q_not_reactivation_on_later_event"]
    assert ce["q_feedback_matches_reason"].tolist() == [True, False]
    assert ce.loc["C1", "q_days_to_nearest_subscription_end"] == 0


def test_no_row_lost_and_original_values_kept(raw_dir):
    raw = clean_data.read_raw(raw_dir)
    tables, _ = clean_data.clean({t: df.copy() for t, df in raw.items()})
    for name, df in raw.items():
        assert len(tables[name]) == len(df)
        # Tipos podem ser normalizados (ex.: satisfaction_score float -> Int64); valores não.
        pd.testing.assert_frame_equal(tables[name][df.columns], df, check_dtype=False)


def test_originals_untouched_and_build_is_deterministic(raw_dir, tmp_path):
    before = file_hashes(raw_dir)
    first = run_build(raw_dir, tmp_path / "a")
    second = run_build(raw_dir, tmp_path / "b")

    assert file_hashes(raw_dir) == before
    assert first == second
    assert file_hashes(tmp_path / "a" / "clean") == file_hashes(tmp_path / "b" / "clean")


def test_load_clean_round_trips_types_and_values(raw_dir, tmp_path):
    run_build(raw_dir, tmp_path)
    tables, _ = cleaned(raw_dir)
    for name, df in tables.items():
        loaded = clean_data.load_clean(name, tmp_path / "clean", tmp_path / "quality" / "derived_manifest.json")
        pd.testing.assert_frame_equal(loaded, df)


def test_checks_status_ok_only_when_nothing_found(raw_dir):
    _, checks = cleaned(raw_dir)
    assert all((c["status"] == "ok") == (c["n"] == 0) for c in checks if c["id"] != "T-07")


@pytest.mark.skipif(raw_data.check(raw_data.RAW_DIR, raw_data.load_manifest()["files"]) != [],
                    reason="originais ausentes; rode raw_data.py fetch")
def test_real_data_matches_audit_numbers(tmp_path):
    manifest = clean_data.build(raw_data.RAW_DIR, tmp_path / "clean", tmp_path / "q", tmp_path / "r.md")
    rows = {t: spec["rows"] for t, spec in manifest["tables"].items()}
    assert rows == {"accounts": 500, "subscriptions": 5000, "feature_usage": 25000,
                    "support_tickets": 2000, "churn_events": 600}
    n = pd.read_csv(tmp_path / "q" / "checks.csv").set_index("id")["n"].to_dict()
    assert {k: n[k] for k in ["A-04", "S-03", "U-01", "U-05", "U-06", "T-03", "C-05", "C-06", "C-11"]} == {
        "A-04": 312, "S-03": 4, "U-01": 42, "U-05": 13198, "U-06": 19142,
        "T-03": 1077, "C-05": 26, "C-06": 213, "C-11": 352}
    assert raw_data.check(raw_data.RAW_DIR, raw_data.load_manifest()["files"]) == []
