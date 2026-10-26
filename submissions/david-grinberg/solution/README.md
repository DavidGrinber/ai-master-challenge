# solution/

| Pasta | Conteúdo | Estado |
|---|---|---|
| `data/manifest.json` | origem, versão, licença, tamanho e SHA-256 dos originais | pronto (DAV-178) |
| `data/raw/` | 5 CSVs + README da fonte, somente leitura, fora do Git | baixados e verificados localmente (DAV-178) |
| `data/processed/clean/` | 5 tabelas limpas e tipadas, com flags `q_*`, fora do Git | pronto (DAV-201) |
| `data/processed/snapshots.csv` | conta × fim de mês, features até t e rótulos de churn | pronto (DAV-181) |
| `data/processed/accounts_retrospective.csv` | 1 linha por conta, período todo (só diagnóstico) | pronto (DAV-181) |
| `src/raw_data.py` | `fetch` e `verify` dos originais | pronto (DAV-178) |
| `src/clean_data.py` | gera a base limpa, `checks.csv`, manifest e relatório; `load_clean()` | pronto (DAV-201) |
| `outputs/data_quality/` | `checks.csv` e `derived_manifest.json` (schema e SHA-256) | pronto (DAV-201) |
| `src/analytic_base.py` | snapshots, perfil, reconciliação e dicionário | pronto (DAV-181) |
| `outputs/analytic_base/` | `reconciliation.csv`, `label_counts.csv`, `base_manifest.json` | pronto (DAV-181) |
| `src/` (demais) | preparação, análise, treino e inferência | pendente (DAV-184, DAV-189) |
| `tests/` | testes de `src/` | `test_raw_data.py` (DAV-178), `test_clean_data.py` (DAV-201), `test_analytic_base.py` (DAV-181) |
| `app/` | painel Streamlit | pendente (DAV-194) |
| `models/` | pipeline treinado e versão | pendente (DAV-189) |
| `outputs/` | scores, tabelas e figuras | pendente |

Comandos e regras: [`../CLAUDE.md`](../CLAUDE.md).
