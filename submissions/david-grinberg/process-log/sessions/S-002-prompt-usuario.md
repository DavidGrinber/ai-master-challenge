# S-002 — Prompt do usuário (literal)
Colado pelo candidato no Claude Code em 2026-10-26, como mensagem única, sem texto adicional. Corresponde à seção "Prompt inicial adaptado" do documento 03 no Linear.

---

Você é o primeiro agente de desenvolvimento do case G4 — RavenStack / Diagnóstico de Churn. Sua primeira tarefa é preparar um harness simples: estrutura da submissão, instruções dos agentes, ambiente, comandos e registro do processo.

O resultado final será um diagnóstico baseado nas cinco tabelas, um modelo preditivo validado e um painel interativo que ajude o CS a priorizar e investigar contas. Nesta execução, entregue somente a preparação.

Responsabilidade pelo GitHub e preparação do repositório

Toda a execução de Git e GitHub é responsabilidade do Claude Code: conferir acessos, preparar fork e clone, configurar remotes, criar a branch, registrar commits, enviar ao fork e abrir o PR na etapa final. O candidato acompanha o trabalho; não deve receber essas operações como tarefas manuais.

Repositório oficial: https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge

- Comece inspecionando a pasta atual e eventuais repositórios existentes. Reaproveite o clone correto quando houver. Se a sessão começar em uma pasta vazia, prepare uma pasta local apropriada para o case, sem alterar outros projetos.
- Confira Git e GitHub CLI ou a integração GitHub disponível, a autenticação e a conta ativa. Use a conta efetivamente autenticada; não invente usuário, nome ou e-mail. Quando uma autenticação exigir a presença do usuário, solicite somente essa intervenção e prossiga após a conexão. Nunca registre tokens nos logs.
- Se os arquivos oficiais ainda não estiverem locais, leia-os remotamente no repositório oficial antes de implementar o harness.
- Localize o fork da conta autenticada e reutilize-o; se não existir, crie o fork. Clone-o localmente ou reutilize um clone válido. Confira origin apontando para o fork e upstream apontando para o repositório oficial.
- Identifique o nome/slug do candidato pelas informações disponíveis; confirme apenas se estiver indefinido ou ambíguo. Crie ou reutilize submission/<slug> e mantenha todos os arquivos novos ou modificados em submissions/<slug>/.
- Desenvolva e verifique localmente. Registre commits por entrega, inclua apenas os arquivos pertinentes da pasta de submissão e faça push da branch para o fork. Confira o resultado e registre URL do fork, branch e SHA. Não sobrescreva alterações existentes nem use force-push.
- Na DAV-178, entregue fork/clone/branch preparados e o primeiro commit do harness enviado ao fork, quando o acesso permitir. Informe qualquer bloqueio real; não declare uma operação concluída sem verificá-la.
- Na DAV-199, depois de validar a entrega, faça o push final e abra o PR do fork para main do repositório oficial. Use o título [Submission] Nome — Challenge 001, o template e as evidências exigidos; confira que o diff altera somente submissions/<slug>/. Se já existir o PR do candidato, atualize a mesma branch e o mesmo PR. Registre a URL real.
- O PR de submissão é a entrega final. Nesta primeira execução, faça somente a preparação do repositório e do harness, sem iniciar análises ou abrir o PR.

Antes de implementar o harness, leia os documentos abaixo. Se ainda não existir clone, consulte os arquivos remotamente no repositório oficial durante a preparação do GitHub:

- No repositório: README.md, CONTRIBUTING.md, submission-guide.md, challenges/data-001-churn/README.md e templates/submission-template.md.
- No projeto “G4 — RavenStack | Diagnóstico de churn e CS”, no Linear:
  - 01 — Central do case e critérios de entrega.
  - 02 — Hipóteses pré-análise e protocolo de validação.
  - 03 — Claude Code, logs e definição de concluído.
  - As oito issues ativas: DAV-178, DAV-181, DAV-184, DAV-189, DAV-193, DAV-194, DAV-198 e DAV-199.
- Ignore issues Canceled ou Duplicate. DAV-177 é o registro histórico do planejamento inicial, já concluído.

Se o Linear estiver indisponível, use os documentos correspondentes do kit e registre essa limitação. Se também faltarem esses documentos, registre o impedimento sem inventar requisitos.

Execute:

1. Execute a preparação de GitHub descrita nas instruções de responsabilidade: confira ferramentas e conta autenticada, reutilize ou crie o fork, prepare o clone local, remotes e branch submission/<slug>. Você deve executar essas operações, sem delegá-las ao candidato. Preserve outros projetos e mantenha a implementação em submissions/<slug>/.
2. Trabalhe no checklist da DAV-178. Revise as hipóteses iniciais com o candidato e registre sua origem antes da análise. Aproveite as oito issues existentes. Se encontrar uma lacuna, descreva-a no fechamento; não crie novas issues nesta execução.
3. Prepare uma estrutura mínima dentro da pasta da submissão:
   - docs/: decisões e documentação.
   - solution/data/raw/: os cinco CSVs originais.
   - solution/data/processed/: bases derivadas.
   - solution/src/: preparação, análise, treino e inferência.
   - solution/app/: painel interativo.
   - solution/models/ e solution/outputs/: modelo e resultados.
   - process-log/: prompts, verificações e decisões reais.
     Crie testes quando houver comportamento que precise ser verificado; não acrescente estrutura sem uso.
4. Confira a disponibilidade dos cinco arquivos ravenstack_accounts.csv, ravenstack_subscriptions.csv, ravenstack_feature_usage.csv, ravenstack_support_tickets.csv e ravenstack_churn_events.csv. Preserve os originais. Registre caminho, origem, versão e hash quando verificáveis; marque o que estiver desconhecido. Se faltarem arquivos, registre como obtê-los e deixe essa pendência explícita. O harness pode ser entregue com pendências de dados, mas a issue não estará concluída enquanto seu aceite estiver incompleto.
5. Use Python como base. A proposta inicial é pandas para dados, scikit-learn para o modelo e Streamlit para o painel. Confira compatibilidade no ambiente e instale apenas o necessário nesta etapa. Confirme as decisões com base no escopo; não introduza infraestrutura adicional sem justificativa concreta.
6. Crie ou atualize:
   - CLAUDE.md: escopo, arquitetura simples, regras dos dados, comandos, critérios de conclusão e instruções do Claude.
   - README.md: preserve o formato do template oficial e acrescente instruções reproduzíveis; resultados ainda não produzidos ficam como pendentes.
   - Dependências do ambiente e .gitignore, protegendo credenciais, ambiente virtual e dados locais conforme a política documentada.
   - .env.example somente se houver variáveis realmente necessárias, sem credenciais.
7. Defina o registro do processo de forma simples: um arquivo por sessão ou etapa, com objetivo, prompt relevante, ações e comandos executados, resultado observado, verificação, decisão do candidato ou revisão pendente, erros reais e correções, tempo quando medido e commit. Preserve o registro do planejamento com ChatGPT. Não invente resultados, exports, revisões, erros ou durações. Basta uma justificativa curta e verificável das decisões; não solicite raciocínio interno privado da IA.
8. Registre no CLAUDE.md o fluxo futuro:
   - DAV-181 prepara os dados das cinco tabelas sem duplicar números.
   - DAV-184 investiga churn e testa hipóteses.
   - DAV-189 define o alvo temporal, constrói e avalia o modelo usando somente informação disponível antes da previsão; salva o pipeline e gera scores reproduzíveis.
   - DAV-193 define as decisões e a experiência do CS.
   - DAV-194 constrói o painel conectado ao modelo ou aos scores gerados por ele: carteira priorizada, filtros, ficha da conta, sinais, histórico disponível, ação sugerida e exportação.
   - DAV-198 consolida o diagnóstico e as recomendações.
   - DAV-199 valida a solução e prepara a submissão por PR.
     O painel deve mostrar a data de referência e a versão do modelo. Probabilidades exigem validação apropriada; correlação e importância de variável não comprovam causa.
9. Defina o fluxo de trabalho com um único agente:

- Claude Code implementa, executa as verificações apropriadas, corrige os problemas encontrados e entrega commit, issue e evidências.
- O candidato acompanha os resultados e valida as interpretações e decisões de negócio.
- Uma issue fica Done após seus critérios de aceite e as verificações pertinentes. Não há revisão obrigatória por outro agente.
- Registrar verificações faz parte da execução da issue; não criar uma etapa separada de QA.

10. Execute apenas as verificações pertinentes ao harness. Documente os comandos realmente implementados e executados; comandos futuros ficam claramente marcados como planejados. Ao terminar, informe arquivos criados, decisões, verificações e saídas observadas, pendências, commit e próxima issue recomendada.

Nesta primeira execução, pare antes de cruzar os dados, calcular resultados de churn, testar hipóteses, treinar modelos ou construir o painel. Entregue o harness e o inventário dos insumos. A implementação seguirá pelas issues.

Entrega final

Diagnóstico que responde às três perguntas, modelo avaliado, painel reproduzível, recomendações e evidências. O PR deve seguir o template oficial e alterar apenas a pasta do candidato.
