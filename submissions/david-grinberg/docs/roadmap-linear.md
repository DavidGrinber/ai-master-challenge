# Roadmap exportado do Linear

> **Snapshot do kit S-001 (ChatGPT, 26/10/2026, roadmap de 24 issues).** Preservado como registro do planejamento. Versão vigente no Linear: roadmap consolidado em 8 issues ativas; a DAV-178 passou a incluir a revisão das hipóteses e a aquisição dos CSVs; as operações de Git/GitHub cabem ao Claude Code. Regras em vigor: `../CLAUDE.md`.


Projeto: https://linear.app/david-grinberg/project/g4-ravenstack-diagnostico-de-churn-e-cs-1a6781700e39
Exportação: 2026-10-26T10:57:11-03:00. Snapshot para a banca; o Linear permanece o controle vivo.

| Ordem | Issue | Marco | Tarefa | Depende de | Estado |
|---|---|---|---|---|---|
| 00 | [DAV-177](https://linear.app/david-grinberg/issue/DAV-177/00-consolidar-regras-roadmap-e-central-de-evidencias) | M0 | Consolidar regras, roadmap e central de evidências | — | Done |
| 01 | [DAV-178](https://linear.app/david-grinberg/issue/DAV-178/01-preparar-fork-branch-ambiente-e-estrutura-da-submissao) | M0 | Preparar fork, branch, ambiente e estrutura da submissão | DAV-177 | Todo |
| 02 | [DAV-179](https://linear.app/david-grinberg/issue/DAV-179/02-revisar-e-fixar-hipoteses-e-decisoes-pre-analise) | M0 | Revisar e fixar hipóteses e decisões pré-análise | DAV-177 | Todo |
| 03 | [DAV-180](https://linear.app/david-grinberg/issue/DAV-180/03-adquirir-as-5-tabelas-e-documentar-origem-e-schemas) | M1 | Adquirir as 5 tabelas e documentar origem e schemas | DAV-178, DAV-179 | Backlog |
| 04 | [DAV-181](https://linear.app/david-grinberg/issue/DAV-181/04-auditar-cardinalidade-qualidade-e-reconciliacao-dos-joins) | M1 | Auditar cardinalidade, qualidade e reconciliação dos joins | DAV-180 | Backlog |
| 05 | [DAV-182](https://linear.app/david-grinberg/issue/DAV-182/05-fixar-alvo-elegibilidade-horizonte-e-validacao-temporal) | M1 | Fixar alvo, elegibilidade, horizonte e validação temporal | DAV-180, DAV-181 | Backlog |
| 06 | [DAV-183](https://linear.app/david-grinberg/issue/DAV-183/06-construir-snapshots-e-features-disponiveis-no-instante-de-decisao) | M1 | Construir snapshots e features disponíveis no instante de decisão | DAV-181, DAV-182 | Backlog |
| 07 | [DAV-184](https://linear.app/david-grinberg/issue/DAV-184/07-reconciliar-churn-receita-uso-e-satisfacao-por-coorte) | M2 | Reconciliar churn, receita, uso e satisfação por coorte | DAV-183 | Backlog |
| 08 | [DAV-185](https://linear.app/david-grinberg/issue/DAV-185/08-testar-h01-queda-de-uso-antecedencia-e-falsos-alertas) | M2 | Testar H01: queda de uso, antecedência e falsos alertas | DAV-183 | Backlog |
| 09 | [DAV-186](https://linear.app/david-grinberg/issue/DAV-186/09-testar-h02-h03-suporte-friccao-tecnica-e-churn-posterior) | M2 | Testar H02–H03: suporte, fricção técnica e churn posterior | DAV-183 | Backlog |
| 10 | [DAV-187](https://linear.app/david-grinberg/issue/DAV-187/10-testar-h04-perfis-adocao-e-proxies-de-valor) | M2 | Testar H04: perfis, adoção e proxies de valor | DAV-183 | Backlog |
| 11 | [DAV-188](https://linear.app/david-grinberg/issue/DAV-188/11-examinar-alternativas-e-sintetizar-explicacoes-sustentadas) | M2 | Examinar alternativas e sintetizar explicações sustentadas | DAV-184, DAV-185, DAV-186, DAV-187 | Backlog |
| 12 | [DAV-189](https://linear.app/david-grinberg/issue/DAV-189/12-criar-referencias-e-primeiro-modelo-interpretavel) | M3 | Criar referências e primeiro modelo interpretável | DAV-183 | Backlog |
| 13 | [DAV-190](https://linear.app/david-grinberg/issue/DAV-190/13-comparar-challenger-e-validar-generalizacao-sem-vazamento) | M3 | Comparar challenger e validar generalização sem vazamento | DAV-189 | Backlog |
| 14 | [DAV-191](https://linear.app/david-grinberg/issue/DAV-191/14-definir-calibracao-limiar-e-politica-de-acionamento-do-cs) | M3 | Definir calibração, limiar e política de acionamento do CS | DAV-185, DAV-188, DAV-190 | Backlog |
| 15 | [DAV-192](https://linear.app/david-grinberg/issue/DAV-192/15-empacotar-inferencia-scores-e-model-card) | M3 | Empacotar inferência, scores e model card | DAV-190, DAV-191 | Backlog |
| 16 | [DAV-193](https://linear.app/david-grinberg/issue/DAV-193/16-definir-fluxo-e-contrato-do-painel-para-uso-por-cs) | M4 | Definir fluxo e contrato do painel para uso por CS | DAV-182 | Backlog |
| 17 | [DAV-194](https://linear.app/david-grinberg/issue/DAV-194/17-implementar-fila-priorizada-e-investigacao-de-contas) | M4 | Implementar fila priorizada e investigação de contas | DAV-192, DAV-193 | Backlog |
| 18 | [DAV-195](https://linear.app/david-grinberg/issue/DAV-195/18-adicionar-visao-diagnostica-playbooks-e-exportacao) | M4 | Adicionar visão diagnóstica, playbooks e exportação | DAV-188, DAV-191, DAV-194 | Backlog |
| 19 | [DAV-196](https://linear.app/david-grinberg/issue/DAV-196/19-validar-painel-com-cenarios-operacionais-e-dados-extremos) | M4 | Validar painel com cenários operacionais e dados extremos | DAV-195 | Backlog |
| 20 | [DAV-197](https://linear.app/david-grinberg/issue/DAV-197/20-priorizar-acoes-e-estimar-impacto-em-cenarios-explicitos) | M5 | Priorizar ações e estimar impacto em cenários explícitos | DAV-188, DAV-191 | Backlog |
| 21 | [DAV-198](https://linear.app/david-grinberg/issue/DAV-198/21-redigir-diagnostico-executivo-e-responder-as-3-perguntas) | M5 | Redigir diagnóstico executivo e responder às 3 perguntas | DAV-196, DAV-197 | Backlog |
| 22 | [DAV-199](https://linear.app/david-grinberg/issue/DAV-199/22-reproduzir-entrega-e-auditar-process-log-e-escopo-do-pr) | M5 | Reproduzir entrega e auditar process-log e escopo do PR | DAV-198 | Backlog |
| 23 | [DAV-200](https://linear.app/david-grinberg/issue/DAV-200/23-preparar-e-abrir-pr-no-formato-oficial) | M5 | Preparar e abrir PR no formato oficial | DAV-199 | Backlog |
