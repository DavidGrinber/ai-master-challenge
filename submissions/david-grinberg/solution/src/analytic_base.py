"""Base analítica (DAV-181): perfil retrospectivo por conta e snapshots conta × data de corte.

Premissas do candidato (DEC-015, P-01 a P-03 em docs/data-contract.md):
    P-01 churn = evento em churn_events (com data); churn_flag só descritivo.
    P-02 MRR da conta em t = soma do mrr_amount das assinaturas ativas em t; as 4 cópias exatas
         contam como assinaturas legítimas (DEC-018).
    P-03 uso e tickets entram pela data do próprio evento, mesmo fora do ciclo da conta.
Proposta pendente de revisão (DEC-016): elegível em t = signup <= t e >= 1 assinatura ativa em t.

Cada tabela é agregada por conta separadamente e alinhada 1:1 pelo account_id; nenhuma
junção de eventos brutos multiplica contas, eventos ou receita (conferido em reconciliation.csv).
Snapshots usam apenas eventos com data <= t (fim do dia t); rótulos olham (t, t+H] e ficam
nulos quando t+H passa do fim da observação.

Uso, a partir de submissions/david-grinberg/ (depois de clean_data.py):
    python solution/src/analytic_base.py

Saídas:
    solution/data/processed/accounts_retrospective.csv   (local, fora do Git)
    solution/data/processed/snapshots.csv                (local, fora do Git)
    solution/outputs/analytic_base/reconciliation.csv    (versionado)
    solution/outputs/analytic_base/label_counts.csv      (versionado)
    solution/outputs/analytic_base/base_manifest.json    (versionado: schema, SHA-256, linhagem)
    docs/analytic-base-dictionary.md                     (versionado, gerado)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

import clean_data
import raw_data

PROCESSED_DIR = raw_data.DATA_DIR / "processed"
OUT_DIR = clean_data.SUB_DIR / "solution" / "outputs" / "analytic_base"
DICTIONARY = clean_data.SUB_DIR / "docs" / "analytic-base-dictionary.md"
HORIZONS = (30, 60, 90)
DAY = pd.Timedelta(days=1)

SNAPSHOT_COLUMNS = {
    "account_id": "conta",
    "cutoff_date": "data de corte t (fim de mês); tudo abaixo usa só eventos com data <= t",
    "industry": "accounts.industry (atributo de cadastro)",
    "country": "accounts.country (atributo de cadastro)",
    "referral_source": "accounts.referral_source (atributo de cadastro)",
    "plan_tier_initial": "accounts.plan_tier, plano inicial segundo a fonte",
    "tenure_days": "dias entre signup_date e t",
    "n_active_subs": "assinaturas ativas em t (início <= t e fim vazio ou > t)",
    "mrr_active": "P-02: soma do mrr_amount das assinaturas ativas em t",
    "seats_active": "soma de seats das assinaturas ativas em t",
    "n_active_trial_subs": "assinaturas ativas em t com is_trial",
    "n_active_basic": "assinaturas ativas em t no plano Basic",
    "n_active_pro": "assinaturas ativas em t no plano Pro",
    "n_active_enterprise": "assinaturas ativas em t no plano Enterprise",
    "share_active_annual": "fração das assinaturas ativas em t com cobrança anual",
    "n_active_no_autorenew": "assinaturas ativas em t sem auto_renew",
    "n_subs_started_90d": "assinaturas iniciadas em (t-90, t]",
    "n_subs_ended_90d": "assinaturas encerradas em (t-90, t]",
    "n_upgrade_closed_subs": "assinaturas já encerradas até t com upgrade_flag (a flag não tem data; só entra após o fim)",
    "n_downgrade_closed_subs": "assinaturas já encerradas até t com downgrade_flag (idem)",
    "usage_rows_30d": "linhas de uso em (t-30, t] (P-03)",
    "usage_count_30d": "soma de usage_count em (t-30, t]",
    "usage_count_prev_30d": "soma de usage_count em (t-60, t-30]",
    "usage_secs_30d": "soma de usage_duration_secs em (t-30, t]",
    "errors_30d": "soma de error_count em (t-30, t]",
    "distinct_features_30d": "features distintas usadas em (t-30, t]",
    "beta_rows_30d": "linhas de uso de feature beta em (t-30, t]",
    "usage_count_90d": "soma de usage_count em (t-90, t]",
    "errors_90d": "soma de error_count em (t-90, t]",
    "usage_rows_to_date": "linhas de uso com data <= t",
    "days_since_last_usage": "dias desde o último uso <= t; nulo se nunca houve uso",
    "tickets_90d": "tickets abertos em (t-90, t]",
    "tickets_urgent_high_90d": "tickets urgent ou high abertos em (t-90, t]",
    "tickets_to_date": "tickets abertos até t",
    "open_tickets": "tickets abertos até t e ainda não fechados em t",
    "closed_tickets_90d": "tickets fechados em (t-90, t]",
    "mean_resolution_hours_90d": "média de resolution_time_hours dos fechados em (t-90, t]; nulo se nenhum",
    "mean_first_response_min_90d": "média de first_response_time_minutes dos fechados em (t-90, t]; nulo se nenhum",
    "escalations_90d": "fechados em (t-90, t] com escalation_flag (só conhecido no fechamento)",
    "satisfaction_responses_90d": "fechados em (t-90, t] com nota de satisfação",
    "mean_satisfaction_90d": "média das notas dos fechados em (t-90, t]; nulo se nenhuma (escala observada 3–5)",
    "prior_churn_events": "eventos de churn com data <= t",
    "days_since_last_churn": "dias desde o último churn <= t; nulo se nenhum",
    **{f"churn_next_{h}d": f"RÓTULO: algum evento de churn em (t, t+{h}]; nulo se t+{h} > fim dos dados" for h in HORIZONS},
}

PROFILE_COLUMNS = {
    "account_id": "conta",
    "account_name": "accounts.account_name",
    "industry": "accounts.industry",
    "country": "accounts.country",
    "signup_date": "accounts.signup_date",
    "referral_source": "accounts.referral_source",
    "plan_tier": "accounts.plan_tier (inicial segundo a fonte)",
    "seats": "accounts.seats (momento de referência desconhecido)",
    "is_trial": "accounts.is_trial ('currently trialing' segundo a fonte)",
    "churn_flag": "accounts.churn_flag original (contraditório; ver q_churn_flag_conflict)",
    "has_churn_event": "P-01: a conta tem ao menos um evento em churn_events",
    "q_churn_flag_conflict": "churn_flag diverge de has_churn_event",
    "n_churn_events": "eventos de churn no período todo",
    "first_churn_date": "primeiro evento de churn",
    "last_churn_date": "último evento de churn",
    "n_subscriptions": "assinaturas no período todo",
    "n_active_subs_end": "assinaturas ativas no fim dos dados",
    "mrr_active_end": "P-02: MRR ativo no fim dos dados",
    "usage_rows": "linhas de uso no período todo",
    "usage_count": "soma de usage_count",
    "usage_secs": "soma de usage_duration_secs",
    "errors": "soma de error_count",
    "distinct_features": "features distintas usadas",
    "beta_rows": "linhas de uso de feature beta",
    "tickets": "tickets no período todo",
    "escalations": "tickets com escalation_flag",
    "mean_resolution_hours": "média de resolution_time_hours; nulo se sem ticket",
    "satisfaction_responses": "tickets com nota de satisfação",
    "mean_satisfaction": "média das notas; nulo se nenhuma",
}


def _until(df: pd.DataFrame, col: str, t: pd.Timestamp) -> pd.DataFrame:
    return df[df[col] < t + DAY]


def _window(df: pd.DataFrame, col: str, t: pd.Timestamp, days: int, skip: int = 0) -> pd.DataFrame:
    """Linhas com data em (t-days-skip, t-skip], contando o dia t inteiro."""
    hi = t + DAY - pd.Timedelta(days=skip)
    return df[(df[col] >= hi - pd.Timedelta(days=days)) & (df[col] < hi)]


def active_subscriptions(sub: pd.DataFrame, t: pd.Timestamp) -> pd.DataFrame:
    return sub[(sub["start_date"] <= t) & (sub["end_date"].isna() | (sub["end_date"] > t))]


def eligible_accounts(acc: pd.DataFrame, sub: pd.DataFrame, t: pd.Timestamp) -> pd.Index:
    signed = set(acc.loc[acc["signup_date"] <= t, "account_id"])
    active = set(active_subscriptions(sub, t)["account_id"])
    return pd.Index(sorted(signed & active), name="account_id")


def snapshot_at(tables: dict[str, pd.DataFrame], t: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    acc, sub, fu, tk, ce = (tables[n] for n in clean_data.TABLES)
    ids = eligible_accounts(acc, sub, t)
    a = acc.set_index("account_id").loc[ids]
    f = pd.DataFrame(index=ids)
    f["cutoff_date"] = t
    f["industry"], f["country"], f["referral_source"] = a["industry"], a["country"], a["referral_source"]
    f["plan_tier_initial"] = a["plan_tier"]
    f["tenure_days"] = (t - a["signup_date"]).dt.days

    act = active_subscriptions(sub, t)
    g = act.groupby("account_id")
    f["n_active_subs"] = g.size()
    f["mrr_active"] = g["mrr_amount"].sum()
    f["seats_active"] = g["seats"].sum()
    f["n_active_trial_subs"] = g["is_trial"].sum()
    for tier in ("Basic", "Pro", "Enterprise"):
        f[f"n_active_{tier.lower()}"] = (act["plan_tier"] == tier).groupby(act["account_id"]).sum()
    f["share_active_annual"] = (act["billing_frequency"] == "annual").groupby(act["account_id"]).mean()
    f["n_active_no_autorenew"] = (~act["auto_renew_flag"]).groupby(act["account_id"]).sum()
    f["n_subs_started_90d"] = _window(sub, "start_date", t, 90).groupby("account_id").size()
    ended = sub[sub["end_date"].notna()]
    f["n_subs_ended_90d"] = _window(ended, "end_date", t, 90).groupby("account_id").size()
    closed = _until(ended, "end_date", t).groupby("account_id")
    f["n_upgrade_closed_subs"] = closed["upgrade_flag"].sum()
    f["n_downgrade_closed_subs"] = closed["downgrade_flag"].sum()

    u30 = _window(fu, "usage_date", t, 30).groupby("account_id")
    f["usage_rows_30d"] = u30.size()
    f["usage_count_30d"] = u30["usage_count"].sum()
    f["usage_count_prev_30d"] = _window(fu, "usage_date", t, 30, skip=30).groupby("account_id")["usage_count"].sum()
    f["usage_secs_30d"] = u30["usage_duration_secs"].sum()
    f["errors_30d"] = u30["error_count"].sum()
    f["distinct_features_30d"] = u30["feature_name"].nunique()
    f["beta_rows_30d"] = u30["is_beta_feature"].sum()
    u90 = _window(fu, "usage_date", t, 90).groupby("account_id")
    f["usage_count_90d"] = u90["usage_count"].sum()
    f["errors_90d"] = u90["error_count"].sum()
    u_all = _until(fu, "usage_date", t).groupby("account_id")
    f["usage_rows_to_date"] = u_all.size()
    f["days_since_last_usage"] = (t - u_all["usage_date"].max()).dt.days

    opened = _until(tk, "submitted_at", t)
    o90 = _window(tk, "submitted_at", t, 90)
    f["tickets_90d"] = o90.groupby("account_id").size()
    f["tickets_urgent_high_90d"] = o90["priority"].isin(["urgent", "high"]).groupby(o90["account_id"]).sum()
    f["tickets_to_date"] = opened.groupby("account_id").size()
    f["open_tickets"] = opened[opened["closed_at"] >= t + DAY].groupby("account_id").size()
    c90 = _window(tk, "closed_at", t, 90)
    gc = c90.groupby("account_id")
    f["closed_tickets_90d"] = gc.size()
    f["mean_resolution_hours_90d"] = gc["resolution_time_hours"].mean()
    f["mean_first_response_min_90d"] = gc["first_response_time_minutes"].mean()
    f["escalations_90d"] = gc["escalation_flag"].sum()
    f["satisfaction_responses_90d"] = gc["has_satisfaction"].sum()
    f["mean_satisfaction_90d"] = gc["satisfaction_score"].mean().astype("Float64")

    prior = _until(ce, "churn_date", t).groupby("account_id")
    f["prior_churn_events"] = prior.size()
    f["days_since_last_churn"] = (t - prior["churn_date"].max()).dt.days

    for h in HORIZONS:
        if t + pd.Timedelta(days=h) > end:
            f[f"churn_next_{h}d"] = pd.array([pd.NA] * len(f), dtype="boolean")
            continue
        hit = ce[(ce["churn_date"] > t) & (ce["churn_date"] <= t + pd.Timedelta(days=h))]["account_id"]
        f[f"churn_next_{h}d"] = pd.array(f.index.isin(hit), dtype="boolean")

    nullable = {"days_since_last_usage", "days_since_last_churn", "share_active_annual",
                "mean_resolution_hours_90d", "mean_first_response_min_90d", "mean_satisfaction_90d"}
    for col in f.columns:
        if col in nullable or col.startswith("churn_next_") or not pd.api.types.is_numeric_dtype(f[col]):
            continue
        f[col] = f[col].fillna(0).astype("int64")
    for col in ("days_since_last_usage", "days_since_last_churn"):
        f[col] = f[col].astype("Int64")
    return f.reset_index()[list(SNAPSHOT_COLUMNS)]


def build_snapshots(tables: dict[str, pd.DataFrame], cutoffs: list[pd.Timestamp], end: pd.Timestamp) -> pd.DataFrame:
    frames = [snapshot_at(tables, t, end) for t in cutoffs]
    snaps = pd.concat(frames, ignore_index=True)
    return snaps.sort_values(["cutoff_date", "account_id"], ignore_index=True)


def build_profile(tables: dict[str, pd.DataFrame], end: pd.Timestamp) -> pd.DataFrame:
    acc, sub, fu, tk, ce = (tables[n] for n in clean_data.TABLES)
    p = acc.set_index("account_id")[[c for c in PROFILE_COLUMNS if c in acc.columns and c != "account_id"]].copy()
    ev = ce.groupby("account_id")
    p["n_churn_events"] = ev.size()
    p["first_churn_date"] = ev["churn_date"].min()
    p["last_churn_date"] = ev["churn_date"].max()
    p["n_subscriptions"] = sub.groupby("account_id").size()
    act = active_subscriptions(sub, end).groupby("account_id")
    p["n_active_subs_end"] = act.size()
    p["mrr_active_end"] = act["mrr_amount"].sum()
    gu = fu.groupby("account_id")
    p["usage_rows"] = gu.size()
    p["usage_count"] = gu["usage_count"].sum()
    p["usage_secs"] = gu["usage_duration_secs"].sum()
    p["errors"] = gu["error_count"].sum()
    p["distinct_features"] = gu["feature_name"].nunique()
    p["beta_rows"] = gu["is_beta_feature"].sum()
    gt = tk.groupby("account_id")
    p["tickets"] = gt.size()
    p["escalations"] = gt["escalation_flag"].sum()
    p["mean_resolution_hours"] = gt["resolution_time_hours"].mean()
    p["satisfaction_responses"] = gt["has_satisfaction"].sum()
    p["mean_satisfaction"] = gt["satisfaction_score"].mean().astype("Float64")
    counts = ["n_churn_events", "n_subscriptions", "n_active_subs_end", "mrr_active_end", "usage_rows", "usage_count",
              "usage_secs", "errors", "distinct_features", "beta_rows", "tickets", "escalations", "satisfaction_responses"]
    p[counts] = p[counts].fillna(0).astype("int64")
    return p.reset_index()[list(PROFILE_COLUMNS)]


def reconcile(tables: dict[str, pd.DataFrame], profile: pd.DataFrame, snaps: pd.DataFrame,
              end: pd.Timestamp) -> list[dict]:
    """Totais da base analítica versus as tabelas limpas: provam que nada foi multiplicado ou perdido."""
    acc, sub, fu, tk, ce = (tables[n] for n in clean_data.TABLES)
    open_mrr = sub.loc[sub["end_date"].isna(), "mrr_amount"].sum()  # independente de active_subscriptions
    last = snaps[snaps["cutoff_date"] == end]
    rows = [
        ("perfil: contas", len(acc), len(profile)),
        ("perfil: account_id único", 1, int(profile["account_id"].is_unique)),
        ("perfil: eventos de churn", len(ce), profile["n_churn_events"].sum()),
        ("perfil: assinaturas", len(sub), profile["n_subscriptions"].sum()),
        ("perfil: MRR ativo no fim (assinaturas sem end_date)", open_mrr, profile["mrr_active_end"].sum()),
        ("perfil: linhas de uso", len(fu), profile["usage_rows"].sum()),
        ("perfil: usage_count", fu["usage_count"].sum(), profile["usage_count"].sum()),
        ("perfil: error_count", fu["error_count"].sum(), profile["errors"].sum()),
        ("perfil: tickets", len(tk), profile["tickets"].sum()),
        ("snapshots: (account_id, cutoff_date) único", 1, int(not snaps.duplicated(["account_id", "cutoff_date"]).any())),
        (f"snapshots em {end.date()}: contas elegíveis", len(eligible_accounts(acc, sub, end)), len(last)),
        (f"snapshots em {end.date()}: MRR ativo", open_mrr, last["mrr_active"].sum()),
        (f"snapshots em {end.date()}: linhas de uso até t", len(_until(fu[fu["account_id"].isin(last["account_id"])], "usage_date", end)), last["usage_rows_to_date"].sum()),
        (f"snapshots em {end.date()}: tickets até t", len(_until(tk[tk["account_id"].isin(last["account_id"])], "submitted_at", end)), last["tickets_to_date"].sum()),
        (f"snapshots em {end.date()}: eventos de churn até t", len(_until(ce[ce["account_id"].isin(last["account_id"])], "churn_date", end)), last["prior_churn_events"].sum()),
    ]
    return [{"check": c, "expected": int(e), "observed": int(o), "ok": int(e) == int(o)} for c, e, o in rows]


def label_counts(snaps: pd.DataFrame) -> pd.DataFrame:
    g = snaps.groupby("cutoff_date")
    out = pd.DataFrame({"eligible": g.size(), "mrr_active": g["mrr_active"].sum()})
    for h in HORIZONS:
        col = f"churn_next_{h}d"
        known = g[col].count()
        out[f"positives_{h}d"] = g[col].sum().astype("Int64").where(known > 0)
        out[f"mrr_positives_{h}d"] = (snaps["mrr_active"] * snaps[col].fillna(False)).groupby(snaps["cutoff_date"]).sum().astype("Int64").where(known > 0)
    return out.reset_index()


def render_dictionary(manifest: dict) -> str:
    lines = ["# Dicionário da base analítica", "",
             "> Gerado por `solution/src/analytic_base.py`; não editar à mão. Premissas e regras em [data-contract.md](data-contract.md).", ""]
    for name, descriptions in (("snapshots", SNAPSHOT_COLUMNS), ("accounts_retrospective", PROFILE_COLUMNS)):
        spec = manifest["tables"][name]
        lines += [f"## {name}.csv — {spec['rows']} linhas", "", spec["purpose"], "",
                  "| Coluna | Tipo | Descrição |", "|---|---|---|"]
        lines += [f"| `{c}` | {spec['columns'][c]} | {d} |" for c, d in descriptions.items()]
        lines.append("")
    return "\n".join(lines)


def write(profile: pd.DataFrame, snaps: pd.DataFrame, checks: list[dict], counts: pd.DataFrame,
          cutoffs: list[pd.Timestamp], end: pd.Timestamp, processed_dir: Path, out_dir: Path,
          dictionary: Path, lineage: dict) -> dict:
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    purposes = {
        "snapshots": "Uma linha por conta elegível e data de corte. Features só com eventos até t; rótulos em (t, t+H]. Base para o modelo (DAV-189) e para comparações temporais (DAV-184). O corte no fim dos dados não tem rótulo: é a carteira a pontuar.",
        "accounts_retrospective": "Uma linha por conta com o período todo. **Retrospectiva**: mistura informação anterior e posterior ao churn; serve ao diagnóstico, nunca como feature de previsão.",
    }
    manifest = {"generated_by": "solution/src/analytic_base.py", "pandas": pd.__version__,
                "data_end": str(end.date()), "cutoffs": [str(t.date()) for t in cutoffs],
                "horizons_days": list(HORIZONS),
                "eligibility": "signup_date <= t e >= 1 assinatura com start_date <= t e end_date vazio ou > t",
                "lineage": lineage, "tables": {}}
    for name, df in (("snapshots", snaps), ("accounts_retrospective", profile)):
        data = clean_data.to_csv_text(df).encode("utf-8")
        (processed_dir / f"{name}.csv").write_bytes(data)
        manifest["tables"][name] = {"rows": len(df), "purpose": purposes[name],
                                    "sha256": hashlib.sha256(data).hexdigest(),
                                    "columns": {c: clean_data.dtype_label(df[c]) for c in df.columns}}
    (out_dir / "base_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(checks).to_csv(out_dir / "reconciliation.csv", index=False, lineterminator="\n")
    counts.to_csv(out_dir / "label_counts.csv", index=False, lineterminator="\n", date_format="%Y-%m-%d")
    dictionary.write_text(render_dictionary(manifest), encoding="utf-8")
    return manifest


def build_all(tables: dict[str, pd.DataFrame], end: pd.Timestamp, processed_dir: Path, out_dir: Path,
              dictionary: Path, lineage: dict) -> tuple[dict, list[dict]]:
    first = tables["accounts"]["signup_date"].min()
    cutoffs = list(pd.date_range(first, end, freq="ME"))
    profile = build_profile(tables, end)
    snaps = build_snapshots(tables, cutoffs, end)
    checks = reconcile(tables, profile, snaps, end)
    manifest = write(profile, snaps, checks, label_counts(snaps), cutoffs, end, processed_dir, out_dir, dictionary, lineage)
    return manifest, checks


def main() -> int:
    derived = clean_data.QUALITY_DIR / "derived_manifest.json"
    if not derived.exists():
        print("base limpa ausente; rode clean_data.py antes", file=sys.stderr)
        return 1
    spec = json.loads(derived.read_text(encoding="utf-8"))
    for name, table in spec["tables"].items():
        path = clean_data.CLEAN_DIR / f"{name}.csv"
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != table["sha256"]:
            print(f"{path.name} diverge de derived_manifest.json; rode clean_data.py antes", file=sys.stderr)
            return 1
    tables = {t: clean_data.load_clean(t) for t in clean_data.TABLES}
    end = pd.Timestamp(spec["data_end"])
    lineage = {"derived_manifest_sha256": hashlib.sha256(derived.read_bytes()).hexdigest()}
    manifest, checks = build_all(tables, end, PROCESSED_DIR, OUT_DIR, DICTIONARY, lineage)
    for name, table in manifest["tables"].items():
        print(f"{name:24} {table['rows']:>6} linhas  {table['sha256'][:12]}")
    failed = [c for c in checks if not c["ok"]]
    for c in checks:
        print(f"{'ok' if c['ok'] else 'ERRO':4}  {c['check']}: {c['observed']} (esperado {c['expected']})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
