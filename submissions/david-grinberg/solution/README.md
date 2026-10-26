# solution/

| Pasta | Conteúdo | Estado |
|---|---|---|
| `data/manifest.json` | origem, versão, licença, tamanho e SHA-256 dos originais | pronto (DAV-178) |
| `data/raw/` | 5 CSVs + README da fonte, somente leitura, fora do Git | baixados e verificados localmente (DAV-178) |
| `data/processed/` | bases derivadas geradas por script, fora do Git | pendente (DAV-181) |
| `src/raw_data.py` | `fetch` e `verify` dos originais | pronto (DAV-178) |
| `src/` (demais) | preparação, análise, treino e inferência | pendente (DAV-181, DAV-184, DAV-189) |
| `tests/` | testes de `src/` | `test_raw_data.py` (DAV-178) |
| `app/` | painel Streamlit | pendente (DAV-194) |
| `models/` | pipeline treinado e versão | pendente (DAV-189) |
| `outputs/` | scores, tabelas e figuras | pendente |

Comandos e regras: [`../CLAUDE.md`](../CLAUDE.md).
