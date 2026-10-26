# Model card — churn-lr-v1 (DAV-189)

Escrito pelo Claude Code em 2026-10-26 a partir de [model-evaluation.md](model-evaluation.md), gerado por `solution/src/model.py`. Pré-registro: [EXP-002](../process-log/experiments/EXP-002-modelo-pre-registro.md). Revisão do candidato: pendente.

## Resultado em uma frase
A regressão logística **não supera** o ranking simples por tempo de casa: no teste, fica significativamente abaixo dele. **O painel deve priorizar pelo ranking transparente, e o modelo não deve exibir probabilidade.**

## Objetivo, população, alvo e horizonte
- Priorizar contas para o CS. Unidade: conta elegível (signup ≤ t e assinatura ativa) × fim de mês.
- Alvo: `churn_next_30d`, evento de churn em (t, t+30] (P-01). **H = 30 dias**: único horizonte compatível com a partição com purga sem perder cortes de teste (DEC-021).

## Dados e features
- Snapshots da DAV-181 (linhagem: SHA-256 de `base_manifest.json` em `solution/models/model_meta.json`). Dados simulados.
- 37 features numéricas e 4 categóricas, todas conhecidas em t (data-contract.md). Pré-processamento ajustado só no treino: mediana + indicador de ausência → log1p → padronização; one-hot.
- Proibidos e conferidos por teste automatizado: `churn_flag`, `is_trial` e `seats` da conta, motivos, refund, feedback, o "risco do gerador" (H10), identificadores e datas.

## Treino, seleção e teste
| Parte | Cortes | Linhas | Positivos | Prevalência |
|---|---|---:|---:|---:|
| Treino | 2023-01 a 2024-05 | 2.338 | 158 | 6,8% |
| Validação | 2024-06 a 2024-08 | 1.087 | 104 | 9,6% |
| Teste (avaliado uma vez) | 2024-09 a 2024-11 | 1.329 | 175 | 13,2% |

- C escolhido na validação: 0,01, o mais regularizado da grade. Todos os valores de C ficaram abaixo da referência.
- Challenger (gradient boosting): **não testado**, porque a logística não superou a referência na validação (regra do EXP-002).

## Métricas fora do treino
| Parte | Ranking | AP [IC 95%] | ROC-AUC [IC 95%] |
|---|---|---|---|
| Validação | M1 logística | 0,122 [0,090–0,170] | 0,541 [0,48–0,60] |
| Validação | **B1 tempo de casa** | **0,133** [0,104–0,173] | 0,613 [0,55–0,67] |
| Teste | M1 logística | 0,231 [0,190–0,293] | 0,641 [0,59–0,69] |
| Teste | **B1 tempo de casa** | **0,302** [0,244–0,379] | 0,693 [0,65–0,74] |
| Teste | B0 aleatório | 0,142 [0,120–0,179] | 0,516 [0,47–0,56] |
| Teste | B2 MRR | 0,111 [0,093–0,140] | 0,414 [0,36–0,46] |

- Diferença pareada M1 − B1 no teste: AP −0,070 [−0,115; −0,029] e ROC-AUC −0,052 [−0,077; −0,028]. O modelo é pior; as features de comportamento só acrescentam ruído.
- O MRR alto vem associado a **menos** churn (AUC 0,41 [0,36–0,46]), o que é coerente com a H10: contas antigas têm mais assinaturas e taxa menor.

## Calibração
O modelo prevê 8,1% em média, contra 13,2% observados no teste (diferença relativa de 38%), e o maior erro por decil é de 18,5 p.p. O Brier é igual ao de uma previsão constante (0,1142 × 0,1143). **Pela regra pré-registrada, nenhuma probabilidade é exibida; só o percentil.** A deriva vem da prevalência crescente (H10).

## Priorização (teste, top-K por mês)
| Ranking | Capacidade | Alertas/mês | Falsos alertas/mês | Precisão | Recall | MRR coberto |
|---|---:|---:|---:|---:|---:|---:|
| B1 tempo de casa | 10% | 44,7 | 27,7 | 38,1% | 29,1% | 15,9% |
| M1 logística | 10% | 44,7 | 30,7 | 31,3% | 24,0% | 22,1% |
| B2 MRR | 10% | 44,7 | 41,0 | 8,2% | 6,3% | 21,1% |
| B1 tempo de casa | 20% | 88,7 | 62,3 | 29,7% | 45,1% | 33,9% |

- **Antecedência mediana:** 13 dias entre o corte mensal e o churn capturado.
- **Escolha para o CS:** "pegar mais contas" (tempo de casa) não é o mesmo que "proteger mais receita" (MRR). A regra de acionamento e a capacidade são decididas na DAV-193.
- **O teste já foi usado.** Uma regra nova, como risco × valor, só pode ser comparada na validação, e essa limitação deve ser declarada.

## Sinais e limites causais
- No modelo final, o coeficiente mais forte é `tenure_days` (−0,33: mais tempo de casa, menos risco). Vêm depois `usage_rows_to_date` (+0,18), `n_subs_started_90d` (+0,12) e `tickets_to_date` (+0,11). Os sinais positivos de uso e tickets acumulados não têm leitura de negócio coerente e são compatíveis com o ruído das datas (P-03).
- Nada aqui é causal. Mesmo o efeito do tempo de casa é explicado pelo mecanismo de geração dos dados (H10), então a validade do ranking numa operação real **não está demonstrada**.

## Inferência
- `python solution/src/model.py` reproduz tudo: seleção, avaliação, modelo final ajustado em treino + validação + teste e scores.
- `solution/outputs/scores/scores_2024-12-31.csv` (500 contas): `account_id`, `reference_date`, `horizon_days`, `model_version`, `model_score`, `model_percentile`, `tenure_days`, `tenure_percentile`, `mrr_active`, `recommended_ranking` (= "tempo de casa"), `probability_reliable` (= False) e `top_signals`.
- O modelo serializado (`solution/models/churn-lr-v1.joblib`) fica fora do Git. Um teste confirma que ele reproduz os scores publicados.

## Limitações e uso indevido
- **Não usar como probabilidade** nem para estimar receita em risco.
- Não interpretar coeficientes como causas.
- O ranking por tempo de casa só funciona aqui porque reflete o gerador. Numa operação real, precisa de validação prospectiva, com grupo de controle.
- A prevalência cresce muito ao longo do tempo: qualquer limiar fixo envelhece rápido.
- Linhas da mesma conta em cortes diferentes são dependentes; os ICs usam bootstrap agrupado por conta, mas o teste cobre só 3 meses.
