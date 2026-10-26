# Resultados das hipóteses (EXP-001)

> Gerado por `solution/src/diagnose.py`; não editar à mão. Pré-registro: [EXP-001](../process-log/experiments/EXP-001-hipoteses-pre-registro.md). Interpretação: [diagnosis-findings.md](diagnosis-findings.md).

Taxa = eventos de churn em (t, t+30] por conta-mês elegível. IC 95% por bootstrap de Poisson agrupado por conta. Desenvolvimento: cortes 2023-01-31 a 2024-05-31; validação: 2024-06-30 a 2024-08-31. O teste final (2024-09-30 a 2024-11-30) não foi usado nas comparações.

## Status pela regra pré-registrada

| H | Status (regra) | Evidência principal |
|---|---|---|
| H01 | inconclusiva | desenvolvimento: AUC 0.48 [0.43, 0.53]; validação: AUC 0.48 [0.41, 0.55] |
| H02 | ticket: inconclusiva; satisfação: inconclusiva | ticket em 90d — desenvolvimento: RR 0.97 [0.72, 1.32]; validação: RR 1.22 [0.83, 1.79] | satisfação — desenvolvimento: AUC 0.48 [0.40, 0.59]; validação: AUC 0.47 [0.37, 0.58] |
| H03 | inconclusiva | desenvolvimento: AUC 0.51 [0.45, 0.56]; validação: AUC 0.49 [0.42, 0.56] |
| H04 | apoiada | 1 de 25 níveis de segmento com IC excluindo RR = 1 nas duas partes: tenure_band=<180d (apoiada) |
| H05 | avaliar (descritivo) | uso total 31400 (2023Q1) → 32227 (2024Q4); uso 30d por conta elegível 24.2 → 21.4 |
| H06 | inconclusiva | maioria anual vs restante — desenvolvimento: RR 1.39 [0.98, 1.98]; validação: RR 0.82 [0.56, 1.19] |
| H07 | inconclusiva | AUC 0.51 [0.44, 0.59], n = 205, positivos = 73 |
| H08 | avaliar (descritivo) | ver definições e tendência trimestral |
| H09 | apoiada | motivo × feedback concordam 101/379 (26.6%; acaso 26.9%; p acima do acaso = 0.570); 0 de 6 vínculos motivo → comportamento confirmados |
| H10 (exploratória) | apoiada | mecanismo do gerador — desenvolvimento: AUC 0.59 [0.55, 0.64]; validação: AUC 0.62 [0.56, 0.67]; eventos previstos 257.5 vs observados 262 |

## Sinais contínuos (AUC; 0,5 = sem sinal)

| H | Sinal | Parte | n | positivos | AUC [IC 95%] | Principal |
|---|---|---|---:|---:|---|---|
| H01 | queda relativa de uso 30d vs 30d anteriores (base > 0, tenure >= 60d) | desenvolvimento | 1761 | 118 | 0.48 [0.43, 0.53] | sim |
| H01 | queda relativa de uso 30d vs 30d anteriores (base > 0, tenure >= 60d) | validação | 847 | 75 | 0.48 [0.41, 0.55] | sim |
| H01 | queda relativa 14d vs 14d anteriores | desenvolvimento | 1280 | 83 | 0.44 [0.39, 0.50] |  |
| H01 | queda relativa 14d vs 14d anteriores | validação | 612 | 57 | 0.47 [0.39, 0.55] |  |
| H01 | queda relativa 7d vs 7d anteriores | desenvolvimento | 779 | 59 | 0.57 [0.51, 0.63] |  |
| H01 | queda relativa 7d vs 7d anteriores | validação | 372 | 30 | 0.53 [0.45, 0.63] |  |
| H01 | queda absoluta de usage_count 30d | desenvolvimento | 2338 | 158 | 0.48 [0.45, 0.52] |  |
| H01 | queda absoluta de usage_count 30d | validação | 1087 | 104 | 0.52 [0.46, 0.57] |  |
| H01 | dias desde o último uso | desenvolvimento | 2338 | 158 | 0.50 [0.45, 0.54] |  |
| H01 | dias desde o último uso | validação | 1087 | 104 | 0.50 [0.44, 0.55] |  |
| H02 | satisfação média baixa (fechados em 90d, com resposta) | desenvolvimento | 582 | 35 | 0.48 [0.40, 0.59] | sim |
| H02 | satisfação média baixa (fechados em 90d, com resposta) | validação | 273 | 33 | 0.47 [0.37, 0.58] | sim |
| H02 | tempo médio de resolução (90d) | desenvolvimento | 892 | 58 | 0.44 [0.36, 0.51] |  |
| H02 | tempo médio de resolução (90d) | validação | 419 | 45 | 0.47 [0.37, 0.56] |  |
| H02 | primeira resposta média (90d) | desenvolvimento | 892 | 58 | 0.55 [0.47, 0.62] |  |
| H02 | primeira resposta média (90d) | validação | 419 | 45 | 0.55 [0.45, 0.64] |  |
| H02 | escalonamentos (90d) | desenvolvimento | 2338 | 158 | 0.50 [0.49, 0.51] |  |
| H02 | escalonamentos (90d) | validação | 1087 | 104 | 0.51 [0.49, 0.53] |  |
| H02 | tickets urgent/high (90d) | desenvolvimento | 2338 | 158 | 0.52 [0.48, 0.55] |  |
| H02 | tickets urgent/high (90d) | validação | 1087 | 104 | 0.51 [0.47, 0.55] |  |
| H02 | tickets abertos no corte | desenvolvimento | 2338 | 158 | 0.50 [0.50, 0.51] |  |
| H02 | tickets abertos no corte | validação | 1087 | 104 | 0.50 [0.50, 0.52] |  |
| H03 | taxa de erro em 30d (erros / usos) | desenvolvimento | 2018 | 133 | 0.51 [0.45, 0.56] | sim |
| H03 | taxa de erro em 30d (erros / usos) | validação | 921 | 88 | 0.49 [0.42, 0.56] | sim |
| H03 | erros em 90d | desenvolvimento | 2338 | 158 | 0.50 [0.45, 0.54] |  |
| H03 | erros em 90d | validação | 1087 | 104 | 0.47 [0.42, 0.53] |  |
| H03 | uso de feature beta em 30d | desenvolvimento | 2338 | 158 | 0.51 [0.48, 0.53] |  |
| H03 | uso de feature beta em 30d | validação | 1087 | 104 | 0.48 [0.45, 0.52] |  |

## H01 — grupos separados

| Parte | Grupo | conta-meses | positivos | taxa | taxa do restante | RR [IC 95%] |
|---|---|---:|---:|---:|---:|---|
| desenvolvimento | base anterior zero (prev 30d = 0) | 335 | 20 | 6.0% | 6.9% | 0.87 [0.50, 1.30] |
| desenvolvimento | conta nova (tenure < 60d) | 274 | 24 | 8.8% | 6.5% | 1.35 [0.87, 1.91] |
| validação | base anterior zero (prev 30d = 0) | 153 | 16 | 10.5% | 9.4% | 1.11 [0.59, 1.73] |
| validação | conta nova (tenure < 60d) | 108 | 19 | 17.6% | 8.7% | 2.03 [1.25, 3.08] |

## H01 — regra de alerta por queda relativa

| Parte | Limiar | Alertas/mês | Precisão | Recall | Prevalência | Lift |
|---|---:|---:|---:|---:|---:|---:|
| desenvolvimento | 0.1 | 61.2 | 6.3% | 41.8% | 6.8% | 0.94 |
| desenvolvimento | 0.2 | 56.4 | 6.3% | 38.0% | 6.8% | 0.93 |
| desenvolvimento | 0.3 | 50.8 | 6.0% | 32.9% | 6.8% | 0.89 |
| desenvolvimento | 0.4 | 45.2 | 5.7% | 27.8% | 6.8% | 0.85 |
| desenvolvimento | 0.5 | 37.8 | 5.8% | 23.4% | 6.8% | 0.85 |
| desenvolvimento | 0.6 | 31.0 | 6.3% | 20.9% | 6.8% | 0.93 |
| desenvolvimento | 0.7 | 24.2 | 6.3% | 16.5% | 6.8% | 0.93 |
| desenvolvimento | 0.8 | 18.0 | 7.2% | 13.9% | 6.8% | 1.06 |
| desenvolvimento | 0.9 | 14.9 | 8.3% | 13.3% | 6.8% | 1.23 |
| desenvolvimento | 1.0 | 14.6 | 8.0% | 12.7% | 6.8% | 1.19 |
| validação (limiar do desenvolvimento) | 0.1 | 162.0 | 9.1% | 42.3% | 9.6% | 0.95 |

## Segmentos (cada nível contra o restante)

| Segmento | Nível | Parte | conta-meses | contas | positivos | taxa | RR [IC 95%] | MRR exposto | MRR churn |
|---|---|---|---:|---:|---:|---:|---|---:|---:|
| indústria | Cybersecurity | desenvolvimento | 448 | 56 | 36 | 8.0% | 1.24 [0.89, 1.69] | 3279755 | 198578 |
| indústria | DevTools | desenvolvimento | 590 | 72 | 31 | 5.3% | 0.72 [0.46, 1.02] | 4183624 | 145397 |
| indústria | EdTech | desenvolvimento | 299 | 48 | 25 | 8.4% | 1.28 [0.81, 1.83] | 1631166 | 116228 |
| indústria | FinTech | desenvolvimento | 524 | 68 | 32 | 6.1% | 0.88 [0.60, 1.23] | 3953247 | 175564 |
| indústria | HealthTech | desenvolvimento | 477 | 66 | 34 | 7.1% | 1.07 [0.67, 1.53] | 3839525 | 320414 |
| indústria | Cybersecurity | validação | 207 | 74 | 10 | 4.8% | 0.45 [0.20, 0.77] | 2526494 | 103713 |
| indústria | DevTools | validação | 247 | 87 | 30 | 12.1% | 1.38 [0.89, 1.97] | 3095290 | 430564 |
| indústria | EdTech | validação | 174 | 62 | 23 | 13.2% | 1.49 [0.89, 2.17] | 2099520 | 215568 |
| indústria | FinTech | validação | 243 | 87 | 19 | 7.8% | 0.78 [0.44, 1.24] | 3106326 | 205889 |
| indústria | HealthTech | validação | 216 | 75 | 22 | 10.2% | 1.08 [0.62, 1.66] | 2639848 | 273493 |
| canal de aquisição | ads | desenvolvimento | 509 | 67 | 35 | 6.9% | 1.02 [0.67, 1.50] | 3718964 | 270660 |
| canal de aquisição | event | desenvolvimento | 435 | 56 | 26 | 6.0% | 0.86 [0.55, 1.25] | 3016904 | 113193 |
| canal de aquisição | organic | desenvolvimento | 440 | 66 | 33 | 7.5% | 1.14 [0.76, 1.61] | 3931873 | 241645 |
| canal de aquisição | other | desenvolvimento | 494 | 64 | 37 | 7.5% | 1.14 [0.77, 1.57] | 3076976 | 173911 |
| canal de aquisição | partner | desenvolvimento | 460 | 57 | 27 | 5.9% | 0.84 [0.52, 1.26] | 3142600 | 156772 |
| canal de aquisição | ads | validação | 242 | 85 | 18 | 7.4% | 0.73 [0.45, 1.15] | 2971658 | 169528 |
| canal de aquisição | event | validação | 201 | 71 | 22 | 10.9% | 1.18 [0.70, 1.82] | 2136795 | 226653 |
| canal de aquisição | organic | validação | 232 | 83 | 34 | 14.7% | 1.79 [1.13, 2.56] | 3225200 | 516492 |
| canal de aquisição | other | validação | 220 | 78 | 12 | 5.5% | 0.51 [0.28, 0.85] | 2547220 | 91463 |
| canal de aquisição | partner | validação | 192 | 68 | 18 | 9.4% | 0.98 [0.52, 1.57] | 2586605 | 225091 |
| plano inicial | Basic | desenvolvimento | 722 | 100 | 54 | 7.5% | 1.16 [0.85, 1.59] | 5488653 | 355629 |
| plano inicial | Enterprise | desenvolvimento | 739 | 97 | 51 | 6.9% | 1.03 [0.72, 1.44] | 4544807 | 279798 |
| plano inicial | Pro | desenvolvimento | 877 | 113 | 53 | 6.0% | 0.84 [0.60, 1.11] | 6853857 | 320754 |
| plano inicial | Basic | validação | 343 | 122 | 35 | 10.2% | 1.10 [0.71, 1.64] | 4549551 | 403730 |
| plano inicial | Enterprise | validação | 340 | 121 | 28 | 8.2% | 0.81 [0.49, 1.19] | 3777334 | 291877 |
| plano inicial | Pro | validação | 404 | 142 | 41 | 10.1% | 1.10 [0.75, 1.62] | 5140593 | 533620 |
| país | AU | desenvolvimento | 158 | 22 | 10 | 6.3% | 0.93 [0.48, 1.45] | 1051572 | 38756 |
| país | CA | desenvolvimento | 106 | 17 | 10 | 9.4% | 1.42 [0.61, 2.64] | 786038 | 61993 |
| país | DE | desenvolvimento | 182 | 20 | 13 | 7.1% | 1.06 [0.53, 1.71] | 804442 | 97094 |
| país | FR | desenvolvimento | 71 | 12 | 4 | 5.6% | 0.83 [0.20, 1.83] | 547985 | 17328 |
| país | IN | desenvolvimento | 254 | 32 | 14 | 5.5% | 0.80 [0.40, 1.39] | 2056590 | 77916 |
| país | UK | desenvolvimento | 252 | 35 | 20 | 7.9% | 1.20 [0.71, 1.80] | 1701009 | 113604 |
| país | US | desenvolvimento | 1315 | 172 | 87 | 6.6% | 0.95 [0.70, 1.31] | 9939681 | 549490 |
| país | AU | validação | 75 | 26 | 4 | 5.3% | 0.54 [0.13, 1.10] | 1041222 | 49436 |
| país | CA | validação | 57 | 20 | 1 | 1.8% | 0.18 [0.00, 0.70] | 681736 | 589 |
| país | DE | validação | 68 | 23 | 6 | 8.8% | 0.92 [0.15, 2.00] | 649040 | 51015 |
| país | FR | validação | 48 | 17 | 8 | 16.7% | 1.80 [0.40, 3.71] | 616203 | 87834 |
| país | IN | validação | 110 | 38 | 9 | 8.2% | 0.84 [0.37, 1.46] | 1662819 | 179241 |
| país | UK | validação | 125 | 45 | 15 | 12.0% | 1.30 [0.68, 2.08] | 1280450 | 110296 |
| país | US | validação | 604 | 216 | 61 | 10.1% | 1.13 [0.74, 1.71] | 7536008 | 750816 |
| tempo de casa | 180-364d | desenvolvimento | 926 | 209 | 54 | 5.8% | 0.79 [0.57, 1.08] | 7815736 | 442380 |
| tempo de casa | <180d | desenvolvimento | 1137 | 300 | 90 | 7.9% | 1.40 [1.03, 1.92] | 6128756 | 428812 |
| tempo de casa | >=365d | desenvolvimento | 275 | 98 | 14 | 5.1% | 0.73 [0.39, 1.17] | 2942825 | 84989 |
| tempo de casa | 180-364d | validação | 359 | 150 | 34 | 9.5% | 0.98 [0.67, 1.49] | 5346097 | 534669 |
| tempo de casa | <180d | validação | 356 | 157 | 47 | 13.2% | 1.69 [1.18, 2.40] | 3034333 | 405679 |
| tempo de casa | >=365d | validação | 372 | 139 | 23 | 6.2% | 0.55 [0.34, 0.82] | 5087048 | 288879 |
| trial ativo | False | desenvolvimento | 1284 | 244 | 90 | 7.0% | 1.09 [0.80, 1.49] | 9402342 | 580200 |
| trial ativo | True | desenvolvimento | 1054 | 177 | 68 | 6.5% | 0.92 [0.67, 1.25] | 7484975 | 375981 |
| trial ativo | False | validação | 443 | 190 | 45 | 10.2% | 1.11 [0.79, 1.64] | 4863986 | 484953 |
| trial ativo | True | validação | 644 | 243 | 59 | 9.2% | 0.90 [0.61, 1.27] | 8603492 | 744274 |
| maioria das assinaturas anual | False | desenvolvimento | 946 | 197 | 52 | 5.5% | 0.72 [0.51, 1.02] | 6651138 | 359039 |
| maioria das assinaturas anual | True | desenvolvimento | 1392 | 245 | 106 | 7.6% | 1.39 [0.98, 1.98] | 10236179 | 597142 |
| maioria das assinaturas anual | False | validação | 458 | 197 | 49 | 10.7% | 1.22 [0.84, 1.79] | 5583310 | 567858 |
| maioria das assinaturas anual | True | validação | 629 | 261 | 55 | 8.7% | 0.82 [0.56, 1.19] | 7884168 | 661369 |
| alguma assinatura sem auto-renew | False | desenvolvimento | 1132 | 232 | 80 | 7.1% | 1.09 [0.80, 1.49] | 6532843 | 375903 |
| alguma assinatura sem auto-renew | True | desenvolvimento | 1206 | 205 | 78 | 6.5% | 0.92 [0.67, 1.25] | 10354474 | 580278 |
| alguma assinatura sem auto-renew | False | validação | 308 | 139 | 32 | 10.4% | 1.12 [0.72, 1.68] | 2822934 | 210341 |
| alguma assinatura sem auto-renew | True | validação | 779 | 287 | 72 | 9.2% | 0.89 [0.60, 1.39] | 10644544 | 1018886 |
| algum ticket em 90d | False | desenvolvimento | 1450 | 280 | 99 | 6.8% | 1.03 [0.75, 1.39] | 10489576 | 614694 |
| algum ticket em 90d | True | desenvolvimento | 888 | 241 | 59 | 6.6% | 0.97 [0.72, 1.32] | 6397741 | 341487 |
| algum ticket em 90d | False | validação | 668 | 301 | 59 | 8.8% | 0.82 [0.56, 1.20] | 7757535 | 772808 |
| algum ticket em 90d | True | validação | 419 | 210 | 45 | 10.7% | 1.22 [0.83, 1.79] | 5709943 | 456419 |

## H05 — uso por trimestre (período todo)

| Trimestre | Linhas de uso (todas) | usage_count (todas) | Contas elegíveis (média) | usage_count 30d das elegíveis (média mensal) | por conta elegível |
|---|---:|---:|---:|---:|---:|
| 2023Q1 | 3142 | 31400 | 11 | 267 | 24.2 |
| 2023Q2 | 3122 | 31128 | 52 | 1100 | 21.0 |
| 2023Q3 | 3084 | 31155 | 112 | 2539 | 22.7 |
| 2023Q4 | 3082 | 30878 | 170 | 3558 | 21.0 |
| 2024Q1 | 3145 | 31593 | 237 | 5014 | 21.2 |
| 2024Q2 | 3073 | 30789 | 310 | 6453 | 20.8 |
| 2024Q3 | 3148 | 31355 | 388 | 8073 | 20.8 |
| 2024Q4 | 3204 | 32227 | 471 | 10080 | 21.4 |

## H07 — ativação inicial

Contas com signup até 2024-02-29, sem churn nos primeiros 90 dias (51 excluídas). Sinal: menos linhas de uso nos 90 dias após o signup. Desfecho: churn entre os dias 91 e 270. n = 205, positivos = 73, AUC 0.51 [0.44, 0.59].

## H08 — o que é "churn" depende da fonte

| Definição | Valor | Denominador |
|---|---:|---:|
| accounts.churn_flag = True | 110 | 500 |
| contas com >= 1 evento em churn_events | 352 | 500 |
| eventos de churn (total) | 600 | 500 |
| contas com evento e churn_flag = False | 277 | 352 |

| Trimestre | conta-meses | positivos | taxa mensal | taxa por MRR | teste reservado |
|---|---:|---:|---:|---:|---|
| 2023Q1 | 33 | 2 | 6.1% | 6.0% |  |
| 2023Q2 | 157 | 9 | 5.7% | 7.2% |  |
| 2023Q3 | 336 | 18 | 5.4% | 4.1% |  |
| 2023Q4 | 509 | 33 | 6.5% | 5.2% |  |
| 2024Q1 | 711 | 43 | 6.0% | 5.1% |  |
| 2024Q2 | 929 | 83 | 8.9% | 7.0% |  |
| 2024Q3 | 1165 | 126 | 10.8% | 9.8% |  |
| 2024Q4 | 914 | 123 | 13.5% | 11.2% | sim |

## H09 — motivos declarados

Motivo × feedback: 101 de 379 concordam (26.6%); esperado pelo acaso 26.9%; p (acima do acaso, 2.000 permutações) = 0.570. Comportamento nos 90 dias antes do evento: 542 de 600 eventos com conta elegível na véspera.

| Motivo | Comportamento | Esperado | n | média no motivo | média nos demais | razão [IC 95%] | confirmado |
|---|---|---|---:|---:|---:|---|---|
| support | tickets_90d | mais tickets | 98 | 0.54 | 0.51 | 1.06 [0.80, 1.33] | não |
| support | mean_satisfaction_90d | satisfação menor | 26 | 4.33 | 4.02 | 1.08 [1.00, 1.15] | não |
| features | distinct_features_30d | menos features usadas | 103 | 2.09 | 2.05 | 1.02 [0.86, 1.18] | não |
| features | usage_count_30d | menos uso | 103 | 21.46 | 20.64 | 1.04 [0.86, 1.23] | não |
| pricing | mrr_active | MRR maior | 83 | 9414.52 | 11358.64 | 0.83 [0.63, 1.06] | não |
| budget | mrr_active | MRR maior | 91 | 11668.77 | 10938.27 | 1.07 [0.86, 1.32] | não |

## H10 (exploratória) — o churn segue o mecanismo do gerador do dataset?

Hipótese surgida ao ver os resultados (2026-10-26 19:14): cada conta recebe ~1.20 eventos em datas uniformes entre o signup e o fim dos dados. O 'risco do gerador' usa o fim dos dados, que não é conhecido em t: serve para diagnóstico e é proibido como feature.

| Tempo de vida até o fim dos dados | Contas | Eventos por conta | Vida média (dias) | Eventos por conta-mês |
|---|---:|---:|---:|---:|
| <180d | 150 | 1.14 | 91 | 0.383 |
| 180-364d | 123 | 1.24 | 266 | 0.141 |
| 365-544d | 116 | 1.33 | 449 | 0.090 |
| 545-730d | 111 | 1.11 | 640 | 0.053 |

Posição do evento entre o signup (0) e o fim dos dados (1), quantis 10/25/50/75/90%: 0.11 / 0.26 / 0.50 / 0.76 / 0.90 (uniforme = 0,10 / 0,25 / 0,50 / 0,75 / 0,90).

| Sinal | Parte | n | positivos | AUC [IC 95%] |
|---|---|---:|---:|---|
| risco do gerador: 30 / dias entre signup e fim dos dados (não é feature) | desenvolvimento | 2338 | 158 | 0.59 [0.55, 0.64] |
| tempo de casa curto | desenvolvimento | 2338 | 158 | 0.57 [0.52, 0.62] |
| churns anteriores | desenvolvimento | 2338 | 158 | 0.49 [0.45, 0.53] |
| risco do gerador: 30 / dias entre signup e fim dos dados (não é feature) | validação | 1087 | 104 | 0.62 [0.56, 0.67] |
| tempo de casa curto | validação | 1087 | 104 | 0.61 [0.56, 0.67] |
| churns anteriores | validação | 1087 | 104 | 0.42 [0.38, 0.47] |

Curva por corte (desenvolvimento + validação): correlação entre taxa observada e prevista pelo mecanismo = 0.57.

| Corte | Elegíveis | Observados | Previstos | Taxa observada | Taxa prevista |
|---|---:|---:|---:|---:|---:|
| 2023-01-31 | 2 | 0 | 0.1 | 0.0% | 4.8% |
| 2023-02-28 | 10 | 1 | 0.5 | 10.0% | 5.0% |
| 2023-03-31 | 21 | 1 | 1.1 | 4.8% | 5.1% |
| 2023-04-30 | 36 | 3 | 1.9 | 8.3% | 5.2% |
| 2023-05-31 | 50 | 4 | 2.6 | 8.0% | 5.3% |
| 2023-06-30 | 71 | 2 | 3.8 | 2.8% | 5.4% |
| 2023-07-31 | 89 | 6 | 4.9 | 6.7% | 5.4% |
| 2023-08-31 | 116 | 5 | 6.5 | 4.3% | 5.6% |
| 2023-09-30 | 131 | 7 | 7.6 | 5.3% | 5.8% |
| 2023-10-31 | 149 | 7 | 8.9 | 4.7% | 5.9% |
| 2023-11-30 | 170 | 10 | 10.5 | 5.9% | 6.1% |
| 2023-12-31 | 190 | 16 | 12.1 | 8.4% | 6.4% |
| 2024-01-31 | 216 | 8 | 14.3 | 3.7% | 6.6% |
| 2024-02-29 | 235 | 18 | 16.1 | 7.7% | 6.9% |
| 2024-03-31 | 260 | 17 | 18.7 | 6.5% | 7.2% |
| 2024-04-30 | 282 | 21 | 21.3 | 7.4% | 7.6% |
| 2024-05-31 | 310 | 32 | 25.0 | 10.3% | 8.1% |
| 2024-06-30 | 337 | 30 | 29.0 | 8.9% | 8.6% |
| 2024-07-31 | 365 | 34 | 34.2 | 9.3% | 9.4% |
| 2024-08-31 | 385 | 40 | 38.5 | 10.4% | 10.0% |

## Carteira em 2024-12-31 no segmento com risco maior (tempo de casa < 180 dias)

149 de 500 contas, MRR 3124317 de 10159608 (30.8%). Ordenadas por MRR. **Não é score de risco**: o segmento é o único com RR acima de 1 nas duas partes, mas o efeito é compatível com o mecanismo do gerador (H10). Lista completa em `solution/outputs/diagnosis/accounts_attention.csv`; abaixo, as 15 de maior MRR.

| Conta | Indústria | Plano inicial | Dias de casa | MRR | Assinaturas ativas | Churns anteriores | Tickets 90d |
|---|---|---|---:|---:|---:|---:|---:|
| A-d4e0d4 | FinTech | Basic | 74 | 114777 | 9 | 0 | 0 |
| A-5c046d | EdTech | Basic | 178 | 83886 | 8 | 0 | 0 |
| A-18793f | EdTech | Basic | 13 | 75776 | 10 | 1 | 0 |
| A-c58f49 | EdTech | Enterprise | 153 | 70980 | 7 | 3 | 0 |
| A-4814a3 | Cybersecurity | Basic | 105 | 70644 | 10 | 1 | 0 |
| A-09316c | FinTech | Enterprise | 111 | 70000 | 11 | 1 | 2 |
| A-e08cd3 | FinTech | Pro | 101 | 67737 | 10 | 2 | 2 |
| A-0cc442 | EdTech | Basic | 166 | 60092 | 11 | 4 | 0 |
| A-66224b | HealthTech | Pro | 74 | 50876 | 11 | 0 | 2 |
| A-e60f9d | FinTech | Basic | 127 | 50095 | 13 | 0 | 0 |
| A-bd4513 | DevTools | Enterprise | 55 | 48804 | 10 | 2 | 1 |
| A-76fa4d | HealthTech | Pro | 37 | 47955 | 5 | 2 | 1 |
| A-9174e0 | Cybersecurity | Basic | 27 | 46613 | 14 | 0 | 1 |
| A-0651a4 | HealthTech | Pro | 76 | 44564 | 14 | 2 | 0 |
| A-902ef7 | HealthTech | Enterprise | 119 | 44322 | 8 | 1 | 0 |
