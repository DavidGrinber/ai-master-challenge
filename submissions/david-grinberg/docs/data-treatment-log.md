# Registro de tratamento dos dados (DAV-201)

Decisões aplicadas por `solution/src/clean_data.py` na base derivada `solution/data/processed/clean/`. Os números citados vêm de `docs/data-quality-report.md`, que é gerado pelo script; os IDs entre parênteses (A-, S-, U-, T-, C-) são checagens desse relatório.
Proposta e implementação: Claude Code (S-003), a pedido do candidato. Revisão das decisões pelo candidato: **pendente**.

## Regra geral

**TR-01. Originais intocados; nada é apagado nem corrigido em silêncio.** Os CSVs em `raw/` são só lidos, e o SHA-256 é conferido antes e depois do build. A base derivada tem as mesmas linhas e os mesmos valores originais. Os problemas viram colunas `q_*` por linha e, quando não têm solução, entram como limitação.
*Por quê:* a auditoria mostrou inconsistências que não têm uma correção correta conhecida, como as datas de uso. Corrigir por suposição criaria dados que não existem.

**TR-02. Normalização de tipos.** Datas em ISO (`AAAA-MM-DD`; `closed_at` com hora); booleanos como `True`/`False`; `satisfaction_score` como inteiro anulável (`Int64`). Categorias mantidas como estão, porque não há variações de caixa ou de espaços em nenhuma coluna. Fim da observação = **2024-12-31**, a última data presente em qualquer tabela. O schema de cada coluna fica em `solution/outputs/data_quality/derived_manifest.json`, e `load_clean()` relê com os tipos certos.

## Tratamentos

| ID | Problema (checagem) | Tratamento | Alternativa descartada |
|---|---|---|---|
| TR-03 | `country = UK` não segue o ISO-2 documentado, que seria GB (A-03) | mantido como na fonte | trocar por GB: sem ganho analítico e torna o painel menos legível |
| TR-04 | 4 assinaturas são cópias exatas de outra, exceto o id (S-03) | mantidas; `q_duplicate_of` aponta a original (o menor id); **excluir de somas de receita**. As 22 linhas de uso ligadas a elas continuam atribuídas à conta (U-08) | apagar as cópias, o que perderia as 22 linhas de uso |
| TR-05 | `usage_id` repetido em 42 linhas (21 ids), sempre em assinaturas diferentes e com conteúdo diferente (U-01, U-03) | chave substituta `usage_row_id` (`UR-00001`…), pela ordem do arquivo; `usage_id` preservado | deduplicar por `usage_id`, o que apagaria eventos distintos |
| TR-06 | 6 linhas com mesma assinatura, dia e feature, mas valores diferentes (U-04) | mantidas como eventos distintos; flag | somar ou apagar, sem base para saber qual é o correto |
| TR-07 | 4.992 de 5.000 assinaturas se sobrepõem a outra da mesma conta; média de 9 ativas por conta no fim de 2024 (S-09) | flag `q_overlaps_other_subscription`. **O MRR da conta não é definido aqui**: é decisão do candidato na DAV-181 | tratar assinaturas como sequência de períodos, o que os dados contradizem |
| TR-08 | 23 assinaturas com upgrade e downgrade ao mesmo tempo, sem data da mudança (S-08) | mantido; flag. Não dá para ordenar as mudanças nem saber se ocorreram antes de uma data de corte | — |
| TR-09 | Uso e tickets datados fora do ciclo da conta: 13.198 usos e 1.077 tickets antes do signup; 19.142 usos antes do início da assinatura e 290 depois do fim (U-05, U-06, U-07, T-03) | mantido; flags por linha. O uso é atribuído à conta pela assinatura, independentemente da data | apagar as linhas, o que eliminaria a maior parte do uso; deslocar datas inventaria dados |
| TR-10 | Churn não reconcilia entre fontes: `accounts.churn_flag` contradiz `churn_events` em 312 contas (A-04); `is_reactivation` incoerente com a ordem dos eventos em 26 + 213 eventos (C-05, C-06); 469 de 600 eventos sem fim de assinatura a até 31 dias (C-10); as 352 contas com evento seguem com assinatura ativa (C-11) | campos originais preservados. Colunas novas: `has_churn_event`, `event_seq` (ordem do evento na conta), `n_events_account`, `q_days_to_nearest_subscription_end`. **A definição de churn fica para a DAV-181** | escolher agora uma fonte "verdadeira" e sobrescrever as outras |
| TR-11 | Nulos e ausências: `satisfaction_score` nulo = sem resposta (T-06); `feedback_text` nulo = sem comentário (C-08); `end_date` nulo = ativa em 2024-12-31; 33 assinaturas sem nenhum uso (U-10); 8 contas sem ticket (T-08) | nulos mantidos; `has_satisfaction`, `active_at_data_end`. Ausência de linha de uso **não** equivale a uso zero | imputar zero ou média |
| TR-12 | `feedback_text` incompatível com `reason_code` em 278 de 379 casos comparáveis (C-09) | ambos preservados; `q_feedback_matches_reason` com o mapa: "too expensive" → pricing/budget; "missing features" → features; "switched to competitor" → competitor. Nulo quando não há feedback ou o motivo é `unknown` | confiar no `reason_code` como causa |
| TR-13 | `submitted_at` só tem a data; `closed_at` tem hora (T-05) | mantido; a duração usa `resolution_time_hours`, que confere com a diferença das datas (T-04 = 0) | — |
| TR-14 | Satisfação: só notas 3, 4 e 5 entre 1.175 respostas; a escala documentada é 1–5 (T-07) | mantido | — |

## Limitações para as próximas etapas

1. **As datas de uso e de tickets não seguem o ciclo da conta** (TR-09). Premissa P-03 (DEC-015): esses eventos entram pela própria data, com ressalva. Features temporais como "queda de uso nos últimos 30 dias" ou "tickets recentes" podem não refletir a realidade da conta. A H01 (queda de uso antecede churn) segue testável, mas o resultado precisa citar esta limitação (DAV-184). Um modelo temporal pode não superar o baseline (DAV-189).
2. **Não existe "churn" único** (TR-10). A DAV-181 precisa escolher a fonte e a unidade antes de qualquer taxa; `churn_flag` e `is_reactivation` são contraditórios e não servem como alvo. → Encaminhado pela premissa P-01 (churn = evento em `churn_events`), decisão do candidato na DAV-181 (DEC-015).
3. **O MRR da conta é ambíguo** com assinaturas sobrepostas (TR-07), então o valor exposto no painel depende da definição da DAV-181. Excluir sempre `q_is_duplicate` das somas. → Encaminhado pela premissa P-02 (soma das ativas sem duplicatas), DEC-015.
4. **O motivo declarado não é confiável** como explicação (TR-12): `reason_code` e `feedback_text` concordam em só 101 de 379 casos.
5. **A escala de satisfação vai de 3 a 5** (TR-14): o dado não mostra insatisfação abaixo de 3, o que importa para a frase "o CS diz que a satisfação está ok".
6. **Dados simulados** (manifest): as inconsistências acima provavelmente vêm do gerador do dataset, não de falhas operacionais da RavenStack. O relatório final deve dizer isso.

## Como reproduzir

```bash
.venv/bin/python solution/src/raw_data.py verify   # originais conferem
.venv/bin/python solution/src/clean_data.py        # gera clean/, checks.csv, manifest e relatório
.venv/bin/python -m pytest                         # flags em casos conhecidos, invariantes e números da auditoria
```

O `derived_manifest.json` guarda o SHA-256 de cada CSV derivado. Um rebuild com as mesmas versões gera os mesmos bytes, conferido duas vezes na S-003.
