# S-007 — Modelo de churn e avaliação honesta (DAV-189)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issue: [DAV-189](https://linear.app/david-grinberg/issue/DAV-189/04-construir-e-validar-modelo-preditivo-de-churn).
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompt do candidato (literal)
> a

(Escolha da opção (a) da DEC-020: treinar um modelo simples, compará-lo com um ranking por tempo de casa e MRR e aceitar "não supera" como resultado.)

## Ações e saídas observadas
1. **Pré-registro** (19:25), antes de treinar: `process-log/experiments/EXP-002-modelo-pre-registro.md`. Define H = 30, concorrentes B0/B1/B2/M1 (M2 condicional), métrica principal AP, regra de decisão, critério numérico para exibir probabilidade e capacidades top-K de 10% e 20%.
2. `solution/src/model.py`, execução única (~10 s):
   - seleção de C na validação: todos os valores ficaram abaixo de B1; C = 0,01 (AP 0,122 contra 0,133 de B1);
   - M1 − B1 na validação: −0,012 [−0,028; 0,012], então o challenger M2 não foi testado (regra);
   - **teste, avaliado uma vez**: M1 AP 0,231 [0,190–0,293] contra B1 0,302 [0,244–0,379]; diferença −0,070 [−0,115; −0,029]; resultado: **não supera**;
   - calibração: 8,1% previsto contra 13,2% observado; maior erro por decil 18,5 p.p.; resultado: **não exibir probabilidade**;
   - priorização com top 10%: B1 precisão 38,1% e MRR coberto 15,9%; M1 31,3% e 22,1%; B2 8,2% e 21,1%; antecedência mediana de 13 dias;
   - modelo final ajustado em treino + validação + teste e scores das 500 contas em 2024-12-31.
3. `solution/tests/test_model.py`: features sem campos proibidos; partição ordenada com purga; priorização num caso conhecido; regra de calibração; o modelo salvo reproduz os scores publicados.
4. `.gitignore`: `*.joblib` fora do Git, porque o script regenera o arquivo e um pickle num PR é risco para quem revisa.
5. `docs/model-card.md` escrito a partir de `docs/model-evaluation.md` (gerado).

## Verificações
- `pytest` → 38 passed.
- Conferi os números do model card contra `evaluation.csv`, `coefficients.csv` e `model_meta.json`.

## Erros reais e correções
1. **Model card com números não conferidos na primeira versão:** escrevi "43 features numéricas" (são 37) e o IC da ROC-AUC da logística no teste como [0,60–0,68] sem ter visto o valor (é [0,59–0,69]). Corrigi depois da conferência e acrescentei os ICs que faltavam a partir do `evaluation.csv`.
2. Pré-visualização do staging rodada de dentro da subpasta não listou `model_meta.json`; refeita pela raiz (como faz o `stage.sh`), saiu correta. Não afetou o commit.

## Decisões
- Do candidato: opção (a) (DEC-020).
- Do Claude Code, revisão pendente: H = 30 (DEC-021).
- Pela regra pré-registrada: o painel usa o ranking por tempo de casa e não exibe probabilidade (DEC-022).
- **Para a DAV-193:** "pegar mais contas" (tempo de casa) ou "proteger mais receita" (MRR) é escolha de negócio. Como o teste já foi consumido, uma regra nova (risco × valor) só pode ser comparada na validação.

## Tempo
Não cronometrado. Timestamps observados (-03:00): DAV-189 iniciada 19:24:57; pré-registro 19:25; modelo rodado ~19:27.

## Commit
SHA no comentário de fechamento da DAV-189.
