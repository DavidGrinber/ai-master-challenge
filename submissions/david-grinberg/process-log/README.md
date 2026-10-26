# Process log

Evidência de como a IA foi usada, uma sessão ou etapa por arquivo. Só registros reais: nada de resultados, exports, revisões, erros ou durações reconstruídos. Justificativas curtas e verificáveis; sem raciocínio interno privado da IA; sem tokens ou segredos.

| Arquivo | Conteúdo |
|---|---|
| `sessions/S-NNN-<tema>.md` | registro da sessão a partir de `TEMPLATE-sessao.md`: objetivo, prompt, ações e comandos, resultado, verificação, decisão do candidato ou revisão pendente, erros e correções, tempo (se medido), commit |
| `sessions/S-NNN-prompt-usuario.md` | prompt longo do usuário, literal |
| `experiments/EXP-NNN.md` | teste de hipótese ou modelo, a partir de `TEMPLATE-experimento.md` |
| `evidence-index.csv` | índice E-NNN → sessão, issue, caminho, estado |
| `time-log.csv` | apenas tempos medidos ou timestamps observados |
| `screenshots/`, `chat-exports/` | capturas e exports reais, quando houver |

## Sessões

| ID | Ferramenta | Issue | Resumo |
|---|---|---|---|
| [S-001](sessions/S-001-planejamento-chatgpt.md) | ChatGPT | DAV-177 | planejamento, roadmap e hipóteses; preservado como veio no kit |
| [S-002](sessions/S-002-claude-code-harness.md) | Claude Code | DAV-178 | fork, branch, revisão das hipóteses, aquisição verificada dos CSVs, harness |

Decisões: [`../docs/decision-log.md`](../docs/decision-log.md). Hipóteses: [`../docs/02-hipoteses.md`](../docs/02-hipoteses.md).
