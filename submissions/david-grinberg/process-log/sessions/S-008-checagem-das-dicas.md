# S-008 — Checagem das dicas do challenge (complemento da DAV-184)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issue: complemento da [DAV-184](https://linear.app/david-grinberg/issue/DAV-184/03-investigar-churn-e-testar-hipoteses). Interrompeu o início da DAV-193.
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompt do candidato (literal)
Enviado enquanto a DAV-193 começava:
> voce analisou tudo que esta nas dicas no repositorio? realmente nada explica o churn?

## Resposta e ações
- **Resposta honesta: não.** A análise principal (EXP-001) era temporal. Ficaram cinco lacunas em relação às dicas do challenge:
  1. uso por `feature_name`;
  2. comparação direta entre churners e retidos no nível da conta;
  3. `churn_flag` testado como rótulo alternativo;
  4. uso por segmento;
  5. assinaturas, refund e MRR perdido por motivo.
- Explorações inline (19:37–19:40), registradas como **pós-hoc e exploratórias**, com correção de Bonferroni:
  - churners × retidos, 27 variáveis por definição: **0 significativas** com `churn_flag` (menor p = 0,059) e com eventos (menor p = 0,084);
  - 40 features: no máximo 2 com p < 0,05 por teste, o esperado ao acaso; nenhuma após a correção;
  - assinaturas encerradas × atributos: tudo com p ≥ 0,44;
  - refund e MRR por motivo: p = 0,79 e 0,32; `preceding_upgrade_flag` em contas com upgrade: 64% contra 61% da base;
  - uso por segmento: EdTech +19%, orgânico +11%, DevTools −14%, evento −13%, sem correspondência com diferenças de churn.
- Tudo virou `solution/src/explore_hints.py` → `docs/hints-checklist.md` (gerado) + `solution/outputs/diagnosis/hints_*.csv`. O script reproduziu os números da exploração inline.
- Em `docs/diagnosis-findings.md`, nova seção "As dicas do challenge, uma a uma". Conclusão mantida e reforçada.

## Verificações
Números citados conferidos contra o relatório gerado. `pytest` depois das mudanças: ver commit.

## Erros reais e correções
1. Na seção nova dos achados, escrevi "1 de 40 com p < 0,05", mas na adoção com `churn_flag` são 2 de 40. Corrigido para "no máximo 2 de 40 em cada teste (o esperado ao acaso)".

## Decisões
Nenhuma decisão nova. A pergunta do candidato expôs lacunas reais, e preenchê-las reforçou a conclusão da DAV-184.

## Tempo
Não cronometrado. Timestamps observados (-03:00): pergunta recebida ~19:37; exploração 19:37–19:40.

## Commit
SHA no comentário da DAV-184.
