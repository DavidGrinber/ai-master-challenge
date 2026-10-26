# S-006 — Diagnóstico e teste das hipóteses (DAV-184)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issue: [DAV-184](https://linear.app/david-grinberg/issue/DAV-184/03-investigar-churn-e-testar-hipoteses). Escopo absorvido: DAV-185 a DAV-188 (critérios lidos no Linear).
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompt do candidato (literal)
> sim

(Resposta a "O que está em aberto agora não depende de você: a próxima etapa é a DAV-184 (diagnóstico e teste das hipóteses H01–H09). Quer que eu comece?")

## Objetivo
Testar H01–H09 com evidência verificável, sem tocar no período que o modelo vai usar como teste final, e separar correlação de causa.

## Ações e saídas observadas
1. **Pré-registro** (19:09), antes de qualquer comparação: `process-log/experiments/EXP-001-hipoteses-pre-registro.md`. Fixa a partição temporal com purga (DEC-019), a métrica principal de cada hipótese, o critério de status, o bootstrap agrupado por conta e o tratamento de múltiplas comparações.
2. `solution/src/diagnose.py`, 1ª execução: H01, H02, H03, H06 e H07 inconclusivas; H04 apoiada só para tempo de casa < 180 dias; H09 apoiada.
3. **Exploração H10** (19:13–19:14, registrada como exploratória em `docs/02-hipoteses.md`):
   - taxa por semestre × faixa de tempo de casa: o churn sobe em **todas** as faixas;
   - eventos por conta: 1,14 / 1,24 / 1,33 / 1,11 por faixa de tempo de vida, ou seja, independem da duração;
   - posição relativa dos eventos no tempo de vida: 0,11 / 0,26 / 0,50 / 0,76 / 0,90, praticamente uniforme;
   - modelo nulo "k eventos uniformes em [signup, fim]": 257,5 previstos contra 262 observados e AUC 0,59 / 0,62, acima de todos os sinais de comportamento.
4. H10, carteira atual por MRR e o uso total das elegíveis (H05) foram incorporados ao script. `docs/diagnosis-findings.md` foi escrito com a interpretação, e conferi os números citados contra as saídas geradas.
5. `solution/tests/test_diagnose.py`: regra de status, contraste de taxas, AUC e garantia de que a partição nunca toca o teste reservado.

## Verificações
- `pytest` → 33 passed.
- Recalculei à mão parte das tabelas, inclusive a curva observada × prevista, por fora do script, antes de incorporá-las.
- Determinismo: semente fixa (20261026); duas execuções produziram status e segmentos idênticos.

## Erros reais e correções
1. Rascunho deixado em `run_h05` (uma linha sem sentido sobrescrita na linha seguinte): removido antes de usar o resultado.
2. **H09, vínculo "support → satisfação menor":** usei a satisfação com sinal negativo e testei razão > 1. Com médias negativas, o sentido se inverte. Os números brutos mostravam o contrário do esperado (4,33 contra 4,02). Corrigido para satisfação direta com razão < 1; a conclusão (vínculo não confirmado) não mudou.
3. **Bug no IC por bootstrap:** com razões infinitas (grupo pequeno sem positivos numa réplica), a interpolação de percentis dava NaN. O teste unitário pegou o problema. Nenhum resultado real tinha IC NaN ou infinito (conferido). Corrigido com `_ci`, que usa o percentil mais próximo só quando há infinito; os resultados reais ficaram idênticos (comparação byte a byte de `hypothesis_status.csv` e `segments.csv`).
4. Título da seção de carteira derivava o ano do período de teste; trocado pela data de referência real.

## Decisões
- Do Claude Code, revisão pendente: partição DEC-019; interpretação em `docs/diagnosis-findings.md`; H05 classificada por julgamento ("refutada na forma"), porque o pré-registro não tinha regra numérica para ela.
- **Para o candidato decidir na DAV-189 (DEC-020):** escopo preditivo diante da H10.

## Tempo
Não cronometrado. Timestamps observados (-03:00): DAV-184 iniciada ~19:08; pré-registro 19:09; H10 19:14.

## Commit
SHA no comentário de fechamento da DAV-184.
