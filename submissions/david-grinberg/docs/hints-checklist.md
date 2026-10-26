# Dicas do challenge: checagem complementar (exploratória)

> Gerado por `solution/src/explore_hints.py`; não editar à mão. Análise pós-hoc feita depois da pergunta do candidato "você analisou tudo que está nas dicas?" (2026-10-26). Exploratória, com correção de Bonferroni. Interpretação em [diagnosis-findings.md](diagnosis-findings.md).

## Dica: "Olhe os tickets de suporte dos clientes que churnearam vs. os que ficaram" — e todo o perfil da conta

Comparação retrospectiva no nível da conta (500 contas, período todo), com as duas definições de churn. 27 variáveis por definição; limite de Bonferroni p < 0.0019.

| Definição | Variáveis significativas | Menor p (variável) | p < 0,05 sem correção |
|---|---:|---|---:|
| churn_flag | 0 | 0.059 (tenure_at_end) | 0 de 27 |
| has_churn_event | 0 | 0.084 (urgent_share) | 0 de 27 |

| Definição | Variável | AUC | p | média churn | média retidos |
|---|---|---:|---:|---:|---:|
| churn_flag | tenure_at_end | 0.559 | 0.059 | 371.673 | 329.433 |
| churn_flag | industry | — | 0.066 | — | — |
| churn_flag | referral_source | — | 0.079 | — | — |
| churn_flag | first_response_min | 0.449 | 0.103 | 84.927 | 89.582 |
| churn_flag | error_rate | 0.451 | 0.115 | 0.054 | 0.057 |
| churn_flag | sub_mrr_mean | 0.456 | 0.154 | 2082.922 | 2315.300 |
| churn_flag | urgent_share | 0.457 | 0.165 | 0.236 | 0.267 |
| churn_flag | usage_count | 0.539 | 0.206 | 522.036 | 495.131 |
| churn_flag | distinct_features | 0.538 | 0.217 | 28.336 | 27.413 |
| churn_flag | usage_rows | 0.538 | 0.221 | 52.045 | 49.423 |
| churn_flag | n_subs | 0.533 | 0.292 | 10.291 | 9.918 |
| churn_flag | share_trial_subs | 0.531 | 0.326 | 0.164 | 0.156 |
| churn_flag | tickets | 0.471 | 0.342 | 3.927 | 4.021 |
| churn_flag | is_trial | — | 0.388 | — | — |
| churn_flag | escalation_rate | 0.518 | 0.391 | 0.062 | 0.044 |
| churn_flag | satisfaction | 0.520 | 0.540 | 4.003 | 3.953 |
| churn_flag | country | — | 0.659 | — | — |
| churn_flag | seats | 0.488 | 0.692 | 19.236 | 20.933 |
| churn_flag | resolution_hours | 0.489 | 0.717 | 35.485 | 36.450 |
| churn_flag | share_downgrade | 0.491 | 0.727 | 0.041 | 0.044 |
| churn_flag | secs_per_use_row | 0.492 | 0.787 | 3054.276 | 3056.905 |
| churn_flag | response_rate | 0.506 | 0.837 | 0.605 | 0.598 |
| churn_flag | share_autorenew | 0.506 | 0.855 | 0.803 | 0.800 |
| churn_flag | beta_share | 0.495 | 0.867 | 0.102 | 0.102 |
| churn_flag | share_annual | 0.495 | 0.883 | 0.488 | 0.492 |
| churn_flag | share_upgrade | 0.496 | 0.892 | 0.103 | 0.106 |
| churn_flag | plan_tier | — | 0.999 | — | — |
| has_churn_event | urgent_share | 0.452 | 0.084 | 0.242 | 0.304 |
| has_churn_event | referral_source | — | 0.143 | — | — |
| has_churn_event | share_upgrade | 0.540 | 0.148 | 0.109 | 0.095 |
| has_churn_event | distinct_features | 0.537 | 0.196 | 27.761 | 27.270 |
| has_churn_event | escalation_rate | 0.523 | 0.241 | 0.049 | 0.045 |
| has_churn_event | beta_share | 0.469 | 0.270 | 0.101 | 0.104 |
| has_churn_event | share_downgrade | 0.522 | 0.369 | 0.046 | 0.039 |
| has_churn_event | secs_per_use_row | 0.522 | 0.432 | 3060.536 | 3046.314 |
| has_churn_event | seats | 0.522 | 0.444 | 20.668 | 20.304 |
| has_churn_event | share_trial_subs | 0.479 | 0.463 | 0.155 | 0.165 |
| has_churn_event | sub_mrr_mean | 0.519 | 0.494 | 2285.204 | 2214.167 |
| has_churn_event | response_rate | 0.482 | 0.535 | 0.597 | 0.606 |
| has_churn_event | tickets | 0.486 | 0.625 | 3.963 | 4.088 |
| has_churn_event | country | — | 0.640 | — | — |
| has_churn_event | usage_rows | 0.513 | 0.657 | 50.256 | 49.392 |
| has_churn_event | usage_count | 0.511 | 0.687 | 503.435 | 495.378 |
| has_churn_event | n_subs | 0.511 | 0.703 | 10.023 | 9.946 |
| has_churn_event | plan_tier | — | 0.713 | — | — |
| has_churn_event | first_response_min | 0.508 | 0.783 | 88.777 | 88.041 |
| has_churn_event | industry | — | 0.785 | — | — |
| has_churn_event | satisfaction | 0.506 | 0.828 | 3.962 | 3.970 |
| has_churn_event | is_trial | — | 0.845 | — | — |
| has_churn_event | share_autorenew | 0.505 | 0.850 | 0.802 | 0.798 |
| has_churn_event | error_rate | 0.505 | 0.873 | 0.056 | 0.057 |
| has_churn_event | resolution_hours | 0.496 | 0.876 | 36.235 | 36.247 |
| has_churn_event | tenure_at_end | 0.502 | 0.934 | 338.741 | 338.689 |
| has_churn_event | share_annual | 0.501 | 0.977 | 0.491 | 0.493 |

## Dica: "Cruze feature usage com churn events — há padrões?" — por feature

40 features: participação de cada feature no uso da conta e adoção (sim/não). Limite de Bonferroni p < 0.00125.

| Definição | Medida | Menor p (feature) | p < 0,05 | esperado ao acaso |
|---|---|---|---:|---:|
| churn_flag | participação no uso | 0.046 (feature_23) | 1 de 40 | 2 |
| churn_flag | adoção sim/não | 0.015 (feature_37) | 2 de 40 | 2 |
| has_churn_event | participação no uso | 0.034 (feature_29) | 1 de 40 | 2 |
| has_churn_event | adoção sim/não | 0.031 (feature_22) | 1 de 40 | 2 |

## Assinaturas: encerramento × atributos (5.000 assinaturas)

| Atributo | p | Taxa de encerramento por nível |
|---|---:|---|
| plan_tier | 0.888 | {"Basic": 0.095, "Enterprise": 0.1, "Pro": 0.097} |
| billing_frequency | 0.486 | {"annual": 0.1, "monthly": 0.094} |
| auto_renew_flag | 0.980 | {"False": 0.096, "True": 0.097} |
| upgrade_flag | 0.445 | {"False": 0.098, "True": 0.087} |
| downgrade_flag | 0.439 | {"False": 0.096, "True": 0.115} |
| is_trial | 0.805 | {"False": 0.097, "True": 0.1} |
| seats | 0.557 | AUC 0.492 |
| mrr_amount | 0.898 | AUC 0.498 |

## Dica: "Nem todo churn tem o mesmo peso" — MRR perdido e motivos

| Motivo | Eventos | MRR perdido | % do MRR perdido | MRR mediano | Refund médio | % com refund | % upgrade prévio | % downgrade prévio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| budget | 104 | 1061858 | 17.7% | 6749 | 12.00 | 23.1% | 23.1% | 5.8% |
| competitor | 92 | 961908 | 16.0% | 7382 | 13.08 | 19.6% | 18.5% | 13.0% |
| features | 114 | 1313345 | 21.9% | 7672 | 16.72 | 21.1% | 14.9% | 7.9% |
| pricing | 91 | 781405 | 13.0% | 4977 | 14.65 | 24.2% | 19.8% | 4.4% |
| support | 104 | 1027996 | 17.1% | 7506 | 11.73 | 26.9% | 26.9% | 12.5% |
| unknown | 95 | 848507 | 14.2% | 5738 | 18.34 | 27.4% | 20.0% | 9.5% |

Refund por motivo p = 0.786; MRR no churn por motivo p = 0.318; upgrade prévio × motivo p = 0.356; downgrade prévio × motivo p = 0.194. Eventos com `preceding_upgrade_flag` em contas que têm alguma assinatura com upgrade: 64.2% (base de todas as contas: 61.4%).

## Dica: "O uso cresceu — isso é verdade pra todos os segmentos?"

Uso médio em 30 dias por conta elegível, por semestre (2023S1 omitido: poucas contas).

| Segmento | Nível | 2023S2 | 2024S1 | 2024S2 | Variação |
|---|---|---:|---:|---:|---:|
| plan_tier_initial | Basic | 21.3 | 21.4 | 22.4 | 5.4% |
| plan_tier_initial | Enterprise | 22.7 | 20.0 | 20.9 | -8.3% |
| plan_tier_initial | Pro | 21.0 | 21.4 | 20.2 | -4.1% |
| industry | Cybersecurity | 22.4 | 20.0 | 22.1 | -1.7% |
| industry | DevTools | 23.9 | 22.5 | 20.5 | -14.3% |
| industry | EdTech | 17.4 | 21.0 | 20.8 | 19.2% |
| industry | FinTech | 20.4 | 20.7 | 21.2 | 3.8% |
| industry | HealthTech | 21.7 | 20.4 | 21.0 | -3.0% |
| referral_source | ads | 20.2 | 20.6 | 20.5 | 1.4% |
| referral_source | event | 24.1 | 21.9 | 20.9 | -13.3% |
| referral_source | organic | 20.5 | 20.6 | 22.7 | 10.6% |
| referral_source | other | 21.3 | 20.5 | 20.1 | -5.7% |
| referral_source | partner | 22.3 | 21.4 | 21.4 | -3.8% |
