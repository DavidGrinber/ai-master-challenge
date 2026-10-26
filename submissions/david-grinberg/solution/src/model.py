"""Modelo de churn (DAV-189), conforme o pré-registro EXP-002.

Uso, a partir de submissions/david-grinberg/ (depois de analytic_base.py):
    python solution/src/model.py

Saídas:
    solution/models/churn-lr-v1.joblib           (local, fora do Git; regenerado por este script)
    solution/models/model_meta.json              (versionado: versão, features, coeficientes, linhagem)
    solution/outputs/model/*.csv                 (versionado: seleção, avaliação, priorização, calibração)
    solution/outputs/scores/scores_<data>.csv    (versionado: carteira pontuada para o painel)
    docs/model-evaluation.md                     (versionado, gerado)

O teste (cortes 2024-09-30 a 2024-11-30) é avaliado uma única vez, depois de todas as escolhas.
"""
from __future__ import annotations

import hashlib
import json
import sys

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

import analytic_base as ab
import clean_data
import diagnose as dg

MODEL_DIR = clean_data.SUB_DIR / "solution" / "models"
OUT_DIR = clean_data.SUB_DIR / "solution" / "outputs" / "model"
SCORES_DIR = clean_data.SUB_DIR / "solution" / "outputs" / "scores"
EVALUATION = clean_data.SUB_DIR / "docs" / "model-evaluation.md"
VERSION = "churn-lr-v1"
LABEL = dg.LABEL
HORIZON_DAYS = 30
SEED = dg.SEED
B = 500
C_GRID = (0.01, 0.03, 0.1, 0.3, 1.0)
CAPACITIES = (0.10, 0.20)
SPLITS = {"treino": dg.PARTS["desenvolvimento"], "validação": dg.PARTS["validação"], "teste": dg.TEST}
CATEGORICAL = ["industry", "country", "referral_source", "plan_tier_initial"]
NOT_FEATURES = {"account_id", "cutoff_date", *(f"churn_next_{h}d" for h in ab.HORIZONS)}
FORBIDDEN = {"churn_flag", "is_trial", "seats", "reason_code", "feedback_text", "refund_amount_usd",
             "is_reactivation", "generator_hazard", "account_id", "cutoff_date"}
NUMERIC = [c for c in ab.SNAPSHOT_COLUMNS if c not in NOT_FEATURES and c not in CATEGORICAL]
FEATURES = NUMERIC + CATEGORICAL
assert not FORBIDDEN & set(FEATURES), "feature proibida no modelo"


# --- dados ----------------------------------------------------------------------------

def load_snapshots() -> tuple[pd.DataFrame, pd.Timestamp, str]:
    manifest_path = ab.OUT_DIR / "base_manifest.json"
    spec = json.loads(manifest_path.read_text(encoding="utf-8"))
    snaps = clean_data.read_typed(ab.PROCESSED_DIR / "snapshots.csv", spec["tables"]["snapshots"]["columns"])
    return snaps, pd.Timestamp(spec["data_end"]), hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def split(s: pd.DataFrame, *names: str) -> pd.DataFrame:
    mask = pd.Series(False, index=s.index)
    for name in names:
        lo, hi = SPLITS[name]
        mask |= s["cutoff_date"].between(lo, hi)
    return s[mask & s[LABEL].notna()].sort_values(["cutoff_date", "account_id"], ignore_index=True)


def X(df: pd.DataFrame) -> pd.DataFrame:
    out = df[FEATURES].copy()
    out[NUMERIC] = out[NUMERIC].astype(float)
    out[CATEGORICAL] = out[CATEGORICAL].astype(str)
    return out


def y(df: pd.DataFrame) -> np.ndarray:
    return df[LABEL].astype(bool).to_numpy()


# --- modelos --------------------------------------------------------------------------

def _preprocess() -> ColumnTransformer:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                        ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
                        ("scale", StandardScaler())])
    return ColumnTransformer([("num", numeric, NUMERIC),
                              ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)])


def make_lr(c: float) -> Pipeline:
    return Pipeline([("pre", _preprocess()), ("clf", LogisticRegression(C=c, max_iter=5000))])


def make_hgb() -> Pipeline:
    return Pipeline([("pre", _preprocess()),
                     ("clf", HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, random_state=SEED))])


def baselines(df: pd.DataFrame) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SEED)
    return {"B0 aleatório": rng.random(len(df)),
            "B1 tempo de casa curto": -df["tenure_days"].to_numpy(dtype=float),
            "B2 MRR": df["mrr_active"].to_numpy(dtype=float)}


# --- métricas -------------------------------------------------------------------------

def bootstrap(df: pd.DataFrame, scores: dict[str, np.ndarray], b: int = B) -> dict[str, dict]:
    """AP e ROC-AUC com réplicas pareadas (mesmos pesos por conta para todos os rankings)."""
    target = y(df)
    codes, w = dg._weights(df, b, SEED)
    keep = [row[codes] for row in w if row[codes][target].sum() and row[codes][~target].sum()]
    out = {}
    for name, x in scores.items():
        out[name] = {"ap": average_precision_score(target, x), "auc": roc_auc_score(target, x),
                     "ap_boot": np.array([average_precision_score(target, x, sample_weight=sw) for sw in keep]),
                     "auc_boot": np.array([roc_auc_score(target, x, sample_weight=sw) for sw in keep])}
    return out


def metric_rows(part: str, df: pd.DataFrame, res: dict[str, dict]) -> list[dict]:
    rows = []
    for name, r in res.items():
        ap_lo, ap_hi = np.percentile(r["ap_boot"], [2.5, 97.5])
        auc_lo, auc_hi = np.percentile(r["auc_boot"], [2.5, 97.5])
        rows.append({"part": part, "ranking": name, "rows": len(df), "accounts": df["account_id"].nunique(),
                     "positives": int(y(df).sum()), "prevalence": y(df).mean(), "ap": r["ap"], "ap_lo": ap_lo,
                     "ap_hi": ap_hi, "auc": r["auc"], "auc_lo": auc_lo, "auc_hi": auc_hi})
    return rows


def paired_diff(res: dict[str, dict], a: str, b: str, metric: str = "ap") -> dict:
    d = res[a][f"{metric}_boot"] - res[b][f"{metric}_boot"]
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"a": a, "b": b, "metric": metric, "diff": res[a][metric] - res[b][metric], "lo": lo, "hi": hi}


def prioritization(df: pd.DataFrame, score: np.ndarray, capacity: float, churn: pd.DataFrame) -> dict:
    """Top-K por corte (K = capacidade × elegíveis): precisão, recall, falsos alertas, MRR coberto, antecedência."""
    d = df.assign(_score=score)
    first = churn.groupby("account_id")["churn_date"].apply(lambda s: sorted(s))
    alerts = tp = positives = 0
    mrr_hit = mrr_all = 0.0
    leads = []
    for t, g in d.groupby("cutoff_date"):
        k = max(1, int(round(capacity * len(g))))
        top = g.sort_values(["_score", "account_id"], ascending=[False, True]).head(k)
        hit = top[top[LABEL].astype(bool)]
        alerts += k
        tp += len(hit)
        positives += int(g[LABEL].astype(bool).sum())
        mrr_hit += hit["mrr_active"].sum()
        mrr_all += g.loc[g[LABEL].astype(bool), "mrr_active"].sum()
        for acc in hit["account_id"]:
            nxt = next(c for c in first[acc] if c > t)
            leads.append((nxt - t).days)
    months = d["cutoff_date"].nunique()
    return {"capacity": capacity, "alerts_per_month": alerts / months, "true_alerts": tp,
            "false_alerts_per_month": (alerts - tp) / months, "precision": tp / alerts,
            "recall": tp / positives if positives else np.nan, "mrr_covered": mrr_hit / mrr_all if mrr_all else np.nan,
            "median_lead_days": float(np.median(leads)) if leads else np.nan}


def calibration(df: pd.DataFrame, prob: np.ndarray) -> tuple[pd.DataFrame, dict]:
    target = y(df)
    bins = pd.qcut(prob, 10, labels=False, duplicates="drop")
    table = pd.DataFrame({"decile": bins, "pred": prob, "obs": target}).groupby("decile").agg(
        rows=("obs", "size"), mean_pred=("pred", "mean"), observed=("obs", "mean")).reset_index()
    table["abs_error"] = (table["mean_pred"] - table["observed"]).abs()
    mean_pred, observed = prob.mean(), target.mean()
    summary = {"brier": brier_score_loss(target, prob), "brier_prevalence": brier_score_loss(target, np.full(len(target), observed)),
               "mean_pred": mean_pred, "observed": observed, "relative_gap": abs(mean_pred - observed) / observed,
               "max_decile_error": table["abs_error"].max()}
    summary["show_probability"] = bool(summary["relative_gap"] < 0.2 and summary["max_decile_error"] <= 0.05)
    return table, summary


# --- sinais por conta -----------------------------------------------------------------

def top_signals(pipe: Pipeline, df: pd.DataFrame, n: int = 3) -> list[str]:
    """Maiores contribuições positivas (coeficiente × valor padronizado) de cada conta, em texto."""
    pre, clf = pipe.named_steps["pre"], pipe.named_steps["clf"]
    contrib = pre.transform(X(df)) * clf.coef_[0]
    names = pre.get_feature_names_out()
    out = []
    for i, row in enumerate(contrib):
        parts = []
        for j in np.argsort(row)[::-1][:n]:
            if row[j] <= 0:
                break
            name = names[j]
            if name.startswith("cat__"):
                col = next(c for c in CATEGORICAL if name.startswith(f"cat__{c}_"))
                parts.append(f"{col}={df.iloc[i][col]}")
            elif name.startswith("num__missingindicator_"):
                parts.append(f"sem dado: {name.removeprefix('num__missingindicator_')}")
            else:
                col = name.removeprefix("num__")
                parts.append(f"{col}={df.iloc[i][col]}")
        out.append("; ".join(parts))
    return out


# --- relatório ------------------------------------------------------------------------

def render(selection, evaluation, diffs, prio, cal_table, cal, decision, coefs, meta) -> str:
    f = dg._fmt
    L = ["# Avaliação do modelo (EXP-002)", "",
         "> Gerado por `solution/src/model.py`; não editar à mão. Pré-registro: [EXP-002](../process-log/experiments/EXP-002-modelo-pre-registro.md). Resumo: [model-card.md](model-card.md).", "",
         f"Alvo `churn_next_30d`. Treino {SPLITS['treino'][0]} a {SPLITS['treino'][1]}; validação {SPLITS['validação'][0]} a {SPLITS['validação'][1]}; "
         f"teste {SPLITS['teste'][0]} a {SPLITS['teste'][1]} (avaliado uma vez). IC 95% por bootstrap agrupado por conta, pareado entre rankings.", "",
         "## Seleção de C (treino → validação)", "", "| C | AP validação | ROC-AUC validação |", "|---:|---:|---:|"]
    L += [f"| {r.C} | {f(r.ap, digits=3)} | {f(r.auc, digits=3)} |" for r in selection.itertuples()]
    L += ["", f"C escolhido: **{meta['C']}**. Challenger M2: {meta['challenger']}.", "",
          "## Validação e teste", "", "| Parte | Ranking | Linhas | Positivos | Prevalência | AP [IC 95%] | ROC-AUC [IC 95%] |", "|---|---|---:|---:|---:|---|---|"]
    L += [f"| {r.part} | {r.ranking} | {r.rows} | {r.positives} | {f(r.prevalence, True)} | {f(r.ap, digits=3)} [{f(r.ap_lo, digits=3)}, {f(r.ap_hi, digits=3)}] | {f(r.auc, digits=3)} [{f(r.auc_lo, digits=3)}, {f(r.auc_hi, digits=3)}] |" for r in evaluation.itertuples()]
    L += ["", "## Diferenças pareadas", "", "| Parte | A − B | Métrica | Diferença [IC 95%] |", "|---|---|---|---|"]
    L += [f"| {r.part} | {r.a} − {r.b} | {r.metric} | {f(r.diff, digits=3)} [{f(r.lo, digits=3)}, {f(r.hi, digits=3)}] |" for r in diffs.itertuples()]
    L += ["", f"**Decisão pela regra pré-registrada:** {decision}", "",
          "## Priorização no teste (top-K por corte)", "", "| Ranking | Capacidade | Alertas/mês | Falsos alertas/mês | Precisão | Recall | MRR coberto | Antecedência mediana (dias) |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {r.ranking} | {f(r.capacity, True)} | {f(r.alerts_per_month, digits=1)} | {f(r.false_alerts_per_month, digits=1)} | {f(r.precision, True)} | {f(r.recall, True)} | {f(r.mrr_covered, True)} | {f(r.median_lead_days, digits=0)} |" for r in prio.itertuples()]
    L += ["", "## Calibração do modelo no teste", "",
          f"Brier {f(cal['brier'], digits=4)} (prevalência constante: {f(cal['brier_prevalence'], digits=4)}). Média prevista {f(cal['mean_pred'], True)} × observada {f(cal['observed'], True)} "
          f"(diferença relativa {f(cal['relative_gap'], True)}); maior erro por decil {f(cal['max_decile_error'], True)}. "
          f"**Exibir probabilidade: {'sim' if cal['show_probability'] else 'não — usar só o percentil do ranking'}.**", "",
          "| Decil | Linhas | Prevista | Observada |", "|---:|---:|---:|---:|"]
    L += [f"| {int(r.decile) + 1} | {r.rows} | {f(r.mean_pred, True)} | {f(r.observed, True)} |" for r in cal_table.itertuples()]
    L += ["", "## Coeficientes do modelo final (10 maiores em módulo; features padronizadas)", "", "| Feature | Coeficiente |", "|---|---:|"]
    L += [f"| `{r.feature}` | {f(r.coef, digits=3)} |" for r in coefs.head(10).itertuples()]
    return "\n".join(L) + "\n"


# --- execução -------------------------------------------------------------------------

def main() -> int:
    snaps, end, lineage = load_snapshots()
    churn = clean_data.load_clean("churn_events")[["account_id", "churn_date"]]
    tr, va, te = split(snaps, "treino"), split(snaps, "validação"), split(snaps, "teste")

    selection = []
    for c in C_GRID:
        p = make_lr(c).fit(X(tr), y(tr)).predict_proba(X(va))[:, 1]
        selection.append({"C": c, "ap": average_precision_score(y(va), p), "auc": roc_auc_score(y(va), p)})
    selection = pd.DataFrame(selection)
    best_c = float(selection.sort_values(["ap", "C"], ascending=[False, True]).iloc[0]["C"])

    m1_val = make_lr(best_c).fit(X(tr), y(tr)).predict_proba(X(va))[:, 1]
    val_scores = {"M1 regressão logística": m1_val, **baselines(va)}
    val_res = bootstrap(va, val_scores)
    diffs = [{"part": "validação", **paired_diff(val_res, "M1 regressão logística", "B1 tempo de casa curto")}]
    chosen, factory = "M1 regressão logística", (lambda: make_lr(best_c))
    challenger = "não testado: M1 não superou B1 na validação (IC da diferença de AP inclui 0)"
    if diffs[0]["lo"] > 0:
        m2_val = make_hgb().fit(X(tr), y(tr)).predict_proba(X(va))[:, 1]
        val_scores["M2 gradient boosting"] = m2_val
        val_res = bootstrap(va, val_scores)
        if average_precision_score(y(va), m2_val) > average_precision_score(y(va), m1_val):
            chosen, factory = "M2 gradient boosting", make_hgb
        challenger = f"testado; escolhido {chosen} pela AP de validação"

    # Teste: avaliado uma única vez, com o modelo ajustado em treino + validação.
    trva = split(snaps, "treino", "validação")
    fitted = factory().fit(X(trva), y(trva))
    p_test = fitted.predict_proba(X(te))[:, 1]
    test_scores = {chosen: p_test, **baselines(te)}
    test_res = bootstrap(te, test_scores)
    diffs.append({"part": "teste", **paired_diff(test_res, chosen, "B1 tempo de casa curto")})
    diffs.append({"part": "teste", **paired_diff(test_res, chosen, "B1 tempo de casa curto", "auc")})
    beats = diffs[1]["lo"] > 0
    decision = (f"{chosen} **supera** B1 no teste (IC da diferença de AP acima de 0); o painel usa o modelo." if beats else
                f"{chosen} **não supera** B1 no teste (IC da diferença de AP inclui 0 ou fica abaixo). "
                "O painel usa ranking transparente; o modelo fica documentado como resultado negativo.")
    evaluation = pd.DataFrame(metric_rows("validação", va, val_res) + metric_rows("teste", te, test_res))
    prio = pd.DataFrame([{"ranking": name, **prioritization(te, score, cap, churn)}
                         for name, score in test_scores.items() for cap in CAPACITIES])
    cal_table, cal = calibration(te, p_test)

    # Modelo final para a carteira: treino + validação + teste, mesmos hiperparâmetros.
    allrows = split(snaps, "treino", "validação", "teste")
    final = factory().fit(X(allrows), y(allrows))
    now = snaps[snaps["cutoff_date"] == end].sort_values("account_id", ignore_index=True)
    score = final.predict_proba(X(now))[:, 1]
    coefs = pd.DataFrame()
    if chosen.startswith("M1"):
        coefs = pd.DataFrame({"feature": final.named_steps["pre"].get_feature_names_out(),
                              "coef": final.named_steps["clf"].coef_[0]})
        coefs = coefs.reindex(coefs["coef"].abs().sort_values(ascending=False).index).reset_index(drop=True)
    scores = pd.DataFrame({
        "account_id": now["account_id"], "reference_date": end.date().isoformat(), "horizon_days": HORIZON_DAYS,
        "model_version": VERSION, "model_score": np.round(score, 6),
        "model_percentile": np.round(pd.Series(score).rank(pct=True).to_numpy() * 100, 1),
        "tenure_days": now["tenure_days"], "tenure_percentile": np.round((-now["tenure_days"]).rank(pct=True).to_numpy() * 100, 1),
        "mrr_active": now["mrr_active"], "recommended_ranking": "modelo" if beats else "tempo de casa",
        "probability_reliable": cal["show_probability"],
        "top_signals": top_signals(final, now) if chosen.startswith("M1") else "",
    })

    meta = {"version": VERSION, "chosen": chosen, "C": best_c, "challenger": challenger, "horizon_days": HORIZON_DAYS,
            "splits": {k: list(v) for k, v in SPLITS.items()}, "final_fit": "treino + validação + teste",
            "reference_date": end.date().isoformat(), "features_numeric": NUMERIC, "features_categorical": CATEGORICAL,
            "forbidden_checked": sorted(FORBIDDEN), "beats_baseline_on_test": bool(beats),
            "recommended_ranking": "modelo" if beats else "tempo de casa", "probability_reliable": cal["show_probability"],
            "calibration": {k: float(v) for k, v in cal.items() if k != "show_probability"},
            "coefficients": dict(zip(coefs.get("feature", []), map(float, coefs.get("coef", [])))),
            "lineage": {"base_manifest_sha256": lineage}, "sklearn": sklearn.__version__, "pandas": pd.__version__}

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final, MODEL_DIR / f"{VERSION}.joblib")
    (MODEL_DIR / "model_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    opts = {"index": False, "lineterminator": "\n", "float_format": "%.6g"}
    selection.to_csv(OUT_DIR / "selection.csv", **opts)
    evaluation.to_csv(OUT_DIR / "evaluation.csv", **opts)
    pd.DataFrame(diffs).to_csv(OUT_DIR / "paired_diff.csv", **opts)
    prio.to_csv(OUT_DIR / "prioritization_test.csv", **opts)
    cal_table.to_csv(OUT_DIR / "calibration_test.csv", **opts)
    coefs.to_csv(OUT_DIR / "coefficients.csv", **opts)
    scores.to_csv(SCORES_DIR / f"scores_{end.date().isoformat()}.csv", index=False, lineterminator="\n")
    EVALUATION.write_text(render(selection, evaluation, pd.DataFrame(diffs), prio, cal_table, cal, decision, coefs, meta), encoding="utf-8")
    print(evaluation[["part", "ranking", "prevalence", "ap", "ap_lo", "ap_hi", "auc"]].round(3).to_string(index=False))
    print(pd.DataFrame(diffs).round(3).to_string(index=False))
    print(decision)
    print(f"calibração: {cal}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
