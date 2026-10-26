# S-005 — Revisão do candidato: elegibilidade e tratamento dos dados
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issues: DAV-181 e DAV-201 (já Done; esta sessão registra a revisão e aplica a mudança decidida).
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompt do candidato (literal)
Resposta às três pendências do fechamento da DAV-181 (1: elegibilidade; 2: revisão dos tratamentos; 3: escopo e horizonte para a DAV-189):
> 1. ok
> 2. como reviso?
> 3: ok

## Ações
- Expliquei que só 3 das 14 decisões de tratamento exigiam julgamento (TR-04, TR-11, TR-12). As demais só marcam linhas, são técnicas ou já foram cobertas pelas premissas P-01 a P-03.
- Formulário de 4 perguntas. Respostas do candidato:
  - **TR-04 → "Tratar como legítimas"**, contra a minha recomendação de excluir da receita;
  - TR-11 → não imputar (recomendado);
  - TR-12 → aprovar o mapa (recomendado);
  - demais → aprovar em bloco (recomendado).
- Implementação da DEC-018:
  - `analytic_base.py`: retirado o filtro `q_is_duplicate` de `active_subscriptions`, das contagens de assinaturas e do perfil. A reconciliação do MRR passou a usar uma soma independente (assinaturas sem `end_date`), em vez de reutilizar `active_subscriptions`.
  - `clean_data.py`: textos de S-03 e U-08 atualizados (status "mantido"); C-10 deixou de excluir as cópias, sem efeito numérico, porque nenhuma cópia tem `end_date`.
  - Testes: `test_duplicate_subscription_never_counts_as_revenue` virou `test_exact_copies_count_as_legitimate_subscriptions` (A1: 3 assinaturas, MRR 500); a regressão nos dados reais passou a esperar 10.159.608.
- Documentação: P-02 no README, `docs/data-contract.md` e `CLAUDE.md`; TR-04 em `docs/data-treatment-log.md`; DEC-017 e DEC-018 no decision log, com o estado de DEC-014/015/016 atualizado.

## Resultado observado
- `clean_data.py` → originais intactos; `analytic_base.py` → snapshots 5.254 linhas (`c5db01421d8f…`), perfil 500 (`0adcf6d73a89…`); 15/15 reconciliações, com 5.000 assinaturas e MRR final de 10.159.608.
- Comparação de `label_counts.csv` com o commit `afa8cb0`: elegíveis e positivos idênticos em todos os cortes; o MRR muda só em 2024-12-31 (+8.544), porque as cópias começam em dezembro de 2024.

## Verificações
`pytest` → 20 passed. Pipeline completo de novo (verify → clean → base).

## Erros reais e correções
Nenhum nesta sessão.

## Decisões
- Do candidato: DEC-017 (elegibilidade aprovada; escopo e H para a DAV-189; tratamentos revisados) e DEC-018 (cópias exatas legítimas).

## Tempo
Não cronometrado. Início observado: 19:04:42 (-03:00).

## Commit
SHA no comentário da DAV-181.
