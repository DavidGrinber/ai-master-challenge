"""Checagem das dicas do challenge (complemento pós-hoc da DAV-184, exploratório).

Pergunta do candidato em 2026-10-26: "você analisou tudo que está nas dicas do repositório?
realmente nada explica o churn?". A análise principal (EXP-001) era temporal; aqui entram as
comparações que as dicas sugerem e que faltavam: churners × retidos no nível da conta (com as duas
definições de churn), uso por feature, assinaturas, motivos e uso por segmento. Tudo é exploratório
e corrigido para múltiplas comparações (Bonferroni).

Uso: python solution/src/explore_hints.py
Saídas: solution/outputs/diagnosis/hints_*.csv e docs/hints-checklist.md (gerado).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, kruskal, mannwhitneyu
from sklearn.metrics import roc_auc_score

import analytic_base as ab
import clean_data
import diagnose as dg

OUT_DIR = dg.OUT_DIR
REPORT = clean_data.SUB_DIR / "docs" / "hints-checklist.md"
ALPHA = 0.05


def account_profile(tables: dict[str, pd.DataFrame], end: pd.Timestamp) -> pd.DataFrame:
    """Uma linha por conta com agregados do período todo (comparação retrospectiva, como sugerem as dicas)."""
    acc, sub, fu, tk, ce = (tables[n] for n in clean_data.TABLES)
    a = acc.set_index("account_id")[["industry", "country", "referral_source", "plan_tier", "is_trial", "seats",
                                      "signup_date", "churn_flag", "has_churn_event"]].copy()
    gs = sub.groupby("account_id")
    a["n_subs"] = gs.size()
    a["sub_mrr_mean"] = gs["mrr_amount"].mean()
    a["share_annual"] = (sub["billing_frequency"] == "annual").groupby(sub["account_id"]).mean()
    a["share_autorenew"] = gs["auto_renew_flag"].mean()
    a["share_upgrade"] = gs["upgrade_flag"].mean()
    a["share_downgrade"] = gs["downgrade_flag"].mean()
    a["share_trial_subs"] = gs["is_trial"].mean()
    gu = fu.groupby("account_id")
    a["usage_rows"] = gu.size()
    a["usage_count"] = gu["usage_count"].sum()
    a["secs_per_use_row"] = gu["usage_duration_secs"].mean()
    a["error_rate"] = gu["error_count"].sum() / gu["usage_count"].sum()
    a["distinct_features"] = gu["feature_name"].nunique()
    a["beta_share"] = gu["is_beta_feature"].mean()
    gt = tk.groupby("account_id")
    a["tickets"] = gt.size()
    a["resolution_hours"] = gt["resolution_time_hours"].mean()
    a["first_response_min"] = gt["first_response_time_minutes"].mean()
    a["escalation_rate"] = gt["escalation_flag"].mean()
    a["satisfaction"] = gt["satisfaction_score"].mean().astype(float)
    a["response_rate"] = gt["has_satisfaction"].mean()
    a["urgent_share"] = (tk["priority"] == "urgent").groupby(tk["account_id"]).mean()
    a["tenure_at_end"] = (end - a["signup_date"]).dt.days
    a["tickets"] = a["tickets"].fillna(0)
    return a


NUMERIC = ["seats", "n_subs", "sub_mrr_mean", "share_annual", "share_autorenew", "share_upgrade", "share_downgrade",
           "share_trial_subs", "usage_rows", "usage_count", "secs_per_use_row", "error_rate", "distinct_features",
           "beta_share", "tickets", "resolution_hours", "first_response_min", "escalation_rate", "satisfaction",
           "response_rate", "urgent_share", "tenure_at_end"]
CATEGORICAL = ["industry", "country", "referral_source", "plan_tier", "is_trial"]


def churners_vs_retained(a: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_tests = len(NUMERIC) + len(CATEGORICAL)
    for label in ("churn_flag", "has_churn_event"):
        y = a[label].astype(bool)
        for col in NUMERIC:
            d = a[[col]].assign(y=y).dropna()
            rows.append({"label": label, "variable": col, "kind": "numérica", "n": len(d),
                         "auc": roc_auc_score(d["y"], d[col]), "p": mannwhitneyu(d.loc[d["y"], col], d.loc[~d["y"], col]).pvalue,
                         "churn": d.loc[d["y"], col].mean(), "retained": d.loc[~d["y"], col].mean()})
        for col in CATEGORICAL:
            tab = pd.crosstab(a[col].astype(str), y)
            rows.append({"label": label, "variable": col, "kind": "categórica", "n": int(tab.values.sum()),
                         "auc": np.nan, "p": chi2_contingency(tab)[1], "churn": np.nan, "retained": np.nan})
    out = pd.DataFrame(rows)
    out["bonferroni_threshold"] = ALPHA / n_tests
    out["significant"] = out["p"] < out["bonferroni_threshold"]
    return out


def feature_usage(tables: dict[str, pd.DataFrame], a: pd.DataFrame) -> pd.DataFrame:
    fu = tables["feature_usage"]
    share = fu.pivot_table(index="account_id", columns="feature_name", values="usage_count", aggfunc="sum", fill_value=0)
    share = share.div(share.sum(axis=1), axis=0)
    adopted = fu.groupby(["account_id", "feature_name"]).size().unstack(fill_value=0) > 0
    rows = []
    for label in ("churn_flag", "has_churn_event"):
        y_share = a.loc[share.index, label].astype(bool).to_numpy()
        y_adopt = a.loc[adopted.index, label].astype(bool)
        for f in share.columns:
            p_share = mannwhitneyu(share[f][y_share], share[f][~y_share]).pvalue
            p_adopt = chi2_contingency(pd.crosstab(adopted[f], y_adopt))[1] if adopted[f].nunique() > 1 else np.nan
            rows.append({"label": label, "feature": f, "auc_share": roc_auc_score(y_share, share[f]),
                         "p_share": p_share, "p_adoption": p_adopt})
    out = pd.DataFrame(rows)
    out["bonferroni_threshold"] = ALPHA / share.shape[1]
    return out


def subscription_level(sub: pd.DataFrame) -> pd.DataFrame:
    s = sub.assign(ended=sub["end_date"].notna())
    rows = []
    for col in ("plan_tier", "billing_frequency", "auto_renew_flag", "upgrade_flag", "downgrade_flag", "is_trial"):
        tab = pd.crosstab(s[col].astype(str), s["ended"])
        rows.append({"variable": col, "p": chi2_contingency(tab)[1],
                     "ended_rate_by_level": json.dumps((tab[True] / tab.sum(axis=1)).round(3).to_dict())})
    for col in ("seats", "mrr_amount"):
        rows.append({"variable": col, "p": mannwhitneyu(s.loc[s["ended"], col], s.loc[~s["ended"], col]).pvalue,
                     "ended_rate_by_level": f"AUC {roc_auc_score(s['ended'], s[col]):.3f}"})
    out = pd.DataFrame(rows)
    out["bonferroni_threshold"] = ALPHA / len(out)
    return out


def reasons_value(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    sub, ce, acc = tables["subscriptions"], tables["churn_events"].copy(), tables["accounts"]
    ce["mrr_at_churn"] = [ab.active_subscriptions(sub[sub["account_id"] == a], d - pd.Timedelta(days=1))["mrr_amount"].sum()
                          for a, d in zip(ce["account_id"], ce["churn_date"])]
    g = ce.groupby("reason_code").agg(events=("churn_event_id", "size"), mrr_lost=("mrr_at_churn", "sum"),
                                      median_mrr=("mrr_at_churn", "median"), mean_refund=("refund_amount_usd", "mean"),
                                      share_refund=("refund_amount_usd", lambda r: (r > 0).mean()),
                                      share_preceding_upgrade=("preceding_upgrade_flag", "mean"),
                                      share_preceding_downgrade=("preceding_downgrade_flag", "mean")).reset_index()
    g["share_mrr_lost"] = g["mrr_lost"] / g["mrr_lost"].sum()
    groups = [x for _, x in ce.groupby("reason_code")]
    upgraded = set(sub.loc[sub["upgrade_flag"], "account_id"])
    tests = {"p_refund_by_reason": kruskal(*[x["refund_amount_usd"] for x in groups]).pvalue,
             "p_mrr_by_reason": kruskal(*[x["mrr_at_churn"] for x in groups]).pvalue,
             "p_preceding_upgrade_by_reason": chi2_contingency(pd.crosstab(ce["reason_code"], ce["preceding_upgrade_flag"]))[1],
             "p_preceding_downgrade_by_reason": chi2_contingency(pd.crosstab(ce["reason_code"], ce["preceding_downgrade_flag"]))[1],
             "preceding_upgrade_events_with_upgraded_sub": ce.loc[ce["preceding_upgrade_flag"], "account_id"].isin(upgraded).mean(),
             "all_accounts_with_upgraded_sub": acc["account_id"].isin(upgraded).mean()}
    return g, tests


def usage_by_segment(snaps: pd.DataFrame) -> pd.DataFrame:
    s = snaps[snaps["cutoff_date"] >= pd.Timestamp("2023-07-31")].copy()  # 2023S1 tem poucas contas elegíveis
    s["half"] = s["cutoff_date"].dt.year.astype(str) + "S" + ((s["cutoff_date"].dt.month > 6) + 1).astype(str)
    frames = []
    for seg in ("plan_tier_initial", "industry", "referral_source"):
        p = s.pivot_table(index=seg, columns="half", values="usage_count_30d", aggfunc="mean")
        p["change"] = p.iloc[:, -1] / p.iloc[:, 0] - 1
        frames.append(p.reset_index().rename(columns={seg: "level"}).assign(segment=seg))
    return pd.concat(frames, ignore_index=True)


def render(cvr, feats, subs, reasons, tests, seg) -> str:
    f = dg._fmt
    L = ["# Dicas do challenge: checagem complementar (exploratória)", "",
         "> Gerado por `solution/src/explore_hints.py`; não editar à mão. Análise pós-hoc feita depois da pergunta do candidato "
         "\"você analisou tudo que está nas dicas?\" (2026-10-26). Exploratória, com correção de Bonferroni. Interpretação em "
         "[diagnosis-findings.md](diagnosis-findings.md).", "",
         "## Dica: \"Olhe os tickets de suporte dos clientes que churnearam vs. os que ficaram\" — e todo o perfil da conta", "",
         f"Comparação retrospectiva no nível da conta (500 contas, período todo), com as duas definições de churn. "
         f"{len(NUMERIC) + len(CATEGORICAL)} variáveis por definição; limite de Bonferroni p < {f(cvr['bonferroni_threshold'].iloc[0], digits=4)}.", "",
         "| Definição | Variáveis significativas | Menor p (variável) | p < 0,05 sem correção |", "|---|---:|---|---:|"]
    for label, g in cvr.groupby("label"):
        top = g.sort_values("p").iloc[0]
        L.append(f"| {label} | {int(g['significant'].sum())} | {f(top['p'], digits=3)} ({top['variable']}) | {int((g['p'] < ALPHA).sum())} de {len(g)} |")
    L += ["", "| Definição | Variável | AUC | p | média churn | média retidos |", "|---|---|---:|---:|---:|---:|"]
    L += [f"| {r.label} | {r.variable} | {f(r.auc, digits=3)} | {f(r.p, digits=3)} | {f(r.churn, digits=3)} | {f(r.retained, digits=3)} |"
          for r in cvr.sort_values(["label", "p"]).itertuples()]
    L += ["", "## Dica: \"Cruze feature usage com churn events — há padrões?\" — por feature", "",
          f"40 features: participação de cada feature no uso da conta e adoção (sim/não). Limite de Bonferroni p < {f(feats['bonferroni_threshold'].iloc[0], digits=5)}.", "",
          "| Definição | Medida | Menor p (feature) | p < 0,05 | esperado ao acaso |", "|---|---|---|---:|---:|"]
    for label, g in feats.groupby("label"):
        for col, desc in (("p_share", "participação no uso"), ("p_adoption", "adoção sim/não")):
            gg = g.dropna(subset=[col]).sort_values(col)
            L.append(f"| {label} | {desc} | {f(gg[col].iloc[0], digits=3)} ({gg['feature'].iloc[0]}) | {int((gg[col] < ALPHA).sum())} de {len(gg)} | {f(ALPHA * len(gg), digits=0)} |")
    L += ["", "## Assinaturas: encerramento × atributos (5.000 assinaturas)", "", "| Atributo | p | Taxa de encerramento por nível |", "|---|---:|---|"]
    L += [f"| {r.variable} | {f(r.p, digits=3)} | {r.ended_rate_by_level} |" for r in subs.itertuples()]
    L += ["", "## Dica: \"Nem todo churn tem o mesmo peso\" — MRR perdido e motivos", "",
          "| Motivo | Eventos | MRR perdido | % do MRR perdido | MRR mediano | Refund médio | % com refund | % upgrade prévio | % downgrade prévio |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    L += [f"| {r.reason_code} | {r.events} | {int(r.mrr_lost)} | {f(r.share_mrr_lost, True)} | {f(r.median_mrr, digits=0)} | {f(r.mean_refund)} | {f(r.share_refund, True)} | {f(r.share_preceding_upgrade, True)} | {f(r.share_preceding_downgrade, True)} |" for r in reasons.itertuples()]
    L += ["", f"Refund por motivo p = {f(tests['p_refund_by_reason'], digits=3)}; MRR no churn por motivo p = {f(tests['p_mrr_by_reason'], digits=3)}; "
          f"upgrade prévio × motivo p = {f(tests['p_preceding_upgrade_by_reason'], digits=3)}; downgrade prévio × motivo p = {f(tests['p_preceding_downgrade_by_reason'], digits=3)}. "
          f"Eventos com `preceding_upgrade_flag` em contas que têm alguma assinatura com upgrade: {f(tests['preceding_upgrade_events_with_upgraded_sub'], True)} "
          f"(base de todas as contas: {f(tests['all_accounts_with_upgraded_sub'], True)}).", "",
          "## Dica: \"O uso cresceu — isso é verdade pra todos os segmentos?\"", "",
          "Uso médio em 30 dias por conta elegível, por semestre (2023S1 omitido: poucas contas).", "",
          "| Segmento | Nível | 2023S2 | 2024S1 | 2024S2 | Variação |", "|---|---|---:|---:|---:|---:|"]
    L += [f"| {r.segment} | {r.level} | {f(r._3, digits=1)} | {f(r._4, digits=1)} | {f(r._5, digits=1)} | {f(r.change, True)} |" for r in seg[["segment", "level", "2023S2", "2024S1", "2024S2", "change"]].itertuples()]
    return "\n".join(L) + "\n"


def main() -> int:
    snaps, tables, end = dg.load_inputs()
    a = account_profile(tables, end)
    cvr = churners_vs_retained(a)
    feats = feature_usage(tables, a)
    subs = subscription_level(tables["subscriptions"])
    reasons, tests = reasons_value(tables)
    seg = usage_by_segment(snaps)
    opts = {"index": False, "lineterminator": "\n", "float_format": "%.6g"}
    cvr.to_csv(OUT_DIR / "hints_churners_vs_retained.csv", **opts)
    feats.to_csv(OUT_DIR / "hints_feature_usage.csv", **opts)
    subs.to_csv(OUT_DIR / "hints_subscriptions.csv", **opts)
    reasons.to_csv(OUT_DIR / "hints_reasons_value.csv", **opts)
    seg.to_csv(OUT_DIR / "hints_usage_by_segment.csv", **opts)
    (OUT_DIR / "hints_tests.json").write_text(json.dumps(tests, indent=2, default=float) + "\n", encoding="utf-8")
    REPORT.write_text(render(cvr, feats, subs, reasons, tests, seg), encoding="utf-8")
    print(cvr.groupby("label").agg(significant=("significant", "sum"), min_p=("p", "min")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
