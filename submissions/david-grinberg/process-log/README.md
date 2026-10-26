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
| [S-003](sessions/S-003-auditoria-e-limpeza.md) | Claude Code | DAV-181, DAV-201 | auditoria estrutural; base limpa com flags, relatório de qualidade e registro de tratamento |
| [S-004](sessions/S-004-premissas-e-base-analitica.md) | Claude Code | DAV-181 | premissas P-01 a P-03; snapshots conta × corte e perfil retrospectivo, reconciliados e sem vazamento |
| [S-005](sessions/S-005-revisao-do-tratamento.md) | Claude Code | DAV-181, DAV-201 | revisão do candidato: elegibilidade e tratamentos aprovados; cópias exatas de assinatura passam a contar como legítimas |
| [S-006](sessions/S-006-diagnostico-hipoteses.md) | Claude Code | DAV-184 | pré-registro; H01–H09 testadas; H10 (mecanismo do gerador) explica a subida do churn |
| [S-007](sessions/S-007-modelo.md) | Claude Code | DAV-189 | modelo não supera o ranking por tempo de casa; sem probabilidade; scores da carteira |

Decisões: [`../docs/decision-log.md`](../docs/decision-log.md). Hipóteses: [`../docs/02-hipoteses.md`](../docs/02-hipoteses.md).
