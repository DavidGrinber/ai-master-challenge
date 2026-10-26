# Avaliação do modelo (EXP-002)

> Gerado por `solution/src/model.py`; não editar à mão. Pré-registro: [EXP-002](../process-log/experiments/EXP-002-modelo-pre-registro.md). Resumo: [model-card.md](model-card.md).

Alvo `churn_next_30d`. Treino 2023-01-31 a 2024-05-31; validação 2024-06-30 a 2024-08-31; teste 2024-09-30 a 2024-11-30 (avaliado uma vez). IC 95% por bootstrap agrupado por conta, pareado entre rankings.

## Seleção de C (treino → validação)

| C | AP validação | ROC-AUC validação |
|---:|---:|---:|
| 0.01 | 0.122 | 0.541 |
| 0.03 | 0.118 | 0.533 |
| 0.1 | 0.115 | 0.525 |
| 0.3 | 0.112 | 0.523 |
| 1.0 | 0.109 | 0.520 |

C escolhido: **0.01**. Challenger M2: não testado: M1 não superou B1 na validação (IC da diferença de AP inclui 0).

## Validação e teste

| Parte | Ranking | Linhas | Positivos | Prevalência | AP [IC 95%] | ROC-AUC [IC 95%] |
|---|---|---:|---:|---:|---|---|
| validação | M1 regressão logística | 1087 | 104 | 9.6% | 0.122 [0.090, 0.170] | 0.541 [0.478, 0.599] |
| validação | B0 aleatório | 1087 | 104 | 9.6% | 0.091 [0.072, 0.116] | 0.489 [0.432, 0.548] |
| validação | B1 tempo de casa curto | 1087 | 104 | 9.6% | 0.133 [0.104, 0.173] | 0.613 [0.554, 0.665] |
| validação | B2 MRR | 1087 | 104 | 9.6% | 0.097 [0.076, 0.127] | 0.466 [0.404, 0.521] |
| teste | M1 regressão logística | 1329 | 175 | 13.2% | 0.231 [0.190, 0.293] | 0.641 [0.593, 0.692] |
| teste | B0 aleatório | 1329 | 175 | 13.2% | 0.142 [0.120, 0.179] | 0.516 [0.473, 0.564] |
| teste | B1 tempo de casa curto | 1329 | 175 | 13.2% | 0.302 [0.244, 0.379] | 0.693 [0.650, 0.737] |
| teste | B2 MRR | 1329 | 175 | 13.2% | 0.111 [0.093, 0.140] | 0.414 [0.364, 0.463] |

## Diferenças pareadas

| Parte | A − B | Métrica | Diferença [IC 95%] |
|---|---|---|---|
| validação | M1 regressão logística − B1 tempo de casa curto | ap | -0.012 [-0.028, 0.012] |
| teste | M1 regressão logística − B1 tempo de casa curto | ap | -0.070 [-0.115, -0.029] |
| teste | M1 regressão logística − B1 tempo de casa curto | auc | -0.052 [-0.077, -0.028] |

**Decisão pela regra pré-registrada:** M1 regressão logística **não supera** B1 no teste (IC da diferença de AP inclui 0 ou fica abaixo). O painel usa ranking transparente; o modelo fica documentado como resultado negativo.

## Priorização no teste (top-K por corte)

| Ranking | Capacidade | Alertas/mês | Falsos alertas/mês | Precisão | Recall | MRR coberto | Antecedência mediana (dias) |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 regressão logística | 10.0% | 44.7 | 30.7 | 31.3% | 24.0% | 22.1% | 13 |
| M1 regressão logística | 20.0% | 88.7 | 65.0 | 26.7% | 40.6% | 32.6% | 13 |
| B0 aleatório | 10.0% | 44.7 | 37.3 | 16.4% | 12.6% | 11.2% | 12 |
| B0 aleatório | 20.0% | 88.7 | 75.7 | 14.7% | 22.3% | 21.3% | 12 |
| B1 tempo de casa curto | 10.0% | 44.7 | 27.7 | 38.1% | 29.1% | 15.9% | 13 |
| B1 tempo de casa curto | 20.0% | 88.7 | 62.3 | 29.7% | 45.1% | 33.9% | 13 |
| B2 MRR | 10.0% | 44.7 | 41.0 | 8.2% | 6.3% | 21.1% | 13 |
| B2 MRR | 20.0% | 88.7 | 80.3 | 9.4% | 14.3% | 38.1% | 7 |

## Calibração do modelo no teste

Brier 0.1142 (prevalência constante: 0.1143). Média prevista 8.1% × observada 13.2% (diferença relativa 38.3%); maior erro por decil 18.5%. **Exibir probabilidade: não — usar só o percentil do ranking.**

| Decil | Linhas | Prevista | Observada |
|---:|---:|---:|---:|
| 1 | 133 | 4.9% | 8.3% |
| 2 | 133 | 5.8% | 10.5% |
| 3 | 133 | 6.3% | 8.3% |
| 4 | 133 | 6.8% | 7.5% |
| 5 | 133 | 7.3% | 11.3% |
| 6 | 132 | 7.8% | 9.8% |
| 7 | 133 | 8.5% | 7.5% |
| 8 | 133 | 9.4% | 12.8% |
| 9 | 133 | 10.8% | 23.3% |
| 10 | 133 | 13.8% | 32.3% |

## Coeficientes do modelo final (10 maiores em módulo; features padronizadas)

| Feature | Coeficiente |
|---|---:|
| `num__tenure_days` | -0.327 |
| `num__usage_rows_to_date` | 0.177 |
| `num__n_subs_started_90d` | 0.124 |
| `num__tickets_to_date` | 0.110 |
| `num__escalations_90d` | -0.072 |
| `cat__industry_EdTech` | 0.072 |
| `cat__referral_source_organic` | 0.068 |
| `cat__country_UK` | 0.065 |
| `cat__country_AU` | -0.056 |
| `cat__referral_source_ads` | -0.052 |
