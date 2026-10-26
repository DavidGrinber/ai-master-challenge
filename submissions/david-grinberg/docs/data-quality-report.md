# Relatório de qualidade dos dados

> Gerado por `solution/src/clean_data.py`; não editar à mão. Decisões de tratamento em [data-treatment-log.md](data-treatment-log.md).

Fim da observação (última data nas tabelas): **2024-12-31**. Nenhuma linha removida; valores originais preservados; problemas viram colunas `q_*`.

| Tabela | Linhas originais | Linhas derivadas | Colunas na base derivada |
|---|---:|---:|---:|
| accounts | 500 | 500 | 12 |
| subscriptions | 5000 | 5000 | 19 |
| feature_usage | 25000 | 25000 | 16 |
| support_tickets | 2000 | 2000 | 11 |
| churn_events | 600 | 600 | 16 |

## Checagens

| ID | Tabela | Checagem | n | de | Tratamento | Status |
|---|---|---|---:|---:|---|---|
| A-01 | accounts | account_id duplicado | 0 | 500 | nenhum | ok |
| A-02 | accounts | valores nulos | 0 | 5000 | nenhum | ok |
| A-03 | accounts | country = UK, fora do padrão ISO-2 documentado (seria GB) | 58 | 500 | mantido como na fonte (TR-03) | mantido |
| A-04 | accounts | churn_flag contradiz a existência de churn_events | 312 | 500 | churn_flag preservado; flag q_churn_flag_conflict (TR-10) | limitação |
| S-01 | subscriptions | subscription_id duplicado | 0 | 5000 | nenhum | ok |
| S-02 | subscriptions | account_id sem conta (órfão) | 0 | 5000 | nenhum | ok |
| S-03 | subscriptions | cópia exata de outra assinatura (todos os campos exceto o id) | 4 | 5000 | mantida e tratada como legítima por decisão do candidato; q_duplicate_of só informa a cópia (TR-04) | mantido |
| S-04 | subscriptions | churn_flag diverge de ter end_date | 0 | 5000 | nenhum | ok |
| S-05 | subscriptions | start_date antes do signup da conta | 0 | 5000 | nenhum | ok |
| S-06 | subscriptions | end_date antes de start_date | 0 | 5000 | nenhum | ok |
| S-07 | subscriptions | MRR zero fora de trial ou ARR != 12 x MRR | 0 | 5000 | nenhum | ok |
| S-08 | subscriptions | upgrade_flag e downgrade_flag ao mesmo tempo, sem data da mudança | 23 | 5000 | mantido; flag q_upgrade_and_downgrade (TR-08) | limitação |
| S-09 | subscriptions | período sobreposto a outra assinatura da mesma conta | 4992 | 5000 | mantido; flag q_overlaps_other_subscription; MRR da conta a definir na DAV-181 (TR-07) | limitação |
| U-01 | feature_usage | usage_id repetido em linhas diferentes | 42 | 25000 | chave substituta usage_row_id pela ordem do arquivo (TR-05) | tratado |
| U-02 | feature_usage | subscription_id sem assinatura (órfão) | 0 | 25000 | nenhum | ok |
| U-03 | feature_usage | linha idêntica a outra (exceto ids) | 0 | 25000 | nenhum | ok |
| U-04 | feature_usage | mais de uma linha para a mesma assinatura, dia e feature | 6 | 25000 | mantidas como eventos distintos; flag q_same_subscription_day_feature (TR-06) | mantido |
| U-05 | feature_usage | uso datado antes do signup da conta | 13198 | 25000 | mantido; flag q_before_account_signup (TR-09) | limitação |
| U-06 | feature_usage | uso datado antes do início da assinatura | 19142 | 25000 | mantido; flag q_before_subscription_start (TR-09) | limitação |
| U-07 | feature_usage | uso datado depois do fim da assinatura | 290 | 25000 | mantido; flag q_after_subscription_end (TR-09) | limitação |
| U-08 | feature_usage | uso ligado a uma assinatura duplicada | 22 | 25000 | mantido; a assinatura conta como legítima (TR-04) | mantido |
| U-09 | feature_usage | usage_count = 0 | 2 | 25000 | mantido | mantido |
| U-10 | subscriptions | assinatura sem nenhuma linha de uso | 33 | 5000 | mantida; ausência de linha não é uso zero (TR-11) | mantido |
| T-01 | support_tickets | ticket_id duplicado | 0 | 2000 | nenhum | ok |
| T-02 | support_tickets | account_id sem conta (órfão) | 0 | 2000 | nenhum | ok |
| T-03 | support_tickets | ticket aberto antes do signup da conta | 1077 | 2000 | mantido; flag q_before_account_signup (TR-09) | limitação |
| T-04 | support_tickets | closed_at antes de submitted_at ou divergente de resolution_time_hours (>1h) | 0 | 2000 | nenhum | ok |
| T-05 | support_tickets | submitted_at só com a data (closed_at tem hora) | 2000 | 2000 | mantido; o tempo de resolução vem de resolution_time_hours (TR-13) | limitação |
| T-06 | support_tickets | satisfaction_score nulo (sem resposta) | 825 | 2000 | mantido nulo; coluna has_satisfaction (TR-11) | mantido |
| T-07 | support_tickets | respostas de satisfação; notas 1 e 2 nunca aparecem (escala documentada 1–5) | 1175 | 2000 | mantido; notas observadas [3, 4, 5], 0 notas 1–2 (TR-14) | limitação |
| T-08 | accounts | conta sem nenhum ticket | 8 | 500 | mantida | mantido |
| C-01 | churn_events | churn_event_id duplicado | 0 | 600 | nenhum | ok |
| C-02 | churn_events | account_id sem conta (órfão) | 0 | 600 | nenhum | ok |
| C-03 | churn_events | churn_date antes do signup da conta | 0 | 600 | nenhum | ok |
| C-04 | churn_events | dois eventos da mesma conta na mesma data | 2 | 600 | mantidos; flag q_same_day_event | mantido |
| C-05 | churn_events | is_reactivation = True no primeiro evento da conta | 26 | 600 | is_reactivation preservado; flag; usar event_seq (TR-10) | limitação |
| C-06 | churn_events | is_reactivation = False em evento posterior a outro churn | 213 | 600 | is_reactivation preservado; flag; usar event_seq (TR-10) | limitação |
| C-07 | churn_events | reason_code = unknown | 95 | 600 | mantido como categoria própria | mantido |
| C-08 | churn_events | feedback_text nulo | 148 | 600 | mantido nulo (sem comentário) | mantido |
| C-09 | churn_events | feedback_text incompatível com reason_code | 278 | 379 | ambos preservados; flag q_feedback_matches_reason (TR-12) | limitação |
| C-10 | churn_events | sem fim de assinatura da conta a até 31 dias do evento | 469 | 600 | mantido; coluna q_days_to_nearest_subscription_end (TR-10) | limitação |
| C-11 | churn_events | conta com evento que segue com assinatura ativa em 2024-12-31 | 352 | 352 | mantido; churn de conta não equivale a encerrar todas as assinaturas (TR-10) | limitação |

## Limitações sem solução

- **A-04**: churn_flag contradiz a existência de churn_events (312 de 500).
- **S-08**: upgrade_flag e downgrade_flag ao mesmo tempo, sem data da mudança (23 de 5000).
- **S-09**: período sobreposto a outra assinatura da mesma conta (4992 de 5000).
- **U-05**: uso datado antes do signup da conta (13198 de 25000).
- **U-06**: uso datado antes do início da assinatura (19142 de 25000).
- **U-07**: uso datado depois do fim da assinatura (290 de 25000).
- **T-03**: ticket aberto antes do signup da conta (1077 de 2000).
- **T-05**: submitted_at só com a data (closed_at tem hora) (2000 de 2000).
- **T-07**: respostas de satisfação; notas 1 e 2 nunca aparecem (escala documentada 1–5) (1175 de 2000).
- **C-05**: is_reactivation = True no primeiro evento da conta (26 de 600).
- **C-06**: is_reactivation = False em evento posterior a outro churn (213 de 600).
- **C-09**: feedback_text incompatível com reason_code (278 de 379).
- **C-10**: sem fim de assinatura da conta a até 31 dias do evento (469 de 600).
- **C-11**: conta com evento que segue com assinatura ativa em 2024-12-31 (352 de 352).
