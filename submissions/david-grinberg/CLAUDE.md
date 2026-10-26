# CLAUDE.md — David Grinberg · Challenge 001 (RavenStack / churn)

Abra o Claude Code **nesta pasta** (`submissions/david-grinberg/`). Se a sessão começar na raiz do fork, leia este arquivo antes de qualquer ação.
Leia também, conforme a tarefa: `docs/02-hipoteses.md` (hipóteses e protocolo), `docs/decision-log.md`, a issue do Linear em execução e as regras oficiais em `docs/references/`.

## Escopo

- Entrega final: diagnóstico que responde às 3 perguntas do challenge (o que causa o churn, quais segmentos/contas estão em risco, o que fazer, com prioridade e impacto estimado), cruzando as 5 tabelas; modelo preditivo validado sem vazamento; painel local para o CS priorizar e investigar contas; process-log real; um único PR ao repositório oficial.
- Fontes de verdade: Linear, projeto "G4 — RavenStack | Diagnóstico de churn e CS" (tarefas, aceite, decisões resumidas); este fork (código, relatório, logs, evidências). Regras oficiais no commit `4aed364` do upstream; revalidar antes do PR.
- Somente arquivos dentro de `submissions/david-grinberg/`. Nunca alterar arquivos fora desta pasta, nem para acomodar a aplicação.
- Fora do MVP: CRM, envio automático de mensagens, autenticação, retreinamento contínuo, plataforma de MLOps, hospedagem obrigatória. Infraestrutura nova só com justificativa concreta registrada no decision-log.

## Arquitetura

```
README.md              entrega no formato do template oficial
docs/                  hipóteses, contrato de dados, model card, decisões, referências oficiais
solution/
  data/manifest.json   origem, versão, licença, tamanho e SHA-256 dos originais (versionado)
  data/raw/            5 CSVs originais + README da fonte (local, somente leitura, não versionado)
  data/processed/      bases derivadas geradas por script (local, não versionado)
    clean/             5 tabelas limpas e tipadas com flags q_* (DAV-201); ler com clean_data.load_clean()
    snapshots.csv      conta × fim de mês: features até t + rótulos churn_next_{30,60,90}d (DAV-181)
    accounts_retrospective.csv  1 linha por conta, período todo; só diagnóstico, nunca feature
  src/                 preparação, análise, treino e inferência (scripts Python)
  tests/               testes do comportamento que precisa ser verificado
  app/                 painel Streamlit (DAV-194)
  models/              pipeline treinado + versão (DAV-189)
  outputs/             scores, tabelas e figuras usadas no relatório
    data_quality/      checks.csv + derived_manifest.json (schema e SHA-256 da base limpa)
    analytic_base/     reconciliation.csv, label_counts.csv, base_manifest.json (schema, SHA-256, linhagem)
process-log/           registros por sessão, experimentos, evidências e tempo
scripts/stage.sh       git add seguro para esta pasta
```

Fluxo: `raw/` → `clean_data.py` → `processed/clean/` → `analytic_base.py` → `processed/snapshots.csv` e `accounts_retrospective.csv` → `src/` treina e avalia → `models/` → `src/` gera scores → `outputs/` (account_id, data de referência, horizonte, versão do modelo, sinais) → `app/` lê `processed/` e `outputs/`. O painel não treina modelo.

## Dados

- Fonte: Kaggle `rivalytics/saas-subscription-and-churn-analytics-dataset`, versão 1 (21/07/2025), licença MIT. **Dados simulados**: a própria fonte diz que foram gerados com Python e ChatGPT. Isso limita a generalização e deve constar no relatório.
- `raw/` guarda os originais em modo somente leitura. Nunca editar, renomear, reformatar ou sobrescrever. Todo derivado vai para `processed/` e é gerado por script.
- Política de versionamento (kit S-001, mantida em DEC-010): `raw/` e `processed/` ficam fora do Git; o manifest e o script reproduzem os arquivos. Revisar na DAV-199.
- Regras analíticas (detalhe em `docs/02-hipoteses.md`):
  - Definir grão, chaves e joins antes de agregar; não multiplicar contas, eventos ou receita em joins.
  - Diferenciar uso zero, ausência de registro e falta de histórico.
  - Features apenas com informação conhecida até a data de corte t. Proibidos como preditor: churn_flag, reason code, refund, feedback de saída, status final, end_date ou cancelamento conhecidos depois de t. `account_id` não é preditor.
  - Split temporal; preprocessing ajustado só no treino; limiar escolhido na validação, nunca no teste.
  - "Probabilidade" só com calibração validada; caso contrário, exibir score/ranking.
  - Correlação, importância de variável e motivo declarado não provam causa. Risco previsto não mede efeito de intervenção.
- **Premissas do candidato (DEC-015), obrigatórias:** P-01 churn = evento em `churn_events`; P-02 MRR da conta = soma das assinaturas ativas em t, com as 4 cópias exatas contadas como legítimas (DEC-018); P-03 uso e tickets pela data do próprio evento. Detalhes, elegibilidade, rótulos e campos proibidos em `docs/data-contract.md`.
- Ler sempre a base limpa (`clean_data.load_clean`), nunca reimplementar o parsing dos originais. Colunas `q_*` são flags de qualidade: não apagar as linhas marcadas sem decisão registrada. `q_is_duplicate` é só informativo: não exclui nada (DEC-018).
- Limitações conhecidas (detalhe em `docs/data-treatment-log.md`): datas de uso e tickets fora do ciclo da conta; `churn_flag` e `is_reactivation` contraditórios; assinaturas sobrepostas (MRR da conta ambíguo); `reason_code` incoerente com `feedback_text`; satisfação só com notas 3–5. Citar essas limitações em qualquer conclusão que dependa delas.
- **Teste final reservado (DEC-019):** cortes de 2024-09-30 a 2024-11-30 só podem ser usados na avaliação final da DAV-189. Nenhuma exploração, escolha de feature ou limiar olha esses cortes.
- **O "risco do gerador" (H10)** usa o fim dos dados e é proibido como feature. Achados em `docs/diagnosis-findings.md`.
- pandas 3.x: `str` é o dtype padrão para texto e copy-on-write está sempre ativo. Parsear datas explicitamente.

## Ambiente e comandos

Python 3.12 (`.python-version`). Dependências diretas em `requirements.in`; lock universal em `requirements.txt`.

Verificados na sessão S-002 (saídas em `process-log/sessions/S-002-claude-code-harness.md`):

| Comando (a partir desta pasta) | Efeito |
|---|---|
| `uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -r requirements.txt` | cria o ambiente local (caminho usado nesta máquina) |
| `python3.12 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt` | alternativa sem uv (resolução conferida com `pip install --dry-run`) |
| `.venv/bin/python solution/src/raw_data.py fetch` | baixa o pacote público do Kaggle, valida no temporário e grava em `raw/` sem sobrescrever |
| `.venv/bin/python solution/src/raw_data.py verify` | confere presença, tamanho e SHA-256 contra o manifest; exit 1 se divergir |
| `.venv/bin/python solution/src/clean_data.py` | gera `processed/clean/`, `outputs/data_quality/` e `docs/data-quality-report.md`; recusa rodar se os originais divergirem (S-003) |
| `.venv/bin/python solution/src/analytic_base.py` | gera snapshots, perfil retrospectivo, reconciliação (15 checagens), contagem de rótulos e `docs/analytic-base-dictionary.md`; exige a base limpa conferida por hash (S-004) |
| `.venv/bin/python solution/src/diagnose.py` | testa H01–H10 conforme o EXP-001 (bootstrap agrupado por conta) e gera `outputs/diagnosis/` e `docs/hypotheses-results.md`; ~15 s (S-006) |
| `.venv/bin/python -m pytest` | testes de `solution/tests/` |
| `sh scripts/stage.sh` | prepara o commit e falha se algo fora da pasta estiver preparado |
| `uv pip compile requirements.in --universal --python-version 3.12 --exclude-newer <AAAA-MM-DD> -o requirements.txt` | recompila o lock, apenas com versões publicadas até a data |

Planejados (ainda não existem; cada issue define nome e interface e move a linha para "verificados"):

| Issue | Comando previsto |
|---|---|
| DAV-189 | scripts de treino/avaliação e de geração de scores em `outputs/` |
| DAV-194 | `.venv/bin/streamlit run solution/app/<arquivo>.py` |

Não documentar como verificado um comando que não foi executado com saída observada.

## Git e GitHub (responsabilidade do Claude Code)

- `origin` = fork `git@github.com:DavidGrinber/ai-master-challenge.git`; `upstream` = repositório oficial, com push desabilitado. Branch: `submission/david-grinberg`. Conta autenticada no `gh`: DavidGrinber.
- O `.gitignore` raiz oficial ignora `submissions/`. Arquivos novos só entram com `git add -f`, então use sempre `sh scripts/stage.sh` e confira a lista impressa. Nunca rode `git add -f` em diretório inteiro.
- Um commit por entrega, citando a issue (`Refs DAV-xxx`). Identidade local: David Grinberg, com o e-mail noreply da conta GitHub. Sem force-push, sem reescrever histórico publicado e sem descartar alterações existentes.
- Depois do push: conferir `git rev-parse HEAD` = `git ls-remote origin submission/david-grinberg` e registrar URL, branch e SHA.
- Escopo do diff, obrigatório antes do PR: `git diff --name-only upstream/main...HEAD | grep -v '^submissions/david-grinberg/'` precisa sair vazio.
- PR somente na DAV-199 (planejado): `gh pr create --repo Gestao-Quatro-Ponto-Zero/ai-master-challenge --base main --head DavidGrinber:submission/david-grinberg --title "[Submission] David Grinberg — Challenge 001"`, com o corpo no template oficial. Se o PR já existir, atualizar a mesma branch.

## Fluxo das issues

| Etapa | Issue | Entrega |
|---|---|---|
| 1 | DAV-178 | harness, fork/branch, hipóteses revisadas, CSVs com manifest |
| 1b | DAV-201 | base derivada limpa (sem apagar linhas), relatório de qualidade e registro de tratamento; inconsistências como limitações |
| 2 | DAV-181 | prepara e cruza as cinco tabelas sem duplicar números; define churn, população elegível e datas que separam passado de futuro; base reproduzível em `processed/` e contrato em `docs/data-contract.md` |
| 3 | DAV-184 | investiga o churn e testa H01–H09 (e H10+ datadas): apoiada, refutada, inconclusiva ou não testável, com n, denominador, período, magnitude e incerteza |
| 4 | DAV-189 | define o alvo temporal e o horizonte; compara baseline simples com modelo interpretável usando só informação anterior à previsão; split temporal e auditoria de vazamento; salva o pipeline em `models/` e gera scores reproduzíveis (account_id, corte, versão, sinais); model card |
| 5 | DAV-193 | define as decisões e a experiência do CS: quem abordar, por quê, valor exposto, ação; contrato scores ↔ app (data, horizonte, versão) |
| 6 | DAV-194 | painel conectado ao modelo ou aos scores gerados por ele: carteira priorizada, filtros, ficha da conta, sinais, histórico disponível, ação sugerida e exportação |
| 7 | DAV-198 | consolida diagnóstico e recomendações (até 3 ações, com gatilho, responsável, indicador e impacto em cenários) no README |
| 8 | DAV-199 | valida a reprodução e as evidências, faz o push final e abre o PR |

O painel deve mostrar a data de referência e a versão do modelo. Probabilidades exigem validação apropriada. Correlação e importância de variável não comprovam causa.
Gate do projeto: se os dados não sustentarem previsão temporal honesta, documentar o limite e reavaliar o escopo preditivo. Nunca apresentar classificação retrospectiva como probabilidade futura.

## Como trabalhar (agente único)

1. Uma issue por vez: ler issue, aceite, dependências e as hipóteses pertinentes; mover a issue para In Progress.
2. O Claude Code implementa, executa as verificações apropriadas, corrige os problemas encontrados e entrega commit, atualização da issue e evidências.
3. O candidato acompanha os resultados e valida interpretações e decisões de negócio. Até a revisão de fato acontecer, registrar "pendente de revisão".
4. Uma issue fica Done quando os critérios de aceite e as verificações pertinentes estão cumpridos. Não há revisão obrigatória por outro agente; registrar verificações faz parte da issue, sem etapa separada de QA.
5. Comentário de fechamento no Linear com arquivos, verificações, SHA e pendências. Sem acesso ao Linear, gerar o texto para o candidato aplicar.
6. Não criar issues novas sem pedido do candidato; lacunas vão para o fechamento.

## Registro do processo

- Um arquivo por sessão ou etapa: `process-log/sessions/S-NNN-<tema>.md`, a partir de `TEMPLATE-sessao.md`. Prompt longo do usuário vai literal em `S-NNN-prompt-usuario.md`.
- Campos: objetivo, prompt relevante, ações e comandos, resultado observado, verificação, decisão do candidato ou revisão pendente, erros reais e correções, tempo (só se medido) e commit.
- Atualizar `process-log/evidence-index.csv` (E-NNN), `process-log/time-log.csv`, `docs/decision-log.md` (DEC-NNN) e `process-log/experiments/EXP-NNN.md` para testes de hipótese e modelos.
- Nunca inventar resultados, exports, screenshots, revisões, erros ou durações. Nunca registrar tokens, códigos de autenticação ou segredos. Justificativas curtas e verificáveis bastam; não expor raciocínio interno privado.
- S-001 (planejamento com ChatGPT) é preservado como está; não atribuí-lo ao Claude Code nem ao julgamento exclusivo do candidato.

## Critério de conclusão do projeto

Relatório responde às 3 perguntas; as cinco tabelas contribuem com evidências; métricas e recomendações são rastreáveis até script e versão dos dados; o score deriva de modelo validado e usa apenas informação disponível no instante de decisão; o painel permite priorizar e investigar contas; setup e inferência reproduzíveis a partir deste README; process-log real e completo; PR restrito a esta pasta.
