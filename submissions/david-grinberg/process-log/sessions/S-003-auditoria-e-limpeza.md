# S-003 — Auditoria inicial (DAV-181) e limpeza da base (DAV-201)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issues: [DAV-181](https://linear.app/david-grinberg/issue/DAV-181/02-cruzar-tabelas-e-preparar-base-de-analise) (iniciada e pausada) · [DAV-201](https://linear.app/david-grinberg/issue/DAV-201/01b-normalizar-e-limpar-a-base-camada-derivada-relatorio-de-qualidade) (criada nesta sessão).
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompts do candidato (literais)
1. Depois do fechamento da DAV-178:
   > siga
   >
   > pendencias
   > 1.organizei tudo chat gpt, mas isso acho que podemos fazer depois ao organizar a entrega
   > 2. depois coloco
2. Depois da auditoria; o candidato recusou as perguntas de decisão sobre churn, escopo, elegibilidade e MRR, e pediu esclarecimento:
   > estou identificando que a base de dados precisa ser normalizada/limpada antes de seguirmos: Preserve os CSVs originais. Produza uma base derivada com transformações reproduzíveis, um relatório curto de qualidade e um registro das decisões de tratamento. Mantenha inconsistências sem solução como limitações explícitas. Cria task no linear pra isso e seguimos assim

## Objetivo
Iniciar a DAV-181 auditando a estrutura das cinco tabelas. Depois, a pedido do candidato, criar e executar a DAV-201: base limpa, relatório de qualidade e registro de tratamento, sem apagar nem corrigir dados em silêncio.

## Ações, comandos e saídas observadas

### Auditoria exploratória (DAV-181, comandos inline no venv)
- Leitura do README da fonte, pela primeira vez neste fluxo: contagens esperadas; exige crédito "River @ Rivalytics"; a fonte afirma "signup ≤ subscription ≤ churn" e "no orphans".
- Formato: 500 / 5.000 / 25.000 / 2.000 / 600 linhas, iguais à fonte. Nulos: `end_date` 4.514, `satisfaction_score` 825, `feedback_text` 148.
- Chaves: nenhum órfão; `usage_id` com 24.979 valores distintos em 25.000 linhas; 4 assinaturas iguais a outras exceto pelo id.
- Coerência temporal: 52,8% do uso e 1.077 de 2.000 tickets antes do signup; 19.142 usos antes do início da assinatura; 0 violações de signup ≤ início da assinatura e de churn ≥ signup. As 500 contas, inclusive as 352 com evento de churn, têm assinatura ativa em 2024-12-31.
- Reconciliação: `accounts.churn_flag` × existência de evento → 75 True/True, 113 False/False, 277 False com evento, 35 True sem evento. `is_reactivation` incoerente com a ordem dos eventos.
- Distribuição por trimestre: uso (~3.100/trimestre) e tickets (~250/trimestre) constantes; eventos de churn de 6 (1º tri/2023) a 251 (4º tri/2024).
- Viabilidade: tabela de contas elegíveis e positivos por corte mensal para H = 30/60/90 dias (com H=30, de 1 positivo em 21 elegíveis em mar/2023 a 75 em 475 em nov/2024).
- Nenhuma comparação entre segmentos nem teste de hipótese.

### Perguntas de decisão (recusadas para esclarecimento)
Fonte do churn, escopo preditivo, elegibilidade e MRR da conta. O candidato preferiu limpar a base antes (prompt 2). As quatro decisões continuam abertas na DAV-181.

### DAV-201
- Issue criada no Linear (In Progress, bloqueia a DAV-181, relacionada à DAV-178).
- Perfil de categorias e faixas: categorias sem variação de caixa ou espaços; `country` usa UK; satisfação só com 3/4/5; `reason_code` × `feedback_text` com distribuição quase uniforme; 23 assinaturas com upgrade e downgrade; 1 par de eventos na mesma conta e data.
- Criados `solution/src/clean_data.py` e `solution/tests/test_clean_data.py`. Saídas: `processed/clean/*.csv` (fora do Git), `outputs/data_quality/checks.csv`, `outputs/data_quality/derived_manifest.json`, `docs/data-quality-report.md` (gerado). Escritos à mão: `docs/data-treatment-log.md` (TR-01 a TR-14).
- `python solution/src/clean_data.py` → 5 tabelas com o mesmo número de linhas; hashes `13be6f19267e`, `c06f1162220a`, `54526a120d1a`, `50e8f6d28fdf`, `318be49c4423`; "originais intactos". Segunda execução: hashes idênticos.
- Verificação manual da conta A-6e08f3: flags de uso antes do signup (3) e antes do início da assinatura (34) iguais ao recálculo à mão; evento único de 10/02/2024 com `is_reactivation = True` e `churn_flag = False`; 10 assinaturas ativas, 6 iniciadas depois do evento.

## Verificações
- `pytest` → 13 passed: flags em dados sintéticos com resposta conhecida; nenhuma linha perdida e valores originais iguais; originais intocados e build determinístico; round-trip de `load_clean`; status "ok" só quando n = 0; números da auditoria reproduzidos sobre os dados reais (A-04 312, S-03 4, U-01 42, U-05 13.198, U-06 19.142, T-03 1.077, C-05 26, C-06 213, C-11 352).
- `raw_data.py verify` antes e depois → 6/6 ok.

## Erros reais e correções
1. Teste: a 1ª versão de `test_no_row_lost_and_original_values_kept` comparava tipos e falhou em `satisfaction_score` (float64 → Int64, uma normalização intencional). Passou a comparar só os valores (`check_dtype=False`), com comentário.
2. IDs: as decisões de tratamento usavam "T-NN", que colidia com as checagens de tickets (T-01 a T-08). Renomeadas para TR-NN no script e no registro.
3. Rótulo "Colunas derivadas" do relatório trocado por "Colunas na base derivada" (era o total de colunas).
4. Decision log: DEC-012 a 014 inseridas antes da DEC-011 por engano; ordem corrigida.
5. A exploração contou 4.492 assinaturas "iniciadas antes do fim de uma anterior"; a checagem S-09 conta 4.992 "sobrepostas a qualquer outra". As definições são diferentes e as duas estão corretas; o relatório usa a S-09.

## Decisões
- Do candidato: detalhar a exploração anterior na DAV-199 e incluir o LinkedIn depois (DEC-012); limpar a base numa etapa própria antes da DAV-181 (DEC-013).
- Do Claude Code, revisão pendente: TR-01 a TR-14 (DEC-014).
- Em aberto na DAV-181: fonte do churn, escopo preditivo, elegibilidade e MRR da conta.

## Tempo
Não cronometrado. Timestamps observados (-03:00): DAV-181 iniciada 17:07:46; DAV-201 criada ~17:26 (Linear: 20:26 UTC); registro escrito 17:32.

## Commit
SHA no comentário de fechamento da DAV-201.
