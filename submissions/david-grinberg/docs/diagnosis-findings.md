# Diagnóstico — achados (DAV-184)

Interpretação escrita pelo Claude Code em 2026-10-26 sobre os números gerados em [hypotheses-results.md](hypotheses-results.md) (`solution/src/diagnose.py`), seguindo o pré-registro [EXP-001](../process-log/experiments/EXP-001-hipoteses-pre-registro.md).
Comparações usam desenvolvimento (cortes até mai/2024) e validação (jun–ago/2024). O teste final (set–nov/2024) ficou intocado para a DAV-189. **Validação desta interpretação pelo candidato: pendente.**
Premissas P-01 a P-03 em [data-contract.md](data-contract.md). Os dados são simulados.

## Resposta curta

1. **O churn subiu de fato.** A taxa mensal de churn por conta elegível ficou entre 5,4% e 6,5% nos trimestres de 2023, foi a 8,9% no 2º tri/2024 e a 10,8% no 3º tri/2024. No 4º tri/2024, período reservado e só descritivo, chegou a 13,5%. Pesada por MRR, a taxa passou de 4–7% para 9,8%.
2. **Nenhum comportamento disponível antecipa o churn.** Queda de uso (janelas de 7, 14 e 30 dias), tickets, satisfação, tempo de resolução, primeira resposta, escalonamentos e erros dão AUC entre 0,47 e 0,51. Plano, indústria, canal, país, trial, cobrança anual e auto-renew dão RR com IC contendo 1 ou com sinal que muda entre períodos.
3. **A subida é estrutural, não comportamental (H10, exploratória).** Cada conta tem cerca de 1,2 evento de churn, qualquer que seja o tempo de vida, e as datas caem uniformemente entre o cadastro e o fim dos dados. Esse mecanismo, sozinho, prevê 257,5 eventos contra 262 observados, reproduz a curva de 5% para 10% ao mês e é o único "sinal" acima do acaso (AUC 0,59 e 0,62). Contas novas "churnam mais" porque o mesmo número de eventos cabe numa janela menor. É compatível com o gerador do dataset simulado e incompatível com um churn real contínuo, em que contas mais antigas acumulariam mais eventos.
4. **"Algo não bate" porque cada time olha um indicador sem relação com o churn nestes dados**, e o próprio número de churn depende da fonte:
   - "o churn subiu": verdade, mas 110 contas pelo `churn_flag` contra 352 pelos eventos (H08);
   - "o uso cresceu": só no agregado. O uso total dos clientes ativos ficou 38× maior (de 267 para 10.080 por mês) porque a base passou de ~11 para ~471 contas; por conta, ficou estável (21,0 → 21,4 usos/mês). E o uso não diferencia quem sai (AUC 0,48);
   - "a satisfação está ok": a escala observada só tem notas 3, 4 e 5, 41% dos tickets ficam sem resposta, e a satisfação não prevê churn (AUC 0,48 e 0,47). Quem saiu alegando "support" tinha satisfação média **maior** (4,33 contra 4,02; n = 26).
5. **Os motivos declarados não explicam o churn (H09).** `reason_code` concorda com o feedback em 26,6% dos casos, contra 26,9% esperado pelo acaso (p = 0,57). Nenhum motivo corresponde ao comportamento esperado nos 90 dias anteriores (0 de 6 vínculos).

## Matriz de hipóteses

| H | Status final | Evidência principal | Leitura |
|---|---|---|---|
| H01 queda de uso antecede churn | inconclusiva, sem sinal | AUC 0,48 [0,43–0,53] e 0,48 [0,41–0,55]; 7d e 14d iguais | Regra de alerta por queda, com limiar escolhido no desenvolvimento: na validação, 162 alertas/mês, precisão 9,1% contra prevalência 9,6% (lift 0,95). **Não usar queda de uso como gatilho do CS.** |
| H02 suporte → churn | inconclusiva | ticket em 90d: RR 0,97 [0,72–1,32] e 1,22 [0,83–1,79]; satisfação AUC 0,48 e 0,47 | Sem associação detectável. Causalidade reversa (quem usa mais abre mais tickets) não chega a ser relevante, porque não há efeito a explicar. |
| H03 erros técnicos → churn | inconclusiva | taxa de erro AUC 0,51 [0,45–0,56] e 0,49 [0,42–0,56] | Sem sinal; erros em 90d e uso de beta também ~0,5. |
| H04 perfis diferem | apoiada **só para tempo de casa < 180 dias** | RR 1,40 [1,04–1,92] e 1,69 [1,18–2,40]; 1 de 25 níveis | Explicado pelo mecanismo da H10. Indústria, canal, plano, país e trial não diferem de forma consistente. |
| H05 crescimento agregado esconde deterioração | refutada na forma (julgamento; sem regra numérica pré-registrada) | uso por conta elegível estável; total cresce com a base | O "uso cresceu" é composição: mais clientes, mesmo uso por cliente. Não há deterioração por conta detectável. |
| H06 cobrança/renovação | inconclusiva | maioria anual: RR 1,39 [0,98–1,98] e 0,82 [0,56–1,19] | O sinal inverte entre períodos. Sem data de renovação nos dados, a proximidade da renovação não é testável. |
| H07 ativação fraca | inconclusiva | AUC 0,51 [0,44–0,59]; n = 205; 73 positivos | O uso nos primeiros 90 dias não prevê churn entre os dias 91 e 270, e as datas de uso não seguem o signup (P-03). |
| H08 definições distorcem a leitura | apoiada (descritivo) | 110 contas (flag) × 352 (eventos) × 600 eventos; 277 contas com evento e flag False; todas seguem ativas | O número de churn depende da fonte escolhida. |
| H09 motivos não se sustentam | apoiada | concordância no nível do acaso; 0/6 vínculos | `reason_code` não deve orientar ações nem features. |
| H10 (exploratória) mecanismo do gerador | apoiada | AUC 0,59 [0,55–0,64] e 0,62 [0,56–0,67]; 257,5 previstos × 262 observados; churns anteriores *reduzem* o risco (AUC 0,42 [0,38–0,47] na validação) | Assinatura de um "estoque" fixo de eventos por conta. É a explicação mais simples para a subida e para o efeito de tempo de casa. |

"Inconclusiva" segue a regra pré-registrada: o IC não era estreito o bastante (±0,03 de AUC) para declarar efeito nulo. Na prática, as estimativas ficam entre 0,47 e 0,51, e os dados descartam efeitos maiores que modestos.

## Correlação × causa

- Nada aqui demonstra causa. A associação entre tempo de casa e churn é explicada por um mecanismo de geração dos dados, então não indica que onboarding reduziria churn.
- Ausência de associação não prova ausência de efeito numa operação real: com P-03 (datas de uso e tickets incoerentes), sinais que existiriam na prática podem ter sido apagados.
- Nenhuma ação tem impacto causal estimável com estes dados. Qualquer intervenção do CS precisa de teste controlado (grupo de controle) para medir retenção incremental.

## Segmentos e contas

- **Segmento com risco maior:** contas com menos de 180 dias. Em 2024-12-31 são 149 de 500 contas e US$ 3,12 milhões de MRR (30,8% do total). Lista completa por MRR em `solution/outputs/diagnosis/accounts_attention.csv`. As cinco maiores:
  - A-d4e0d4 (FinTech, 74 dias, US$ 114.777/mês);
  - A-5c046d (EdTech, 178 dias, US$ 83.886);
  - A-18793f (EdTech, 13 dias, US$ 75.776);
  - A-c58f49 (EdTech, 153 dias, US$ 70.980);
  - A-4814a3 (Cybersecurity, 105 dias, US$ 70.644).
- **Isso não é um score.** O risco do segmento vem do mecanismo H10. O que é robusto é o **valor exposto**: perder uma conta de US$ 114 mil/mês não é o mesmo que perder uma de US$ 171. Enquanto não houver sinal de risco confiável, priorizar por MRR é a alavanca defensável.

## Implicações para as próximas etapas

- **DAV-189 (modelo), decisão do candidato.** Um modelo honesto, com features só até t, deve aprender no máximo o tempo de casa (AUC 0,57–0,61), ou seja, uma aproximação do mecanismo do gerador. Opções: (a) treinar e reportar a comparação com um ranking simples por tempo de casa e MRR, aceitando "não supera" como resultado; (b) reduzir o escopo: painel com prioridade transparente por valor e idade da conta, sem probabilidade.
- **DAV-193/194 (painel):** não exibir "probabilidade de churn". Mostrar valor exposto, idade da conta, histórico e limitações. Um alerta por queda de uso seria pior que o acaso (lift 0,95).
- **DAV-198 (recomendações):** a recomendação principal tende a ser de **dados e instrumentação**, antes de modelo:
  1. uma única definição de churn;
  2. uso e tickets ligados ao ciclo de vida da conta, com datas válidas;
  3. escala de satisfação completa e taxa de resposta acompanhada;
  4. motivo de cancelamento estruturado e conferido.

  Como ação de baixo arrependimento: acompanhamento das contas novas de maior MRR, com grupo de controle para medir efeito.
