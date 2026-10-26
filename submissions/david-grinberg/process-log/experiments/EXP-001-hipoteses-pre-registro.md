# EXP-001 — Teste das hipóteses H01–H09: pré-registro
Estado: **pré-registro**, escrito em 2026-10-26T19:09-03:00, antes de qualquer comparação entre churn e features ou segmentos. Os resultados vão em `docs/hypotheses-results.md` e não alteram este arquivo.
Issue: DAV-184. Dados: base limpa (DAV-201) e snapshots (DAV-181), commit 307f60e. Premissas P-01 a P-03 (DEC-015, DEC-018).

## Partição temporal (DEC-019, proposta do Claude Code, revisão pendente)
Com H = 30 dias e purga (o rótulo do último corte de cada parte termina antes do primeiro corte da parte seguinte):

| Parte | Cortes | Uso |
|---|---|---|
| Desenvolvimento | 2023-01-31 a 2024-05-31 | exploração, faixas e limiares |
| Validação | 2024-06-30 a 2024-08-31 | avaliação fora da amostra dos alertas de H01; seleção de modelo na DAV-189 |
| **Teste final** | 2024-09-30 a 2024-11-30 | **reservado para a DAV-189**; nenhuma comparação de features ou segmentos olha estes cortes |
| Pontuação | 2024-12-31 | carteira atual, sem rótulo |

Exceções descritivas, que não escolhem features: a tendência agregada do churn (H08) e o volume de uso por trimestre (H05) usam o período todo, porque as contagens agregadas já foram vistas na S-003. A H09 usa todos os eventos, porque motivos são campos proibidos como preditor.

## Medidas
- **Taxa:** eventos de churn em (t, t+30] por conta-mês elegível (linhas de snapshot com rótulo conhecido). IC 95% por bootstrap de Poisson agrupado por conta (B = 1.000, semente 20261026), porque linhas da mesma conta são dependentes.
- **Contraste:** razão de risco (RR) entre o grupo de interesse e o de referência, com IC 95% bootstrap. Sinal univariado: AUC da feature contínua, com IC bootstrap agrupado (B = 300).
- **Critério de classificação**, definido antes de ver os dados:
  - *apoiada*: IC 95% da métrica principal exclui o nulo (RR = 1 ou AUC = 0,5) na direção prevista, em desenvolvimento **e** validação;
  - *refutada*: IC 95% exclui o nulo na direção oposta, ou IC estreito em torno do nulo em ambas as partes (|log RR| < 0,1 ou |AUC − 0,5| < 0,03 nos dois limites);
  - *inconclusiva*: os demais casos;
  - *não testável*: os dados não permitem medir a hipótese.
- **Múltiplas comparações:** só a métrica principal decide o status. As secundárias são exploratórias e citadas como tal.

## Métrica principal por hipótese
| H | Métrica principal | Secundárias (exploratórias) |
|---|---|---|
| H01 | AUC de `−queda relativa de usage_count` 30d vs 30d anteriores (contas com base anterior > 0) | janelas 7/14d; queda absoluta; dias desde o último uso; base zero e contas com < 60 dias separadas; regras de alerta com limiar escolhido no desenvolvimento e avaliado na validação (precisão, recall, alertas por mês) |
| H02 | RR de churn: ≥ 1 ticket em 90d vs nenhum; e AUC de `−mean_satisfaction_90d` entre quem tem resposta | resolução, primeira resposta, escalonamentos, tickets abertos, urgent/high; estratificação por tenure |
| H03 | AUC da taxa de erro em 30d (errors_30d / usage_count_30d; contas com uso) | errors_90d; uso beta |
| H04 | RR por segmento contra o restante: indústria, canal, plano inicial, país, faixa de tenure, trial ativo | MRR exposto e MRR perdido por segmento; contas novas (< 180 dias) × maduras |
| H05 | uso total e por conta ativa, por trimestre (período todo) | por coorte de signup |
| H06 | RR: share_active_annual ≥ 0,5 vs < 0,5 | assinaturas sem auto-renew; nº de assinaturas ativas; faixa de MRR |
| H07 | AUC das linhas de uso nos primeiros 90 dias após o signup para churn nos 180 dias seguintes (contas com signup até 2024-02-29) | — |
| H08 | comparação das taxas de churn por definição (flag, contas com evento, eventos por conta-mês) e tendência trimestral | — |
| H09 | concordância reason_code × feedback (101/379, já medida) e diferença de comportamento nos 90 dias antes do evento entre motivos | — |

Hipóteses novas (H10+) que surgirem ao olhar os dados serão marcadas como exploratórias e datadas.
