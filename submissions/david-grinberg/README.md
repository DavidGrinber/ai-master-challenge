# Submissão — David Grinberg — Challenge 001

## Sobre mim

- **Nome:** David Grinberg
- **LinkedIn:** _pendente_
- **Challenge escolhido:** 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

_Pendente (DAV-198). Nenhuma análise de churn foi executada até aqui._



---

## Solução

_Sua análise, protótipo, redesign ou o que o challenge pedir. Use o formato que melhor comunicar._

### Abordagem

_Plano, ainda não executado:_ cruzar as cinco tabelas por conta e data de corte; testar as hipóteses pré-registradas em [`docs/02-hipoteses.md`](docs/02-hipoteses.md); construir um modelo de churn com validação temporal e sem vazamento; entregar ao CS um painel local que prioriza e explica contas. Etapas e critérios em [`CLAUDE.md`](CLAUDE.md).

### Resultados / Findings

_Pendente (DAV-184 e DAV-189)._

### Recomendações

_Pendente (DAV-198)._

### Limitações

- Os dados são simulados: a fonte declara que foram gerados com Python e ChatGPT ([manifest](solution/data/manifest.json)). Conclusões valem para este dataset, não para uma operação real.
- O candidato abriu os CSVs e usou IA sobre os dados antes deste fluxo; as hipóteses não são um registro cego ([DEC-008](docs/decision-log.md)).
- _Demais limitações: pendentes._

### Como reproduzir

Requer Python 3.12. Comandos a partir de `submissions/david-grinberg/`:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # ou: uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python solution/src/raw_data.py fetch      # baixa o pacote público do Kaggle (sem login) para solution/data/raw/
.venv/bin/python solution/src/raw_data.py verify     # confere tamanho e SHA-256 dos 6 arquivos contra o manifest
.venv/bin/python -m pytest                           # testes
```

Se o download automático falhar, baixe o zip na [página do dataset](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) e rode `.venv/bin/python solution/src/raw_data.py fetch --archive caminho/do/arquivo.zip`.

_Preparação da base, treino, geração de scores e painel: pendentes (DAV-181, DAV-189, DAV-194)._

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| ChatGPT | Planejamento inicial: roadmap no Linear, ampliação das hipóteses (H05–H09) e modelos de log ([S-001](process-log/sessions/S-001-planejamento-chatgpt.md)) |
| Claude Code | Fork, branch, ambiente, aquisição verificada dos CSVs e harness do projeto ([S-002](process-log/sessions/S-002-claude-code-harness.md)) |
| Linear | Controle de tarefas, aceite e decisões resumidas |

### Workflow

1. Planejamento com ChatGPT antes de qualquer análise: escopo, roadmap e hipóteses (S-001).
2. Revisão das hipóteses pelo candidato e preparação do repositório, ambiente e dados com Claude Code (S-002).
3. _Pendente: análise, modelo, painel e relatório._

### Onde a IA errou e como corrigi

_Pendente._



### O que eu adicionei que a IA sozinha não faria

_Pendente._



---

## Evidências

- [ ] Screenshots das conversas com IA
- [ ] Screen recording do workflow
- [ ] Chat exports
- [x] Git history (commits por entrega nesta branch)
- [x] Outro: registros por sessão em [`process-log/`](process-log/) e decisões em [`docs/decision-log.md`](docs/decision-log.md)

---

_Submissão enviada em: [pendente — DAV-199]_
