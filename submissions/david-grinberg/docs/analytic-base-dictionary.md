# Dicionário da base analítica

> Gerado por `solution/src/analytic_base.py`; não editar à mão. Premissas e regras em [data-contract.md](data-contract.md).

## snapshots.csv — 5254 linhas

Uma linha por conta elegível e data de corte. Features só com eventos até t; rótulos em (t, t+H]. Base para o modelo (DAV-189) e para comparações temporais (DAV-184). O corte no fim dos dados não tem rótulo: é a carteira a pontuar.

| Coluna | Tipo | Descrição |
|---|---|---|
| `account_id` | str | conta |
| `cutoff_date` | datetime | data de corte t (fim de mês); tudo abaixo usa só eventos com data <= t |
| `industry` | str | accounts.industry (atributo de cadastro) |
| `country` | str | accounts.country (atributo de cadastro) |
| `referral_source` | str | accounts.referral_source (atributo de cadastro) |
| `plan_tier_initial` | str | accounts.plan_tier, plano inicial segundo a fonte |
| `tenure_days` | int64 | dias entre signup_date e t |
| `n_active_subs` | int64 | assinaturas ativas em t (início <= t e fim vazio ou > t), sem duplicatas |
| `mrr_active` | int64 | P-02: soma do mrr_amount das assinaturas ativas em t |
| `seats_active` | int64 | soma de seats das assinaturas ativas em t |
| `n_active_trial_subs` | int64 | assinaturas ativas em t com is_trial |
| `n_active_basic` | int64 | assinaturas ativas em t no plano Basic |
| `n_active_pro` | int64 | assinaturas ativas em t no plano Pro |
| `n_active_enterprise` | int64 | assinaturas ativas em t no plano Enterprise |
| `share_active_annual` | float64 | fração das assinaturas ativas em t com cobrança anual |
| `n_active_no_autorenew` | int64 | assinaturas ativas em t sem auto_renew |
| `n_subs_started_90d` | int64 | assinaturas iniciadas em (t-90, t] |
| `n_subs_ended_90d` | int64 | assinaturas encerradas em (t-90, t] |
| `n_upgrade_closed_subs` | int64 | assinaturas já encerradas até t com upgrade_flag (a flag não tem data; só entra após o fim) |
| `n_downgrade_closed_subs` | int64 | assinaturas já encerradas até t com downgrade_flag (idem) |
| `usage_rows_30d` | int64 | linhas de uso em (t-30, t] (P-03) |
| `usage_count_30d` | int64 | soma de usage_count em (t-30, t] |
| `usage_count_prev_30d` | int64 | soma de usage_count em (t-60, t-30] |
| `usage_secs_30d` | int64 | soma de usage_duration_secs em (t-30, t] |
| `errors_30d` | int64 | soma de error_count em (t-30, t] |
| `distinct_features_30d` | int64 | features distintas usadas em (t-30, t] |
| `beta_rows_30d` | int64 | linhas de uso de feature beta em (t-30, t] |
| `usage_count_90d` | int64 | soma de usage_count em (t-90, t] |
| `errors_90d` | int64 | soma de error_count em (t-90, t] |
| `usage_rows_to_date` | int64 | linhas de uso com data <= t |
| `days_since_last_usage` | Int64 | dias desde o último uso <= t; nulo se nunca houve uso |
| `tickets_90d` | int64 | tickets abertos em (t-90, t] |
| `tickets_urgent_high_90d` | int64 | tickets urgent ou high abertos em (t-90, t] |
| `tickets_to_date` | int64 | tickets abertos até t |
| `open_tickets` | int64 | tickets abertos até t e ainda não fechados em t |
| `closed_tickets_90d` | int64 | tickets fechados em (t-90, t] |
| `mean_resolution_hours_90d` | float64 | média de resolution_time_hours dos fechados em (t-90, t]; nulo se nenhum |
| `mean_first_response_min_90d` | float64 | média de first_response_time_minutes dos fechados em (t-90, t]; nulo se nenhum |
| `escalations_90d` | int64 | fechados em (t-90, t] com escalation_flag (só conhecido no fechamento) |
| `satisfaction_responses_90d` | int64 | fechados em (t-90, t] com nota de satisfação |
| `mean_satisfaction_90d` | float64 | média das notas dos fechados em (t-90, t]; nulo se nenhuma (escala observada 3–5) |
| `prior_churn_events` | int64 | eventos de churn com data <= t |
| `days_since_last_churn` | Int64 | dias desde o último churn <= t; nulo se nenhum |
| `churn_next_30d` | boolean | RÓTULO: algum evento de churn em (t, t+30]; nulo se t+30 > fim dos dados |
| `churn_next_60d` | boolean | RÓTULO: algum evento de churn em (t, t+60]; nulo se t+60 > fim dos dados |
| `churn_next_90d` | boolean | RÓTULO: algum evento de churn em (t, t+90]; nulo se t+90 > fim dos dados |

## accounts_retrospective.csv — 500 linhas

Uma linha por conta com o período todo. **Retrospectiva**: mistura informação anterior e posterior ao churn; serve ao diagnóstico, nunca como feature de previsão.

| Coluna | Tipo | Descrição |
|---|---|---|
| `account_id` | str | conta |
| `account_name` | str | accounts.account_name |
| `industry` | str | accounts.industry |
| `country` | str | accounts.country |
| `signup_date` | datetime | accounts.signup_date |
| `referral_source` | str | accounts.referral_source |
| `plan_tier` | str | accounts.plan_tier (inicial segundo a fonte) |
| `seats` | int64 | accounts.seats (momento de referência desconhecido) |
| `is_trial` | bool | accounts.is_trial ('currently trialing' segundo a fonte) |
| `churn_flag` | bool | accounts.churn_flag original (contraditório; ver q_churn_flag_conflict) |
| `has_churn_event` | bool | P-01: a conta tem ao menos um evento em churn_events |
| `q_churn_flag_conflict` | bool | churn_flag diverge de has_churn_event |
| `n_churn_events` | int64 | eventos de churn no período todo |
| `first_churn_date` | datetime | primeiro evento de churn |
| `last_churn_date` | datetime | último evento de churn |
| `n_subscriptions` | int64 | assinaturas no período todo, sem duplicatas |
| `n_active_subs_end` | int64 | assinaturas ativas no fim dos dados |
| `mrr_active_end` | int64 | P-02: MRR ativo no fim dos dados |
| `usage_rows` | int64 | linhas de uso no período todo |
| `usage_count` | int64 | soma de usage_count |
| `usage_secs` | int64 | soma de usage_duration_secs |
| `errors` | int64 | soma de error_count |
| `distinct_features` | int64 | features distintas usadas |
| `beta_rows` | int64 | linhas de uso de feature beta |
| `tickets` | int64 | tickets no período todo |
| `escalations` | int64 | tickets com escalation_flag |
| `mean_resolution_hours` | float64 | média de resolution_time_hours; nulo se sem ticket |
| `satisfaction_responses` | int64 | tickets com nota de satisfação |
| `mean_satisfaction` | float64 | média das notas; nulo se nenhuma |
