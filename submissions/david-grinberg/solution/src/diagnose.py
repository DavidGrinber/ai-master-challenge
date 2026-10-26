"""Diagnóstico e teste das hipóteses H01–H09 (DAV-184), conforme o pré-registro EXP-001.

Uso, a partir de submissions/david-grinberg/ (depois de clean_data.py e analytic_base.py):
    python solution/src/diagnose.py

Saídas: solution/outputs/diagnosis/*.csv e docs/hypotheses-results.md (gerado).
Comparações de features e segmentos usam só desenvolvimento e validação; os cortes do
teste final (2024-09-30 a 2024-11-30) ficam reservados para a DAV-189.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import analytic_base as ab
import clean_data

OUT_DIR = clean_data.SUB_DIR / "solution" / "outputs" / "diagnosis"
RESULTS = clean_data.SUB_DIR / "docs" / "hypotheses-results.md"
SEED = 20261026
LABEL = "churn_next_30d"
PARTS = {"desenvolvimento": ("2023-01-31", "2024-05-31"), "validação": ("2024-06-30", "2024-08-31")}
TEST = ("2024-09-30", "2024-11-30")
B_RATE, B_AUC = 1000, 300
NULL_LOG_RR, NULL_AUC = 0.1, 0.03
FEEDBACK_REASONS = clean_data.FEEDBACK_REASONS


# --- entradas -------------------------------------------------------------------------

def load_inputs() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], pd.Timestamp]:
    spec = json.loads((ab.OUT_DIR / "base_manifest.json").read_text(encoding="utf-8"))
    snaps = clean_data.read_typed(ab.PROCESSED_DIR / "snapshots.csv", spec["tables"]["snapshots"]["columns"])
    tables = {t: clean_data.load_clean(t) for t in clean_data.TABLES}
    return snaps, tables, pd.Timestamp(spec["data_end"])


def add_signals(snaps: pd.DataFrame, fu: pd.DataFrame) -> pd.DataFrame:
    """Colunas de diagnóstico derivadas só de informação até t (janelas extras de H01 inclusive)."""
    extra = []
    for t, grp in snaps.groupby("cutoff_date"):
        ids = grp["account_id"].to_numpy()

        def window(days, skip=0):
            w = ab._window(fu, "usage_date", t, days, skip)
            return w.groupby("account_id")["usage_count"].sum().reindex(ids).fillna(0).to_numpy()

        extra.append(pd.DataFrame({"account_id": ids, "cutoff_date": t,
                                   "usage_count_7d": window(7), "usage_count_prev_7d": window(7, 7),
                                   "usage_count_14d": window(14), "usage_count_prev_14d": window(14, 14)}))
    s = snaps.merge(pd.concat(extra), on=["account_id", "cutoff_date"], how="left", validate="one_to_one")
    for w in (7, 14, 30):
        cur, prev = f"usage_count_{w}d", f"usage_count_prev_{w}d"
        s[f"rel_drop_{w}d"] = ((s[prev] - s[cur]) / s[prev]).where(s[prev] > 0)
        s[f"abs_drop_{w}d"] = s[prev] - s[cur]
    s["error_rate_30d"] = (s["errors_30d"] / s["usage_count_30d"]).where(s["usage_count_30d"] > 0)
    s["has_ticket_90d"] = s["tickets_90d"] > 0
    s["neg_satisfaction_90d"] = -s["mean_satisfaction_90d"].astype(float)
    s["mean_resolution_hours_90d"] = s["mean_resolution_hours_90d"].astype(float)
    s["tenure_band"] = pd.cut(s["tenure_days"], [-1, 179, 364, 10**6], labels=["<180d", "180-364d", ">=365d"]).astype(str)
    s["trial_active"] = s["n_active_trial_subs"] > 0
    s["annual_majority"] = s["share_active_annual"] >= 0.5
    s["any_no_autorenew"] = s["n_active_no_autorenew"] > 0
    return s


def part(s: pd.DataFrame, name: str) -> pd.DataFrame:
    lo, hi = PARTS[name]
    return s[s["cutoff_date"].between(lo, hi) & s[LABEL].notna()].copy()


# --- estatística ----------------------------------------------------------------------

def _weights(df: pd.DataFrame, b: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Bootstrap de Poisson agrupado por conta: um peso por conta e réplica."""
    codes, uniques = pd.factorize(df["account_id"])
    return codes, np.random.default_rng(seed).poisson(1.0, size=(b, len(uniques)))


def _ci(values: np.ndarray) -> tuple[float, float]:
    """IC 95% percentil. Réplicas 0/0 são descartadas; com razões infinitas (grupo pequeno sem
    positivos na réplica) usa o percentil mais próximo, que devolve limite ilimitado em vez de NaN."""
    v = values[~np.isnan(values)]
    method = "nearest" if np.isinf(v).any() else "linear"
    lo, hi = np.percentile(v, [2.5, 97.5], method=method)
    return float(lo), float(hi)


def rate_contrast(df: pd.DataFrame, mask: pd.Series, b: int = B_RATE, seed: int = SEED) -> dict | None:
    """Taxa de churn no grupo e no restante, razão de risco e IC 95%."""
    y = df[LABEL].astype(bool).to_numpy().astype(float)
    m = mask.to_numpy(dtype=bool)
    if m.sum() == 0 or (~m).sum() == 0:
        return None
    codes, w = _weights(df, b, seed)
    a = w.shape[1]
    pos_g = np.bincount(codes[m], weights=y[m], minlength=a)
    n_g = np.bincount(codes[m], minlength=a).astype(float)
    pos_r = np.bincount(codes[~m], weights=y[~m], minlength=a)
    n_r = np.bincount(codes[~m], minlength=a).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = ((w @ pos_g) / (w @ n_g)) / ((w @ pos_r) / (w @ n_r))
    lo, hi = _ci(ratio)
    rate_g, rate_r = pos_g.sum() / n_g.sum(), pos_r.sum() / n_r.sum()
    return {"n": int(n_g.sum()), "accounts": int((n_g > 0).sum()), "positives": int(pos_g.sum()), "rate": rate_g,
            "n_rest": int(n_r.sum()), "positives_rest": int(pos_r.sum()), "rate_rest": rate_r,
            "rr": rate_g / rate_r if rate_r else np.nan, "rr_lo": lo, "rr_hi": hi}


def auc_ci(df: pd.DataFrame, score: str, b: int = B_AUC, seed: int = SEED) -> dict | None:
    d = df[df[score].notna()]
    y = d[LABEL].astype(bool).to_numpy()
    x = d[score].astype(float).to_numpy()
    if y.all() or not y.any():
        return None
    codes, w = _weights(d, b, seed)
    boots = []
    for row in w:
        sw = row[codes]
        if sw[y].sum() and sw[~y].sum():
            boots.append(roc_auc_score(y, x, sample_weight=sw))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"n": len(d), "accounts": d["account_id"].nunique(), "positives": int(y.sum()),
            "auc": roc_auc_score(y, x), "auc_lo": lo, "auc_hi": hi}


def status(intervals: list[tuple[float, float]], kind: str, two_sided: bool = False) -> str:
    """Regra do EXP-001 aplicada a desenvolvimento e validação. Previsto: acima do nulo."""
    f = np.log if kind == "rr" else (lambda v: v - 0.5)
    tol = NULL_LOG_RR if kind == "rr" else NULL_AUC
    with np.errstate(divide="ignore"):
        lows = [f(lo) for lo, _ in intervals]
        highs = [f(hi) for _, hi in intervals]
    if all(lo > 0 for lo in lows):
        return "apoiada"
    if all(hi < 0 for hi in highs):
        return "apoiada (direção inversa)" if two_sided else "refutada (direção oposta)"
    if all(lo > -tol and hi < tol for lo, hi in zip(lows, highs)):
        return "refutada (efeito nulo)"
    return "inconclusiva"


# --- análises -------------------------------------------------------------------------

AUC_SIGNALS = [
    # (hipótese, coluna, descrição, principal?)
    ("H01", "rel_drop_30d", "queda relativa de uso 30d vs 30d anteriores (base > 0, tenure >= 60d)", True),
    ("H01", "rel_drop_14d", "queda relativa 14d vs 14d anteriores", False),
    ("H01", "rel_drop_7d", "queda relativa 7d vs 7d anteriores", False),
    ("H01", "abs_drop_30d", "queda absoluta de usage_count 30d", False),
    ("H01", "days_since_last_usage", "dias desde o último uso", False),
    ("H02", "neg_satisfaction_90d", "satisfação média baixa (fechados em 90d, com resposta)", True),
    ("H02", "mean_resolution_hours_90d", "tempo médio de resolução (90d)", False),
    ("H02", "mean_first_response_min_90d", "primeira resposta média (90d)", False),
    ("H02", "escalations_90d", "escalonamentos (90d)", False),
    ("H02", "tickets_urgent_high_90d", "tickets urgent/high (90d)", False),
    ("H02", "open_tickets", "tickets abertos no corte", False),
    ("H03", "error_rate_30d", "taxa de erro em 30d (erros / usos)", True),
    ("H03", "errors_90d", "erros em 90d", False),
    ("H03", "beta_rows_30d", "uso de feature beta em 30d", False),
]


def run_aucs(s: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for h, col, desc, primary in AUC_SIGNALS:
        for name in PARTS:
            d = part(s, name)
            if h == "H01" and col.startswith("rel_drop"):
                d = d[d["tenure_days"] >= 60]
            r = auc_ci(d, col)
            if r:
                rows.append({"hypothesis": h, "signal": col, "description": desc, "primary": primary, "part": name, **r})
    return pd.DataFrame(rows)


def run_h01_groups(s: pd.DataFrame) -> pd.DataFrame:
    """Base zero e contas novas separadas, como pede a DAV-185."""
    rows = []
    for name in PARTS:
        d = part(s, name)
        groups = {"base anterior zero (prev 30d = 0)": d["usage_count_prev_30d"] == 0,
                  "conta nova (tenure < 60d)": d["tenure_days"] < 60,
                  "nunca usou até t": d["usage_rows_to_date"] == 0}
        for label, mask in groups.items():
            r = rate_contrast(d, mask)
            if r:
                rows.append({"part": name, "group": label, **r})
    return pd.DataFrame(rows)


def run_h01_alerts(s: pd.DataFrame) -> pd.DataFrame:
    """Regra 'queda relativa >= limiar': limiar escolhido por F1 no desenvolvimento, avaliado na validação."""
    def evaluate(d, thr):
        alert = d["rel_drop_30d"].fillna(-np.inf) >= thr
        y = d[LABEL].astype(bool)
        tp = int((alert & y).sum())
        prec = tp / alert.sum() if alert.sum() else np.nan
        rec = tp / y.sum() if y.sum() else np.nan
        f1 = 2 * prec * rec / (prec + rec) if prec and rec else 0.0
        months = d["cutoff_date"].nunique()
        return {"alerts": int(alert.sum()), "alerts_per_month": alert.sum() / months, "true_alerts": tp,
                "precision": prec, "recall": rec, "f1": f1, "prevalence": y.mean(), "lift": prec / y.mean() if y.mean() else np.nan}
    dev, val = part(s, "desenvolvimento"), part(s, "validação")
    grid = [round(x, 2) for x in np.arange(0.1, 1.0, 0.1)] + [1.0]
    dev_rows = [{"part": "desenvolvimento", "threshold": thr, **evaluate(dev, thr)} for thr in grid]
    best = max(dev_rows, key=lambda r: r["f1"])["threshold"]
    return pd.DataFrame(dev_rows + [{"part": "validação (limiar do desenvolvimento)", "threshold": best, **evaluate(val, best)}])


SEGMENTS = {
    "industry": "indústria", "referral_source": "canal de aquisição", "plan_tier_initial": "plano inicial",
    "country": "país", "tenure_band": "tempo de casa", "trial_active": "trial ativo",
    "annual_majority": "maioria das assinaturas anual", "any_no_autorenew": "alguma assinatura sem auto-renew",
    "has_ticket_90d": "algum ticket em 90d",
}


def run_segments(s: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, desc in SEGMENTS.items():
        for name in PARTS:
            d = part(s, name)
            for level in sorted(d[col].astype(str).unique()):
                r = rate_contrast(d, d[col].astype(str) == level)
                if r:
                    mrr = d.loc[d[col].astype(str) == level]
                    rows.append({"segment": col, "description": desc, "level": level, "part": name, **r,
                                 "mrr_exposed": int(mrr["mrr_active"].sum()),
                                 "mrr_churned": int(mrr.loc[mrr[LABEL].astype(bool), "mrr_active"].sum())})
    return pd.DataFrame(rows)


def run_h05(s: pd.DataFrame, fu: pd.DataFrame) -> pd.DataFrame:
    """Uso total e por conta elegível por trimestre (descritivo, período todo)."""
    q = fu.assign(quarter=fu["usage_date"].dt.to_period("Q").astype(str)).groupby("quarter")
    out = pd.DataFrame({"usage_rows": q.size(), "usage_count": q["usage_count"].sum()})
    sq = s.assign(quarter=s["cutoff_date"].dt.to_period("Q").astype(str)).groupby("quarter")
    out["avg_eligible_accounts"] = sq.size() / 3
    out["usage_30d_total_eligible"] = sq["usage_count_30d"].sum() / 3
    out["usage_30d_per_eligible_account"] = sq["usage_count_30d"].mean()
    return out.reset_index()


def run_h06_h04_status(seg: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (col, level), g in seg.groupby(["segment", "level"]):
        if set(g["part"]) != set(PARTS):
            continue
        g = g.set_index("part").loc[list(PARTS)]
        rows.append({"segment": col, "level": level,
                     "status": status(list(zip(g["rr_lo"], g["rr_hi"])), "rr", two_sided=True)})
    return pd.DataFrame(rows)


def run_h07(tables: dict[str, pd.DataFrame]) -> dict | None:
    acc, fu, ce = tables["accounts"], tables["feature_usage"], tables["churn_events"]
    a = acc[acc["signup_date"] <= pd.Timestamp("2024-02-29")][["account_id", "signup_date"]].copy()
    e = ce.merge(a, on="account_id")
    days = (e["churn_date"] - e["signup_date"]).dt.days
    early_churn = set(e.loc[days <= 90, "account_id"])
    later = set(e.loc[(days > 90) & (days <= 270), "account_id"])
    a = a[~a["account_id"].isin(early_churn)]
    u = fu.merge(a, on="account_id")
    du = (u["usage_date"] - u["signup_date"]).dt.days
    early = u[(du >= 0) & (du <= 90)].groupby("account_id").size()
    a["neg_early_usage_rows"] = -a["account_id"].map(early).fillna(0)
    a[LABEL] = a["account_id"].isin(later)
    r = auc_ci(a, "neg_early_usage_rows")
    return {"hypothesis": "H07", "excluded_early_churn": len(early_churn), **(r or {})}


def run_h08(s: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    acc, ce = tables["accounts"], tables["churn_events"]
    defs = pd.DataFrame([
        {"definition": "accounts.churn_flag = True", "value": int(acc["churn_flag"].sum()), "denominator": len(acc)},
        {"definition": "contas com >= 1 evento em churn_events", "value": ce["account_id"].nunique(), "denominator": len(acc)},
        {"definition": "eventos de churn (total)", "value": len(ce), "denominator": len(acc)},
        {"definition": "contas com evento e churn_flag = False", "value": int((acc["has_churn_event"] & ~acc["churn_flag"]).sum()), "denominator": int(acc["has_churn_event"].sum())},
    ])
    labelled = s[s[LABEL].notna()].assign(quarter=s["cutoff_date"].dt.to_period("Q").astype(str))
    rows = []
    for qtr, g in labelled.groupby("quarter"):
        r = rate_contrast(labelled, labelled["quarter"] == qtr)
        churned = g.loc[g[LABEL].astype(bool), "mrr_active"].sum()
        rows.append({"quarter": qtr, "account_months": r["n"], "positives": r["positives"], "rate": r["rate"],
                     "mrr_rate": churned / g["mrr_active"].sum(), "in_reserved_test": bool(g["cutoff_date"].min() >= pd.Timestamp(TEST[0]))})
    return defs, pd.DataFrame(rows)


def _mean_ratio(df: pd.DataFrame, mask: pd.Series, col: str, b: int = B_RATE, seed: int = SEED) -> dict:
    x = df[col].astype(float).to_numpy()
    ok = ~np.isnan(x)
    m = mask.to_numpy(dtype=bool)
    codes, w = _weights(df, b, seed)
    a = w.shape[1]
    sums = lambda sel: (np.bincount(codes[sel], weights=x[sel], minlength=a), np.bincount(codes[sel], minlength=a).astype(float))
    sg, ng = sums(m & ok)
    sr, nr = sums(~m & ok)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = ((w @ sg) / (w @ ng)) / ((w @ sr) / (w @ nr))
    lo, hi = _ci(ratio)
    point = (sg.sum() / ng.sum()) / (sr.sum() / nr.sum())
    return {"n_group": int(ng.sum()), "mean_group": sg.sum() / ng.sum(), "mean_rest": sr.sum() / nr.sum(),
            "ratio": point, "ratio_lo": lo, "ratio_hi": hi}


H09_LINKS = [  # motivo declarado -> comportamento esperado nos 90 dias antes do evento
    ("support", "tickets_90d", "mais tickets"),
    ("support", "mean_satisfaction_90d", "satisfação menor", -1),
    ("features", "distinct_features_30d", "menos features usadas", -1),
    ("features", "usage_count_30d", "menos uso", -1),
    ("pricing", "mrr_active", "MRR maior"),
    ("budget", "mrr_active", "MRR maior"),
]


def run_h09(tables: dict[str, pd.DataFrame], end: pd.Timestamp) -> tuple[dict, pd.DataFrame]:
    ce = tables["churn_events"]
    comparable = ce[ce["feedback_text"].notna() & (ce["reason_code"] != "unknown")]
    match = lambda reasons, feedback: np.mean([r in FEEDBACK_REASONS[f] for r, f in zip(reasons, feedback)])
    observed = match(comparable["reason_code"], comparable["feedback_text"])
    rng = np.random.default_rng(SEED)
    perm = np.array([match(rng.permutation(comparable["reason_code"].to_numpy()), comparable["feedback_text"]) for _ in range(2000)])
    agreement = {"comparable": len(comparable), "agree": int(round(observed * len(comparable))), "observed": observed,
                 "chance_mean": perm.mean(), "p_above_chance": (perm >= observed).mean()}

    frames = []
    for d, grp in ce.groupby("churn_date"):
        snap = ab.snapshot_at(tables, d - pd.Timedelta(days=1), end)
        frames.append(snap[snap["account_id"].isin(grp["account_id"])].merge(
            grp[["account_id", "churn_event_id", "reason_code"]], on="account_id"))
    pre = pd.concat(frames, ignore_index=True)
    rows = []
    for link in H09_LINKS:
        reason, col, desc = link[:3]
        sign = link[3] if len(link) > 3 else 1
        r = _mean_ratio(pre, pre["reason_code"] == reason, col)
        expected_met = (r["ratio_lo"] > 1) if sign > 0 else (r["ratio_hi"] < 1)
        rows.append({"reason": reason, "behavior": col, "expected": desc, **r, "expected_met": bool(expected_met)})
    agreement["events_with_pre_snapshot"] = len(pre)
    agreement["events_total"] = len(ce)
    return agreement, pd.DataFrame(rows)


def run_h10(s: pd.DataFrame, tables: dict[str, pd.DataFrame], end: pd.Timestamp) -> dict:
    """H10 (exploratória, 2026-10-26 19:14): o churn segue o mecanismo do gerador do dataset?

    Mecanismo testado: cada conta recebe ~k eventos em datas uniformes entre o signup e o fim
    dos dados. O 'risco do gerador' usa o fim dos dados, que não é conhecido em t: serve só
    para diagnóstico e é proibido como feature.
    """
    acc, ce = tables["accounts"], tables["churn_events"]
    k = len(ce) / len(acc)
    life = (end - acc.set_index("account_id")["signup_date"]).dt.days.clip(lower=1)
    a = pd.DataFrame({"life_days": life, "n_events": ce.groupby("account_id").size()}).fillna({"n_events": 0})
    a["lifetime"] = pd.cut(a["life_days"], [0, 180, 365, 545, 731], labels=["<180d", "180-364d", "365-544d", "545-730d"])
    cohorts = a.groupby("lifetime", observed=True).agg(accounts=("n_events", "size"), events_per_account=("n_events", "mean"),
                                                       mean_life_days=("life_days", "mean")).reset_index()
    cohorts["events_per_account_month"] = cohorts["events_per_account"] / (cohorts["mean_life_days"] / 30.44)
    e = ce.merge(a, left_on="account_id", right_index=True)
    signup = e["account_id"].map(acc.set_index("account_id")["signup_date"])
    position = (e["churn_date"] - signup).dt.days / e["life_days"]
    s = s.assign(generator_hazard=30 / s["account_id"].map(life), neg_tenure=-s["tenure_days"])
    aucs = []
    for name in PARTS:
        d = part(s, name)
        for col, desc in (("generator_hazard", "risco do gerador: 30 / dias entre signup e fim dos dados (não é feature)"),
                          ("neg_tenure", "tempo de casa curto"), ("prior_churn_events", "churns anteriores")):
            r = auc_ci(d, col)
            if r:
                aucs.append({"signal": col, "description": desc, "part": name, **r})
    lab = s[s[LABEL].notna() & s["cutoff_date"].between(PARTS["desenvolvimento"][0], PARTS["validação"][1])]
    curve = lab.groupby("cutoff_date").apply(lambda g: pd.Series({
        "eligible": len(g), "observed": int(g[LABEL].astype(bool).sum()),
        "predicted": float((1 - np.exp(-k * 30 / g["account_id"].map(life))).sum())}), include_groups=False).reset_index()
    curve["observed_rate"] = curve["observed"] / curve["eligible"]
    curve["predicted_rate"] = curve["predicted"] / curve["eligible"]
    return {"k": k, "cohorts": cohorts, "position_quantiles": position.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).round(3).to_dict(),
            "aucs": pd.DataFrame(aucs), "curve": curve,
            "curve_corr": float(np.corrcoef(curve["observed_rate"], curve["predicted_rate"])[0, 1])}


ATTENTION_COLUMNS = ["account_id", "industry", "plan_tier_initial", "referral_source", "tenure_days", "mrr_active",
                     "n_active_subs", "prior_churn_events", "tickets_90d", "open_tickets", "usage_count_30d"]


def run_accounts(s: pd.DataFrame, end: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    """Carteira atual no único segmento com risco maior nas duas partes (tempo de casa < 180 dias), por MRR.

    Não é um score: o risco do segmento é compatível com o mecanismo do gerador (H10) e a previsão
    validada fica para a DAV-189.
    """
    now = s[s["cutoff_date"] == end]
    new = now[now["tenure_days"] < 180].sort_values(["mrr_active", "account_id"], ascending=[False, True])
    summary = {"date": str(end.date()), "accounts_now": len(now), "new_accounts": len(new), "new_mrr": int(new["mrr_active"].sum()),
               "total_mrr": int(now["mrr_active"].sum())}
    return new[ATTENTION_COLUMNS], summary


# --- relatório ------------------------------------------------------------------------

def _fmt(v, pct=False, digits=2):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.1%}" if pct else f"{v:.{digits}f}"


def hypothesis_table(aucs: pd.DataFrame, seg: pd.DataFrame, seg_status: pd.DataFrame, h05: pd.DataFrame,
                     h07: dict, agreement: dict, links: pd.DataFrame, h10: dict) -> pd.DataFrame:
    def auc_status(h):
        g = aucs[(aucs["hypothesis"] == h) & aucs["primary"]].set_index("part").loc[list(PARTS)]
        return status(list(zip(g["auc_lo"], g["auc_hi"])), "auc"), "; ".join(
            f"{p}: AUC {_fmt(r.auc)} [{_fmt(r.auc_lo)}, {_fmt(r.auc_hi)}]" for p, r in g.iterrows())

    def rr_status(col, level, two_sided=False):
        g = seg[(seg["segment"] == col) & (seg["level"] == level)].set_index("part").loc[list(PARTS)]
        return status(list(zip(g["rr_lo"], g["rr_hi"])), "rr", two_sided), "; ".join(
            f"{p}: RR {_fmt(r.rr)} [{_fmt(r.rr_lo)}, {_fmt(r.rr_hi)}]" for p, r in g.iterrows())

    rows = []
    st, ev = auc_status("H01"); rows.append(("H01", st, ev))
    st_t, ev_t = rr_status("has_ticket_90d", "True")
    st_s, ev_s = auc_status("H02")
    rows.append(("H02", f"ticket: {st_t}; satisfação: {st_s}", f"ticket em 90d — {ev_t} | satisfação — {ev_s}"))
    st, ev = auc_status("H03"); rows.append(("H03", st, ev))
    h04 = seg_status[~seg_status["segment"].isin(["annual_majority", "any_no_autorenew", "has_ticket_90d"])]
    hits = h04[h04["status"].str.startswith("apoiada")]
    rows.append(("H04", "apoiada" if len(hits) else "inconclusiva",
                 f"{len(hits)} de {len(h04)} níveis de segmento com IC excluindo RR = 1 nas duas partes"
                 + (": " + ", ".join(f"{r.segment}={r.level} ({r.status})" for r in hits.itertuples()) if len(hits) else "")))
    first, last = h05.iloc[0], h05.iloc[-1]
    rows.append(("H05", "avaliar (descritivo)", f"uso total {int(first.usage_count)} ({first.quarter}) → {int(last.usage_count)} ({last.quarter}); "
                 f"uso 30d por conta elegível {_fmt(first.usage_30d_per_eligible_account, digits=1)} → {_fmt(last.usage_30d_per_eligible_account, digits=1)}"))
    st, ev = rr_status("annual_majority", "True", two_sided=True); rows.append(("H06", st, "maioria anual vs restante — " + ev))
    st = "inconclusiva" if not h07.get("auc") else status([(h07["auc_lo"], h07["auc_hi"])] * 2, "auc")
    rows.append(("H07", st, f"AUC {_fmt(h07.get('auc'))} [{_fmt(h07.get('auc_lo'))}, {_fmt(h07.get('auc_hi'))}], n = {h07.get('n')}, positivos = {h07.get('positives')}"))
    rows.append(("H08", "avaliar (descritivo)", "ver definições e tendência trimestral"))
    met = int(links["expected_met"].sum())
    h09 = "apoiada" if agreement["p_above_chance"] >= 0.05 and met < len(links) else "inconclusiva"
    rows.append(("H09", h09, f"motivo × feedback concordam {agreement['agree']}/{agreement['comparable']} ({_fmt(agreement['observed'], True)}; "
                 f"acaso {_fmt(agreement['chance_mean'], True)}; p acima do acaso = {_fmt(agreement['p_above_chance'], digits=3)}); "
                 f"{met} de {len(links)} vínculos motivo → comportamento confirmados"))
    g = h10["aucs"][h10["aucs"]["signal"] == "generator_hazard"].set_index("part").loc[list(PARTS)]
    rows.append(("H10 (exploratória)", status(list(zip(g["auc_lo"], g["auc_hi"])), "auc"),
                 "mecanismo do gerador — " + "; ".join(f"{p}: AUC {_fmt(r.auc)} [{_fmt(r.auc_lo)}, {_fmt(r.auc_hi)}]" for p, r in g.iterrows())
                 + f"; eventos previstos {h10['curve']['predicted'].sum():.1f} vs observados {int(h10['curve']['observed'].sum())}"))
    return pd.DataFrame(rows, columns=["hypothesis", "status_rule", "evidence"])


def render(status_tbl, aucs, h01g, alerts, seg, h05, h07, defs, trend, agreement, links, h10, attention, att) -> str:
    L = ["# Resultados das hipóteses (EXP-001)", "",
         "> Gerado por `solution/src/diagnose.py`; não editar à mão. Pré-registro: [EXP-001](../process-log/experiments/EXP-001-hipoteses-pre-registro.md). "
         "Interpretação: [diagnosis-findings.md](diagnosis-findings.md).", "",
         f"Taxa = eventos de churn em (t, t+30] por conta-mês elegível. IC 95% por bootstrap de Poisson agrupado por conta. "
         f"Desenvolvimento: cortes {PARTS['desenvolvimento'][0]} a {PARTS['desenvolvimento'][1]}; validação: {PARTS['validação'][0]} a {PARTS['validação'][1]}. "
         f"O teste final ({TEST[0]} a {TEST[1]}) não foi usado nas comparações.", "",
         "## Status pela regra pré-registrada", "", "| H | Status (regra) | Evidência principal |", "|---|---|---|"]
    L += [f"| {r.hypothesis} | {r.status_rule} | {r.evidence} |" for r in status_tbl.itertuples()]
    L += ["", "## Sinais contínuos (AUC; 0,5 = sem sinal)", "", "| H | Sinal | Parte | n | positivos | AUC [IC 95%] | Principal |", "|---|---|---|---:|---:|---|---|"]
    L += [f"| {r.hypothesis} | {r.description} | {r.part} | {r.n} | {r.positives} | {_fmt(r.auc)} [{_fmt(r.auc_lo)}, {_fmt(r.auc_hi)}] | {'sim' if r.primary else ''} |" for r in aucs.itertuples()]
    L += ["", "## H01 — grupos separados", "", "| Parte | Grupo | conta-meses | positivos | taxa | taxa do restante | RR [IC 95%] |", "|---|---|---:|---:|---:|---:|---|"]
    L += [f"| {r.part} | {r.group} | {r.n} | {r.positives} | {_fmt(r.rate, True)} | {_fmt(r.rate_rest, True)} | {_fmt(r.rr)} [{_fmt(r.rr_lo)}, {_fmt(r.rr_hi)}] |" for r in h01g.itertuples()]
    L += ["", "## H01 — regra de alerta por queda relativa", "", "| Parte | Limiar | Alertas/mês | Precisão | Recall | Prevalência | Lift |", "|---|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {r.part} | {_fmt(r.threshold, digits=1)} | {_fmt(r.alerts_per_month, digits=1)} | {_fmt(r.precision, True)} | {_fmt(r.recall, True)} | {_fmt(r.prevalence, True)} | {_fmt(r.lift)} |" for r in alerts.itertuples()]
    L += ["", "## Segmentos (cada nível contra o restante)", "", "| Segmento | Nível | Parte | conta-meses | contas | positivos | taxa | RR [IC 95%] | MRR exposto | MRR churn |", "|---|---|---|---:|---:|---:|---:|---|---:|---:|"]
    L += [f"| {r.description} | {r.level} | {r.part} | {r.n} | {r.accounts} | {r.positives} | {_fmt(r.rate, True)} | {_fmt(r.rr)} [{_fmt(r.rr_lo)}, {_fmt(r.rr_hi)}] | {r.mrr_exposed} | {r.mrr_churned} |" for r in seg.itertuples()]
    L += ["", "## H05 — uso por trimestre (período todo)", "", "| Trimestre | Linhas de uso (todas) | usage_count (todas) | Contas elegíveis (média) | usage_count 30d das elegíveis (média mensal) | por conta elegível |", "|---|---:|---:|---:|---:|---:|"]
    L += [f"| {r.quarter} | {r.usage_rows} | {r.usage_count} | {_fmt(r.avg_eligible_accounts, digits=0)} | {_fmt(r.usage_30d_total_eligible, digits=0)} | {_fmt(r.usage_30d_per_eligible_account, digits=1)} |" for r in h05.itertuples()]
    L += ["", "## H07 — ativação inicial", "", f"Contas com signup até 2024-02-29, sem churn nos primeiros 90 dias ({h07.get('excluded_early_churn')} excluídas). "
          f"Sinal: menos linhas de uso nos 90 dias após o signup. Desfecho: churn entre os dias 91 e 270. "
          f"n = {h07.get('n')}, positivos = {h07.get('positives')}, AUC {_fmt(h07.get('auc'))} [{_fmt(h07.get('auc_lo'))}, {_fmt(h07.get('auc_hi'))}]."]
    L += ["", "## H08 — o que é \"churn\" depende da fonte", "", "| Definição | Valor | Denominador |", "|---|---:|---:|"]
    L += [f"| {r.definition} | {r.value} | {r.denominator} |" for r in defs.itertuples()]
    L += ["", "| Trimestre | conta-meses | positivos | taxa mensal | taxa por MRR | teste reservado |", "|---|---:|---:|---:|---:|---|"]
    L += [f"| {r.quarter} | {r.account_months} | {r.positives} | {_fmt(r.rate, True)} | {_fmt(r.mrr_rate, True)} | {'sim' if r.in_reserved_test else ''} |" for r in trend.itertuples()]
    L += ["", "## H09 — motivos declarados", "",
          f"Motivo × feedback: {agreement['agree']} de {agreement['comparable']} concordam ({_fmt(agreement['observed'], True)}); "
          f"esperado pelo acaso {_fmt(agreement['chance_mean'], True)}; p (acima do acaso, 2.000 permutações) = {_fmt(agreement['p_above_chance'], digits=3)}. "
          f"Comportamento nos 90 dias antes do evento: {agreement['events_with_pre_snapshot']} de {agreement['events_total']} eventos com conta elegível na véspera.", "",
          "| Motivo | Comportamento | Esperado | n | média no motivo | média nos demais | razão [IC 95%] | confirmado |", "|---|---|---|---:|---:|---:|---|---|"]
    L += [f"| {r.reason} | {r.behavior} | {r.expected} | {r.n_group} | {_fmt(r.mean_group)} | {_fmt(r.mean_rest)} | {_fmt(r.ratio)} [{_fmt(r.ratio_lo)}, {_fmt(r.ratio_hi)}] | {'sim' if r.expected_met else 'não'} |" for r in links.itertuples()]
    L += ["", "## H10 (exploratória) — o churn segue o mecanismo do gerador do dataset?", "",
          f"Hipótese surgida ao ver os resultados (2026-10-26 19:14): cada conta recebe ~{h10['k']:.2f} eventos em datas uniformes entre o signup e o fim dos dados. "
          f"O 'risco do gerador' usa o fim dos dados, que não é conhecido em t: serve para diagnóstico e é proibido como feature.", "",
          "| Tempo de vida até o fim dos dados | Contas | Eventos por conta | Vida média (dias) | Eventos por conta-mês |", "|---|---:|---:|---:|---:|"]
    L += [f"| {r.lifetime} | {r.accounts} | {_fmt(r.events_per_account)} | {_fmt(r.mean_life_days, digits=0)} | {_fmt(r.events_per_account_month, digits=3)} |" for r in h10["cohorts"].itertuples()]
    q = h10["position_quantiles"]
    L += ["", "Posição do evento entre o signup (0) e o fim dos dados (1), quantis 10/25/50/75/90%: " + " / ".join(_fmt(q[k]) for k in sorted(q)) + " (uniforme = 0,10 / 0,25 / 0,50 / 0,75 / 0,90).", "",
          "| Sinal | Parte | n | positivos | AUC [IC 95%] |", "|---|---|---:|---:|---|"]
    L += [f"| {r.description} | {r.part} | {r.n} | {r.positives} | {_fmt(r.auc)} [{_fmt(r.auc_lo)}, {_fmt(r.auc_hi)}] |" for r in h10["aucs"].itertuples()]
    L += ["", f"Curva por corte (desenvolvimento + validação): correlação entre taxa observada e prevista pelo mecanismo = {_fmt(h10['curve_corr'])}.", "",
          "| Corte | Elegíveis | Observados | Previstos | Taxa observada | Taxa prevista |", "|---|---:|---:|---:|---:|---:|"]
    L += [f"| {r.cutoff_date.date()} | {r.eligible:.0f} | {r.observed:.0f} | {_fmt(r.predicted, digits=1)} | {_fmt(r.observed_rate, True)} | {_fmt(r.predicted_rate, True)} |" for r in h10["curve"].itertuples()]
    L += ["", f"## Carteira em {att['date']} no segmento com risco maior (tempo de casa < 180 dias)", "",
          f"{att['new_accounts']} de {att['accounts_now']} contas, MRR {att['new_mrr']} de {att['total_mrr']} ({_fmt(att['new_mrr'] / att['total_mrr'], True)}). "
          "Ordenadas por MRR. **Não é score de risco**: o segmento é o único com RR acima de 1 nas duas partes, mas o efeito é compatível com o mecanismo do gerador (H10). "
          "Lista completa em `solution/outputs/diagnosis/accounts_attention.csv`; abaixo, as 15 de maior MRR.", "",
          "| Conta | Indústria | Plano inicial | Dias de casa | MRR | Assinaturas ativas | Churns anteriores | Tickets 90d |", "|---|---|---|---:|---:|---:|---:|---:|"]
    L += [f"| {r.account_id} | {r.industry} | {r.plan_tier_initial} | {r.tenure_days} | {r.mrr_active} | {r.n_active_subs} | {r.prior_churn_events} | {r.tickets_90d} |" for r in attention.head(15).itertuples()]
    return "\n".join(L) + "\n"


def main() -> int:
    snaps, tables, end = load_inputs()
    s = add_signals(snaps, tables["feature_usage"])
    aucs = run_aucs(s)
    h01g = run_h01_groups(s)
    alerts = run_h01_alerts(s)
    seg = run_segments(s)
    seg_status = run_h06_h04_status(seg)
    h05 = run_h05(s, tables["feature_usage"])
    h07 = run_h07(tables)
    defs, trend = run_h08(s, tables)
    agreement, links = run_h09(tables, end)
    h10 = run_h10(s, tables, end)
    attention, att = run_accounts(s, end)
    status_tbl = hypothesis_table(aucs, seg, seg_status, h05, h07, agreement, links, h10)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in {"auc_signals": aucs, "h01_groups": h01g, "h01_alerts": alerts, "segments": seg,
                     "segment_status": seg_status, "h05_usage_quarterly": h05, "h08_definitions": defs,
                     "h08_trend": trend, "h09_links": links, "hypothesis_status": status_tbl,
                     "h10_cohorts": h10["cohorts"], "h10_aucs": h10["aucs"], "h10_curve": h10["curve"],
                     "accounts_attention": attention}.items():
        df.to_csv(OUT_DIR / f"{name}.csv", index=False, lineterminator="\n", float_format="%.6g")
    (OUT_DIR / "h07_h09_summary.json").write_text(json.dumps({"h07": h07, "h09_agreement": agreement, "accounts_attention": att, "h10": {"k": h10["k"], "position_quantiles": h10["position_quantiles"], "curve_corr": h10["curve_corr"]}}, indent=2, default=float) + "\n", encoding="utf-8")
    RESULTS.write_text(render(status_tbl, aucs, h01g, alerts, seg, h05, h07, defs, trend, agreement, links, h10, attention, att), encoding="utf-8")
    print(status_tbl.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
