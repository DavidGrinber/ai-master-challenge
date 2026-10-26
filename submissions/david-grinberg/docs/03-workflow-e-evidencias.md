# Execução e evidências

> **Snapshot do kit S-001 (ChatGPT, 26/10/2026, roadmap de 24 issues).** Preservado como registro do planejamento. Versão vigente no Linear: roadmap consolidado em 8 issues ativas; a DAV-178 passou a incluir a revisão das hipóteses e a aquisição dos CSVs; as operações de Git/GitHub cabem ao Claude Code. Regras em vigor: `../CLAUDE.md`.


## Fontes de verdade
- Linear: ordem, escopo, dependências, status e resumo das decisões.
- Fork Git: arquivos oficiais da entrega; código, documentos, logs, exports e artefatos pequenos.
- Claude Code: ambiente de execução e colaboração do candidato, a iniciar depois desta preparação.
Links privados do Linear não bastam como evidência para a banca: exportar o roteiro e as decisões para a pasta da submissão.

## Estrutura-alvo
submissions/<slug-do-candidato>/
  README.md
  CLAUDE.md
  .gitignore
  docs/
    01-central-do-case.md
    02-hipoteses.md
    03-workflow-e-evidencias.md
    data-contract.md
    decision-log.md
    model-card.md
    roadmap-linear.json
  solution/
    data/raw/           # não versionar bytes por padrão; origem/checksums no manifest
    data/processed/
    src/
    app/
    models/
    outputs/
  process-log/
    README.md
    sessions/
    screenshots/
    chat-exports/
    experiments/
    evidence-index.csv
    time-log.csv

Usar requirements/lockfile e comandos reais após escolher ambiente. Não criar dependências fictícias. Não editar arquivos fora da pasta de submissão.

## Identificadores e rastreabilidade
Sessão S-001+, hipótese H01+, decisão DEC-001+, experimento EXP-001+, evidência E-001+. Cada registro inclui task Linear, timestamp com fuso (America/Sao_Paulo), versão dos dados e referência de código quando disponível.
Usar data real; não retroagir sessões. Separar “planejado” de “executado”. O planejamento atual foi apoiado por ChatGPT; Claude Code ainda não foi usado neste fluxo.

## Antes de cada tarefa
1. Ler issue, aceite, dependências e documentos.
2. Registrar objetivo/pergunta, hipótese e plano de verificação.
3. Salvar o prompt real e a resposta ou export relevante em process-log/sessions/ ou chat-exports/.
4. Registrar ferramenta e modelo somente quando observável; do contrário, “não registrado”. Nunca salvar chaves, tokens ou configuração privada.
5. Registrar horário de início no time-log. Não pedir à IA que invente tempo gasto.

## Ao concluir
- Evidência: arquivo/consulta/figura, identificador E, fonte e versão; n, denominador, período e definição quando houver métricas.
- Verificação: comando e saída observada; confronto por conta/amostra, totais ou baseline pertinente.
- Decisão: o que o candidato aceitou, mudou ou rejeitou e por quê, em justificativa curta apoiada em evidência.
- Erros/limites: registrar somente os que de fato ocorreram, com correção e reteste.
- Tempo real, próximo passo e commit.
- Comentário de fechamento no Linear com links para arquivos e commit; Done só quando o aceite estiver verificado. Se acesso ao Linear não estiver disponível no Claude Code, gerar o texto de atualização e o candidato atualiza manualmente.

Não é necessário expor raciocínio interno privado da IA; registrar decisões, justificativas concisas, ações verificáveis e evidências reais.

## Template de sessão
ID / tarefa Linear / data e fuso / ator e ferramenta / modelo observado:
Pergunta e hipótese:
Insumos e versões:
Prompt real e referência da resposta:
Ações e comandos executados:
Resultado observado:
Verificação e evidência:
Decisão humana (pendente até revisão):
Erros observados e correções:
Tempo real e próximo passo:
Commit associado (se ainda não existir, pendente):

## Template de experimento
EXP / issue / hipóteses / pergunta / grão / população / features permitidas / target e H / versão dos dados / commit / seed / split / configuração / baseline / métricas treino-validação-teste / incerteza / vazamento auditado / resultado / decisão.
Não preencher números antes da execução.

## Definição de concluído por tarefa
Aceite específico atendido + artefatos salvos + verificação adequada + log real + decisão/revisão quando necessária + referência de commit e atualização no Linear.
Não marcar análise concluída só porque código rodou. Não chamar indicador de probabilidade se só há score sem calibração validada.

## Fluxo do painel
Fila de contas ativas elegíveis → filtros de segmento/plano → risco ou score claramente rotulado e MRR separado → ficha da conta com sinais e evolução → playbook sugerido → exportação de priorização.
Exibir data de referência, janela prevista, versão do modelo, motivo do sinal e limitações.
Status de contato pode ser manual; só prometer persistência se realmente implementada. Não simular integração com CRM ou envio a clientes.

## Política de seleção do modelo
Começar com prevalência, regra simples de queda e regressão logística; comparar no máximo um challenger tabular se o orçamento permitir.
Validação temporal e teste reservado, PR-AUC com prevalência, precision@K/recall@K, lift e MRR coberto. ROC-AUC complementar; acurácia sozinha não basta.
Checar calibração/Brier se houver probabilidades; escolher limiar na validação por capacidade/custo. Exibir score relativo se probabilidade não for confiável.
Modelo melhor deve justificar complexidade. Evidência de não superar baseline é resultado válido e exige decisão explícita.

## Primeiro prompt para Claude Code — apenas setup
“Vamos iniciar o Challenge 001 da G4. Ainda não faça análise exploratória, não baixe CSVs, não treine modelos e não construa o painel.
Leia os READMEs oficiais, CONTRIBUTING.md, submission-guide.md, template de submissão e os documentos desta preparação.
Confira o usuário/caminho do fork e o slug do candidato antes de criar branch/pasta; confirme por inspeção Git a branch submission/<slug> e a restrição de alterações a submissions/<slug>/.
Trabalhe apenas na tarefa de setup indicada no roadmap. Prepare o ambiente mínimo, a estrutura e os modelos de log dentro da pasta permitida. Preserve os documentos e o registro de planejamento com ChatGPT.
Registre este prompt, as ações executadas, os comandos e a saída observada no process-log. Não invente revisão humana, resultados, erros, tempo ou commits.
Mostre um resumo do setup verificado, pendências e arquivos alterados. Pare antes da aquisição/auditoria dos dados. As hipóteses precisam estar registradas e revisadas pelo candidato antes de avançar.”

## Entrega final
README conforme template oficial; relatório curto; código e setup; dataset manifest sem segredos; artefatos de inferência; model card; painel reproduzível; playbook; evidências acessíveis no PR.
Verificação final: ambiente limpo, previsões offline versus painel, diff apenas na pasta permitida, ausência de segredos e arquivos pesados; dados/licença verificadas; nenhum resultado inventado.


Documento no Linear: https://linear.app/david-grinberg/document/03-claude-code-logs-e-definicao-de-concluido-779de02c1c74
