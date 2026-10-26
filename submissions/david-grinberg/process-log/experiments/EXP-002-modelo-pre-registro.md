# EXP-002 — Modelo de churn: pré-registro
Estado: **pré-registro**, escrito em 2026-10-26T19:25-03:00, antes de treinar qualquer modelo. Os resultados vão em `docs/model-card.md` e `solution/outputs/model/`, e não alteram este arquivo.
Issue: DAV-189. Decisão do candidato: opção (a) da DEC-020, um modelo enxuto comparado com ranking simples, aceitando "não supera" como resultado. Base: snapshots da DAV-181 no commit e0f9db9.

## Alvo, horizonte e população
- Alvo: `churn_next_30d`, algum evento de churn em (t, t+30] (P-01).
- **H = 30 dias** (proposta do Claude Code, revisão pendente). É o único horizonte compatível com a partição com purga do EXP-001 sem perder cortes de teste; com 60 ou 90 dias, o teste reservado ficaria com 1 ou 2 cortes.
- População: contas elegíveis em cada fim de mês (DEC-016/017).

## Partição (DEC-019, igual ao EXP-001)
- Treino: cortes 2023-01-31 a 2024-05-31.
- Validação: 2024-06-30 a 2024-08-31, para escolher o hiperparâmetro e decidir se testa o challenger.
- **Teste:** 2024-09-30 a 2024-11-30, **avaliado uma única vez**, depois de tudo escolhido.
- Modelo final para pontuar a carteira em 2024-12-31: reajustado em treino + validação + teste, com os hiperparâmetros já escolhidos.

## Concorrentes
| ID | Ranking | Papel |
|---|---|---|
| B0 | aleatório (prevalência) | piso |
| B1 | tempo de casa curto (`-tenure_days`) | **referência simples**: o único sinal com efeito no EXP-001 |
| B2 | MRR ativo | ranking por valor, para comparar MRR coberto |
| M1 | regressão logística L2 sobre as features permitidas do contrato de dados | modelo interpretável |
| M2 | HistGradientBoosting | challenger, **só testado se M1 superar B1 na validação** (IC 95% da diferença de AP acima de 0) |

Features de M1: as colunas numéricas e categóricas permitidas de `snapshots.csv` (data-contract.md), exceto identificadores, datas e rótulos.
- Pré-processamento, ajustado só no treino: mediana + indicador de ausência → log1p → padronização para as numéricas; one-hot para as categóricas.
- Proibidos e conferidos por teste: `churn_flag`, `is_trial` da conta, `seats` da conta, motivos, refund, feedback e o "risco do gerador" da H10.
- Hiperparâmetro: C ∈ {0,01; 0,03; 0,1; 0,3; 1}, escolhido pela maior AP na validação.

## Métricas
- **Principal: average precision (PR-AUC)**, sempre comparada com a prevalência. Complementar: ROC-AUC.
- IC 95% por bootstrap de Poisson agrupado por conta (B = 500, semente 20261026). Diferenças M1 − B1 pareadas, com as mesmas réplicas.
- Priorização por corte, com capacidade top-K de 10% e de 20% das contas elegíveis: precisão, recall, falsos alertas por mês, MRR coberto (MRR dos churns capturados ÷ MRR de todos os churns) e antecedência (dias entre o corte e o churn capturado).
- Calibração de M1 no teste: Brier e tabela por decil. **Probabilidade só será exibida** se a taxa média prevista e a observada no teste diferirem em menos de 20% relativos e não houver decil com erro absoluto acima de 5 p.p. Caso contrário, só o ranking (percentil).

## Regra de decisão
- M1 (ou M2) **supera** B1 se o IC 95% da diferença de AP no teste ficar acima de 0. Se não superar, o painel usa ranking transparente e o modelo fica documentado como resultado negativo.
- A regra de acionamento recomendada (top-K) depende da capacidade do CS, definida na DAV-193. Aqui só se reportam as duas capacidades acima.
