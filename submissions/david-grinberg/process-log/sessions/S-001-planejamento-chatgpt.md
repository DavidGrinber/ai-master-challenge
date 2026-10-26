# S-001 — Preparação do case com ChatGPT
Registro escrito em 2026-10-26T10:57:11-03:00; não é uma transcrição integral da conversa.
Ferramenta: ChatGPT / agente de organização. Identificador exato do modelo não registrado.
Tempo total: não aferido; não estimar como se fosse medido.
Issue: https://linear.app/david-grinberg/issue/DAV-177/00-consolidar-regras-roadmap-e-central-de-evidencias
Prompt do usuário: S-001-prompt-usuario.md.

## Objetivo
Organizar o projeto antes de qualquer análise dos dados e preparar continuidade no Claude Code.

## Ações executadas e verificadas
- Lidos os cinco documentos oficiais preservados em docs/references/ no commit 4aed364d572fabe0f1fff1f0c6f32960b30fe575.
- Inventariados times e projetos no Linear: único time Sparring; criado projeto separado para o case.
- Criados seis marcos, três documentos e 24 tarefas com escopo, aceite, evidências e dependências.
- Conferidos o total de tarefas, os marcos e os vínculos das tarefas de contrato temporal e PR.
- Preparados este kit e modelos vazios de logs para execução futura.
- Nenhum CSV foi adquirido ou examinado; nenhuma hipótese testada; nenhum modelo treinado; nenhum painel implementado. Não houve fork, branch ou PR criado neste fluxo.

## Decisões e contribuições
- Usuário: objetivo do case, ferramentas, painel/modelo, hipóteses iniciais e exigência de logs.
- ChatGPT: decomposição, ampliação H05–H09, plano temporal, critérios de validação, escopo MVP e modelos de evidência.
- Revisão do candidato sobre essas propostas: pendente.
- Explorações anteriores fora deste fluxo, se houver: declarar depois; não alegar estudo cego ou inventar registros retroativos.

## Dificuldades realmente observadas
- A leitura pelo serviço de busca retornou DisabledError. O conteúdo oficial foi lido pela API pública do GitHub, fixando o commit.
- A consulta ampla de projetos no Linear excedeu complexidade. Uma consulta com seleção de campos retornou o inventário.
- A consulta às notas compartilhadas de agentes retornou “Tool get_agent_context not found”. Organização seguiu as regras oficiais e o inventário do workspace.
Essas são dificuldades operacionais de preparação, não erros de análise do churn.

## Evidências
E-001: documentos oficiais e commit, docs/references/.
E-002: projeto, três documentos e tarefas, docs/roadmap-linear.json e links dos documentos.
E-003: kit de continuidade e arquivos de logs, sem preencher resultados futuros.
Sem screenshots ou exports de conversa fabricados.

## Próximo passo
DAV-178: setup local com o primeiro prompt; DAV-179: revisão do registro de hipóteses; depois aquisição/auditoria.
Commit: ainda não existe, pois o fork será preparado no próximo passo.
