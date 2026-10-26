# Decisões
Registro criado em 2026-10-26T10:57:11-03:00. Propostas técnicas permanecem pendentes de revisão pelo candidato.

| ID | Origem / estado | Decisão ou proposta | Justificativa e evidência |
|---|---|---|---|
| DEC-001 | Usuário / diretriz recebida | Organizar tarefas no Linear e logs antes de iniciar análise; usar Claude Code depois; entregar diagnóstico, modelo e painel CS. | Solicitação original em process-log/sessions/S-001-prompt-usuario.md. |
| DEC-002 | ChatGPT / execução de organização | Criar projeto próprio no único time disponível, Sparring; 6 marcos e 24 tarefas. | Inventário do Linear e roadmap exportado. Nenhum projeto anterior editado. |
| DEC-003 | ChatGPT / proposta pendente | Usar Python, pandas, scikit-learn e Streamlit para MVP local. | Opção de escopo pequeno; só fixar após setup e auditoria de dados. |
| DEC-004 | ChatGPT / proposta pendente | Avaliar horizonte de 30 dias e janelas 7/14/30 dias. | Parâmetros candidatos, sem teste ou aprovação implícita. |
| DEC-005 | Regras do desafio / incorporada ao plano | Entregar somente por PR, com process log e diff restrito à pasta do candidato. | Regras oficiais no commit fixado, docs/references/. |
| DEC-006 | ChatGPT / guardrail incorporado | Não publicar probabilidade futura com dados pós-evento nem apresentar correlação como causa comprovada. | Critérios analíticos do plano, a verificar na execução. |
| DEC-007 | Candidato / decidido 2026-10-26 (DAV-178) | Aprovar H01–H09 como registro pré-análise, mantendo a origem U/P. | Resposta do candidato na sessão S-002, antes da leitura dos dados. Texto fixado no commit 930e594; revisão em docs/02-hipoteses.md. |
| DEC-008 | Candidato / declarado 2026-10-26 (DAV-178) | Declarar exploração anterior: o candidato abriu os CSVs e usou IA sobre os dados antes deste fluxo. | Resposta na S-002. Detalhes (quando, ferramenta, o que viu) pendentes. Consequência: as hipóteses não são cegas; registrar como exploratórias as que surgirem dos dados (H10+). |
| DEC-009 | Claude Code / implementado, revisão do candidato pendente | Python 3.12 + pandas 3.0.6, scikit-learn 1.9.1, Streamlit 1.65.0 e pytest 9.1.1, com lock universal em requirements.txt (versões publicadas até 12/10/2026). Python 3.12 obtido localmente com uv 0.13.0. | O Python do sistema (3.9.6) está fora de suporte. Imports conferidos no venv; caminho com pip puro conferido com `pip install --dry-run`. Confirma DEC-003 sem infraestrutura adicional. |
| DEC-010 | Kit S-001 / política mantida (DAV-178) | Não versionar `data/raw/` e `data/processed/`; versionar `data/manifest.json` (hashes) e `src/raw_data.py` (fetch/verify). Originais em modo somente leitura. | Licença MIT verificada na fonte; pacote de ~2 MB, com download público sem login conferido duas vezes com bytes idênticos. Reavaliar na DAV-199 se convém incluir os CSVs no PR. |
| DEC-011 | Claude Code / implementado | Fork DavidGrinber/ai-master-challenge; origin = fork, upstream = oficial (push desabilitado); branch submission/david-grinberg; identidade local David Grinberg + e-mail noreply da conta GitHub; staging via scripts/stage.sh. | O .gitignore raiz oficial ignora `submissions/`; o script aplica o .gitignore da pasta antes de `git add -f` e falha com qualquer arquivo preparado fora dela. |

## Modelo para próxima decisão
ID; data/fuso; issue; pergunta; opções consideradas; evidências; decisão humana ou proposta pendente; justificativa curta; consequência; commit.
