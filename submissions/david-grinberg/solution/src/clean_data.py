"""Camada derivada limpa e normalizada (DAV-201).

Lê os 5 CSVs originais, normaliza tipos, cria chaves substitutas e marca com
colunas q_* as duplicatas e inconsistências encontradas na auditoria. Nenhuma
linha é removida e nenhum valor original é alterado: o que não tem solução vira
flag por linha e limitação no relatório. Decisões em docs/data-treatment-log.md.

Uso, a partir de submissions/david-grinberg/:
    python solution/src/clean_data.py

Saídas:
    solution/data/processed/clean/<tabela>.csv           (local, fora do Git)
    solution/outputs/data_quality/checks.csv             (versionado)
    solution/outputs/data_quality/derived_manifest.json  (versionado: schema e SHA-256)
    docs/data-quality-report.md                          (versionado, gerado)

Leitura da base derivada: load_clean("<tabela>").
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

import raw_data

SUB_DIR = Path(__file__).resolve().parents[2]
CLEAN_DIR = raw_data.DATA_DIR / "processed" / "clean"
QUALITY_DIR = SUB_DIR / "solution" / "outputs" / "data_quality"
REPORT = SUB_DIR / "docs" / "data-quality-report.md"

TABLES = ("accounts", "subscriptions", "feature_usage", "support_tickets", "churn_events")
DATE_COLUMNS = {
    "accounts": ["signup_date"],
    "subscriptions": ["start_date", "end_date"],
    "feature_usage": ["usage_date"],
    "support_tickets": ["submitted_at", "closed_at"],
    "churn_events": ["churn_date"],
}
# Correspondência entre o texto de feedback e os reason_code compatíveis (TR-12).
FEEDBACK_REASONS = {
    "too expensive": {"pricing", "budget"},
    "missing features": {"features"},
    "switched to competitor": {"competitor"},
}
NEAREST_END_TOLERANCE_DAYS = 31


def read_raw(raw_dir: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for name in TABLES:
        df = pd.read_csv(raw_dir / f"ravenstack_{name}.csv")
        for col in DATE_COLUMNS[name]:
            df[col] = pd.to_datetime(df[col], format="ISO8601")
        tables[name] = df
    return tables


def data_end(raw: dict[str, pd.DataFrame]) -> pd.Timestamp:
    """Última data presente em qualquer tabela: fim da janela de observação."""
    return max(raw[t][c].max() for t in TABLES for c in DATE_COLUMNS[t]).normalize()


def _status(n: int, otherwise: str) -> str:
    return "ok" if n == 0 else otherwise


def clean(raw: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    acc, sub, fu, tk, ce = (raw[t].copy() for t in TABLES)
    end = data_end(raw)
    checks: list[dict] = []

    def check(cid, table, description, n, total, treatment, status):
        checks.append({"id": cid, "table": table, "check": description, "n": int(n),
                       "total": int(total), "treatment": treatment, "status": status})

    signup = acc.set_index("account_id")["signup_date"]
    account_ids = set(acc["account_id"])

    # --- accounts
    n = int(acc["account_id"].duplicated().sum())
    check("A-01", "accounts", "account_id duplicado", n, len(acc), "nenhum", _status(n, "limitação"))
    n = int(acc.isna().sum().sum())
    check("A-02", "accounts", "valores nulos", n, acc.size, "nenhum", _status(n, "limitação"))
    n = int((acc["country"] == "UK").sum())
    check("A-03", "accounts", "country = UK, fora do padrão ISO-2 documentado (seria GB)", n, len(acc),
          "mantido como na fonte (TR-03)", _status(n, "mantido"))
    acc["has_churn_event"] = acc["account_id"].isin(ce["account_id"])
    acc["q_churn_flag_conflict"] = acc["churn_flag"] != acc["has_churn_event"]
    n = int(acc["q_churn_flag_conflict"].sum())
    check("A-04", "accounts", "churn_flag contradiz a existência de churn_events", n, len(acc),
          "churn_flag preservado; flag q_churn_flag_conflict (TR-10)", _status(n, "limitação"))

    # --- subscriptions
    n = int(sub["subscription_id"].duplicated().sum())
    check("S-01", "subscriptions", "subscription_id duplicado", n, len(sub), "nenhum", _status(n, "limitação"))
    n = int((~sub["account_id"].isin(account_ids)).sum())
    check("S-02", "subscriptions", "account_id sem conta (órfão)", n, len(sub), "nenhum", _status(n, "limitação"))
    content = [c for c in sub.columns if c != "subscription_id"]
    canonical = sub.groupby(content, dropna=False)["subscription_id"].transform("min")
    sub["q_duplicate_of"] = canonical.where(canonical != sub["subscription_id"])
    sub["q_is_duplicate"] = sub["q_duplicate_of"].notna()
    n = int(sub["q_is_duplicate"].sum())
    check("S-03", "subscriptions", "cópia exata de outra assinatura (todos os campos exceto o id)", n, len(sub),
          "mantida; q_duplicate_of aponta a original; excluir de somas de receita (TR-04)", _status(n, "tratado"))
    n = int((sub["end_date"].notna() != sub["churn_flag"]).sum())
    check("S-04", "subscriptions", "churn_flag diverge de ter end_date", n, len(sub), "nenhum", _status(n, "limitação"))
    n = int((sub["start_date"] < sub["account_id"].map(signup)).sum())
    check("S-05", "subscriptions", "start_date antes do signup da conta", n, len(sub), "nenhum", _status(n, "limitação"))
    n = int((sub["end_date"] < sub["start_date"]).sum())
    check("S-06", "subscriptions", "end_date antes de start_date", n, len(sub), "nenhum", _status(n, "limitação"))
    n = int(((sub["mrr_amount"] == 0) != sub["is_trial"]).sum() + (sub["arr_amount"] != 12 * sub["mrr_amount"]).sum())
    check("S-07", "subscriptions", "MRR zero fora de trial ou ARR != 12 x MRR", n, len(sub), "nenhum", _status(n, "limitação"))
    sub["q_upgrade_and_downgrade"] = sub["upgrade_flag"] & sub["downgrade_flag"]
    n = int(sub["q_upgrade_and_downgrade"].sum())
    check("S-08", "subscriptions", "upgrade_flag e downgrade_flag ao mesmo tempo, sem data da mudança", n, len(sub),
          "mantido; flag q_upgrade_and_downgrade (TR-08)", _status(n, "limitação"))
    sub["active_at_data_end"] = sub["end_date"].isna()
    intervals = sub[["subscription_id", "account_id", "start_date"]].assign(
        stop=sub["end_date"].fillna(end + pd.Timedelta(days=1)))
    pairs = intervals.merge(intervals, on="account_id", suffixes=("", "_o"))
    pairs = pairs[(pairs["subscription_id"] != pairs["subscription_id_o"])
                  & (pairs["start_date"] < pairs["stop_o"]) & (pairs["start_date_o"] < pairs["stop"])]
    sub["q_overlaps_other_subscription"] = sub["subscription_id"].isin(pairs["subscription_id"])
    n = int(sub["q_overlaps_other_subscription"].sum())
    check("S-09", "subscriptions", "período sobreposto a outra assinatura da mesma conta", n, len(sub),
          "mantido; flag q_overlaps_other_subscription; MRR da conta a definir na DAV-181 (TR-07)", _status(n, "limitação"))

    # --- feature_usage
    sub_account = sub.set_index("subscription_id")["account_id"]
    fu.insert(0, "usage_row_id", [f"UR-{i:05d}" for i in range(1, len(fu) + 1)])
    fu["q_usage_id_reused"] = fu["usage_id"].duplicated(keep=False)
    n = int(fu["q_usage_id_reused"].sum())
    check("U-01", "feature_usage", "usage_id repetido em linhas diferentes", n, len(fu),
          "chave substituta usage_row_id pela ordem do arquivo (TR-05)", _status(n, "tratado"))
    n = int((~fu["subscription_id"].isin(sub_account.index)).sum())
    check("U-02", "feature_usage", "subscription_id sem assinatura (órfão)", n, len(fu), "nenhum", _status(n, "limitação"))
    n = int(fu.drop(columns=["usage_row_id", "usage_id", "q_usage_id_reused"]).duplicated().sum())
    check("U-03", "feature_usage", "linha idêntica a outra (exceto ids)", n, len(fu), "nenhum", _status(n, "limitação"))
    fu["q_same_subscription_day_feature"] = fu.duplicated(["subscription_id", "usage_date", "feature_name"], keep=False)
    n = int(fu["q_same_subscription_day_feature"].sum())
    check("U-04", "feature_usage", "mais de uma linha para a mesma assinatura, dia e feature", n, len(fu),
          "mantidas como eventos distintos; flag q_same_subscription_day_feature (TR-06)", _status(n, "mantido"))
    fu["account_id"] = fu["subscription_id"].map(sub_account)
    sub_by_id = sub.set_index("subscription_id")
    fu["q_before_account_signup"] = fu["usage_date"] < fu["account_id"].map(signup)
    fu["q_before_subscription_start"] = fu["usage_date"] < fu["subscription_id"].map(sub_by_id["start_date"])
    fu["q_after_subscription_end"] = fu["usage_date"] > fu["subscription_id"].map(sub_by_id["end_date"])
    fu["q_on_duplicate_subscription"] = fu["subscription_id"].map(sub_by_id["q_is_duplicate"])
    for cid, col, desc in [
        ("U-05", "q_before_account_signup", "uso datado antes do signup da conta"),
        ("U-06", "q_before_subscription_start", "uso datado antes do início da assinatura"),
        ("U-07", "q_after_subscription_end", "uso datado depois do fim da assinatura"),
    ]:
        n = int(fu[col].sum())
        check(cid, "feature_usage", desc, n, len(fu), f"mantido; flag {col} (TR-09)", _status(n, "limitação"))
    n = int(fu["q_on_duplicate_subscription"].sum())
    check("U-08", "feature_usage", "uso ligado a uma assinatura duplicada", n, len(fu),
          "mantido e atribuído à conta normalmente (TR-04)", _status(n, "mantido"))
    n = int((fu["usage_count"] == 0).sum())
    check("U-09", "feature_usage", "usage_count = 0", n, len(fu), "mantido", _status(n, "mantido"))
    n = int((~sub["subscription_id"].isin(fu["subscription_id"])).sum())
    check("U-10", "subscriptions", "assinatura sem nenhuma linha de uso", n, len(sub),
          "mantida; ausência de linha não é uso zero (TR-11)", _status(n, "mantido"))

    # --- support_tickets
    n = int(tk["ticket_id"].duplicated().sum())
    check("T-01", "support_tickets", "ticket_id duplicado", n, len(tk), "nenhum", _status(n, "limitação"))
    n = int((~tk["account_id"].isin(account_ids)).sum())
    check("T-02", "support_tickets", "account_id sem conta (órfão)", n, len(tk), "nenhum", _status(n, "limitação"))
    tk["satisfaction_score"] = tk["satisfaction_score"].astype("Int64")
    tk["has_satisfaction"] = tk["satisfaction_score"].notna()
    tk["q_before_account_signup"] = tk["submitted_at"] < tk["account_id"].map(signup)
    n = int(tk["q_before_account_signup"].sum())
    check("T-03", "support_tickets", "ticket aberto antes do signup da conta", n, len(tk),
          "mantido; flag q_before_account_signup (TR-09)", _status(n, "limitação"))
    elapsed = (tk["closed_at"] - tk["submitted_at"]).dt.total_seconds() / 3600
    n = int(((tk["closed_at"] < tk["submitted_at"]) | (elapsed - tk["resolution_time_hours"]).abs().gt(1)).sum())
    check("T-04", "support_tickets", "closed_at antes de submitted_at ou divergente de resolution_time_hours (>1h)",
          n, len(tk), "nenhum", _status(n, "limitação"))
    n = int((tk["submitted_at"] == tk["submitted_at"].dt.normalize()).sum())
    check("T-05", "support_tickets", "submitted_at só com a data (closed_at tem hora)", n, len(tk),
          "mantido; o tempo de resolução vem de resolution_time_hours (TR-13)", _status(n, "limitação"))
    n = int(tk["satisfaction_score"].isna().sum())
    check("T-06", "support_tickets", "satisfaction_score nulo (sem resposta)", n, len(tk),
          "mantido nulo; coluna has_satisfaction (TR-11)", _status(n, "mantido"))
    answered = tk["satisfaction_score"].dropna()
    n_low = int(answered.isin([1, 2]).sum())
    check("T-07", "support_tickets", "respostas de satisfação; notas 1 e 2 nunca aparecem (escala documentada 1–5)",
          len(answered), len(tk), f"mantido; notas observadas {sorted(answered.unique().tolist())}, {n_low} notas 1–2 (TR-14)",
          "limitação" if n_low == 0 else "ok")
    n = int((~acc["account_id"].isin(tk["account_id"])).sum())
    check("T-08", "accounts", "conta sem nenhum ticket", n, len(acc), "mantida", _status(n, "mantido"))

    # --- churn_events
    n = int(ce["churn_event_id"].duplicated().sum())
    check("C-01", "churn_events", "churn_event_id duplicado", n, len(ce), "nenhum", _status(n, "limitação"))
    n = int((~ce["account_id"].isin(account_ids)).sum())
    check("C-02", "churn_events", "account_id sem conta (órfão)", n, len(ce), "nenhum", _status(n, "limitação"))
    n = int((ce["churn_date"] < ce["account_id"].map(signup)).sum())
    check("C-03", "churn_events", "churn_date antes do signup da conta", n, len(ce), "nenhum", _status(n, "limitação"))
    order = ce.sort_values(["account_id", "churn_date", "churn_event_id"])
    ce["event_seq"] = order.groupby("account_id").cumcount().add(1).reindex(ce.index)
    ce["n_events_account"] = ce.groupby("account_id")["churn_event_id"].transform("size")
    ce["q_same_day_event"] = ce.duplicated(["account_id", "churn_date"], keep=False)
    n = int(ce["q_same_day_event"].sum())
    check("C-04", "churn_events", "dois eventos da mesma conta na mesma data", n, len(ce),
          "mantidos; flag q_same_day_event", _status(n, "mantido"))
    ce["q_reactivation_on_first_event"] = ce["is_reactivation"] & (ce["event_seq"] == 1)
    ce["q_not_reactivation_on_later_event"] = ~ce["is_reactivation"] & (ce["event_seq"] > 1)
    n = int(ce["q_reactivation_on_first_event"].sum())
    check("C-05", "churn_events", "is_reactivation = True no primeiro evento da conta", n, len(ce),
          "is_reactivation preservado; flag; usar event_seq (TR-10)", _status(n, "limitação"))
    n = int(ce["q_not_reactivation_on_later_event"].sum())
    check("C-06", "churn_events", "is_reactivation = False em evento posterior a outro churn", n, len(ce),
          "is_reactivation preservado; flag; usar event_seq (TR-10)", _status(n, "limitação"))
    n = int((ce["reason_code"] == "unknown").sum())
    check("C-07", "churn_events", "reason_code = unknown", n, len(ce), "mantido como categoria própria", _status(n, "mantido"))
    n = int(ce["feedback_text"].isna().sum())
    check("C-08", "churn_events", "feedback_text nulo", n, len(ce), "mantido nulo (sem comentário)", _status(n, "mantido"))
    comparable = ce["feedback_text"].notna() & (ce["reason_code"] != "unknown")
    matches = [r in FEEDBACK_REASONS.get(f, set()) for r, f in zip(ce["reason_code"], ce["feedback_text"].fillna(""))]
    ce["q_feedback_matches_reason"] = pd.array(matches, dtype="boolean")
    ce.loc[~comparable, "q_feedback_matches_reason"] = pd.NA
    n = int((ce["q_feedback_matches_reason"] == False).sum())  # noqa: E712 (NA fica de fora)
    check("C-09", "churn_events", "feedback_text incompatível com reason_code", n, int(comparable.sum()),
          "ambos preservados; flag q_feedback_matches_reason (TR-12)", _status(n, "limitação"))
    ended = sub.loc[~sub["q_is_duplicate"] & sub["end_date"].notna(), ["account_id", "end_date"]]
    gaps = ce[["churn_event_id", "account_id", "churn_date"]].merge(ended, on="account_id", how="left")
    gaps["days"] = (gaps["end_date"] - gaps["churn_date"]).dt.days.abs()
    ce["q_days_to_nearest_subscription_end"] = ce["churn_event_id"].map(gaps.groupby("churn_event_id")["days"].min()).astype("Int64")
    far = ce["q_days_to_nearest_subscription_end"].isna() | (ce["q_days_to_nearest_subscription_end"] > NEAREST_END_TOLERANCE_DAYS)
    n = int(far.sum())
    check("C-10", "churn_events", f"sem fim de assinatura da conta a até {NEAREST_END_TOLERANCE_DAYS} dias do evento",
          n, len(ce), "mantido; coluna q_days_to_nearest_subscription_end (TR-10)", _status(n, "limitação"))
    active_accounts = set(sub.loc[sub["active_at_data_end"], "account_id"])
    churned = set(ce["account_id"])
    n = len(churned & active_accounts)
    check("C-11", "churn_events", f"conta com evento que segue com assinatura ativa em {end.date()}", n, len(churned),
          "mantido; churn de conta não equivale a encerrar todas as assinaturas (TR-10)", _status(n, "limitação"))

    return {"accounts": acc, "subscriptions": sub, "feature_usage": fu,
            "support_tickets": tk, "churn_events": ce}, checks


def _dtype_label(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if isinstance(series.dtype, pd.BooleanDtype):
        return "boolean"
    if pd.api.types.is_bool_dtype(series):
        return "bool"
    if isinstance(series.dtype, pd.Int64Dtype):
        return "Int64"
    if pd.api.types.is_integer_dtype(series):
        return "int64"
    if pd.api.types.is_float_dtype(series):
        return "float64"
    return "str"


def _to_csv_text(df: pd.DataFrame) -> str:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            has_time = (out[col].dropna() != out[col].dropna().dt.normalize()).any()
            out[col] = out[col].dt.strftime("%Y-%m-%d %H:%M:%S" if has_time else "%Y-%m-%d")
    return out.to_csv(index=False, lineterminator="\n")


def write(tables: dict[str, pd.DataFrame], checks: list[dict], raw: dict[str, pd.DataFrame],
          clean_dir: Path, quality_dir: Path, report: Path) -> dict:
    clean_dir.mkdir(parents=True, exist_ok=True)
    quality_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"generated_by": "solution/src/clean_data.py", "pandas": pd.__version__,
                "data_end": str(data_end(raw).date()), "tables": {}}
    for name, df in tables.items():
        data = _to_csv_text(df).encode("utf-8")
        (clean_dir / f"{name}.csv").write_bytes(data)
        manifest["tables"][name] = {
            "rows": len(df), "raw_rows": len(raw[name]),
            "sha256": hashlib.sha256(data).hexdigest(),
            "columns": {c: _dtype_label(df[c]) for c in df.columns},
        }
    (quality_dir / "derived_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pd.DataFrame(checks).to_csv(quality_dir / "checks.csv", index=False, lineterminator="\n")
    report.write_text(render_report(checks, manifest), encoding="utf-8")
    return manifest


def render_report(checks: list[dict], manifest: dict) -> str:
    lines = [
        "# Relatório de qualidade dos dados",
        "",
        "> Gerado por `solution/src/clean_data.py`; não editar à mão. Decisões de tratamento em [data-treatment-log.md](data-treatment-log.md).",
        "",
        f"Fim da observação (última data nas tabelas): **{manifest['data_end']}**. Nenhuma linha removida; valores originais preservados; problemas viram colunas `q_*`.",
        "",
        "| Tabela | Linhas originais | Linhas derivadas | Colunas na base derivada |",
        "|---|---:|---:|---:|",
    ]
    for name, spec in manifest["tables"].items():
        lines.append(f"| {name} | {spec['raw_rows']} | {spec['rows']} | {len(spec['columns'])} |")
    lines += ["", "## Checagens", "", "| ID | Tabela | Checagem | n | de | Tratamento | Status |", "|---|---|---|---:|---:|---|---|"]
    for c in checks:
        lines.append(f"| {c['id']} | {c['table']} | {c['check']} | {c['n']} | {c['total']} | {c['treatment']} | {c['status']} |")
    limits = [c for c in checks if c["status"] == "limitação"]
    lines += ["", "## Limitações sem solução", ""]
    lines += [f"- **{c['id']}**: {c['check']} ({c['n']} de {c['total']})." for c in limits] or ["- nenhuma"]
    return "\n".join(lines) + "\n"


def build(raw_dir: Path = raw_data.RAW_DIR, clean_dir: Path = CLEAN_DIR,
          quality_dir: Path = QUALITY_DIR, report: Path = REPORT) -> dict:
    raw = read_raw(raw_dir)
    tables, checks = clean({t: df.copy() for t, df in raw.items()})
    return write(tables, checks, raw, clean_dir, quality_dir, report)


def load_clean(table: str, clean_dir: Path = CLEAN_DIR,
               manifest_path: Path = QUALITY_DIR / "derived_manifest.json") -> pd.DataFrame:
    columns = json.loads(manifest_path.read_text(encoding="utf-8"))["tables"][table]["columns"]
    dtypes = {c: t for c, t in columns.items() if t != "datetime"}
    df = pd.read_csv(clean_dir / f"{table}.csv", dtype=dtypes, keep_default_na=False, na_values=[""])
    for col, kind in columns.items():
        if kind == "datetime":
            df[col] = pd.to_datetime(df[col], format="ISO8601")
    return df


def main() -> int:
    files = raw_data.load_manifest()["files"]
    problems = raw_data.check(raw_data.RAW_DIR, files)
    if problems:
        print("originais divergem do manifest; rode raw_data.py fetch\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    manifest = build()
    after = raw_data.check(raw_data.RAW_DIR, files)
    if after:
        print("ERRO: originais mudaram durante o build\n  " + "\n  ".join(after), file=sys.stderr)
        return 1
    for name, spec in manifest["tables"].items():
        print(f"{name:16} {spec['raw_rows']:>6} -> {spec['rows']:>6} linhas  {spec['sha256'][:12]}")
    print(f"originais intactos; relatório em {REPORT.relative_to(SUB_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
