# S-004 — Premissas e base analítica (DAV-181)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issue: [DAV-181](https://linear.app/david-grinberg/issue/DAV-181/02-cruzar-tabelas-e-preparar-base-de-analise).
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).

## Prompts do candidato (literais)
1. > faz sentido tirar essas dúvidas com o responsável pelo case?
   >
   > • Há eventos de churn em 352 contas, mas 277 delas têm churn_flag=False. Além disso, todas as contas ainda apresentam assinatura ativa no fim da base.
   > • Muitas assinaturas se sobrepõem, o que deixa ambíguo o cálculo do MRR por conta.
   > • Aproximadamente metade dos registros de uso e suporte antecede a data de cadastro da conta.
2. > vamos seguir com as premissas e registramos elas na entrega
3. > segue

## Objetivo
Avaliar se valia consultar o responsável pelo case. Depois da decisão do candidato, fixar as premissas e construir a base analítica da DAV-181: perfil retrospectivo por conta e snapshots conta × data de corte, sem multiplicar números e sem vazamento temporal.

## Ações, comandos e saídas observadas

### Consulta ao responsável pelo case (avaliação, nada enviado)
- `gh issue list --repo Gestao-Quatro-Ponto-Zero/ai-master-challenge --state all` → 2 issues no total, ambas sem nenhum comentário. `has_discussions: false`.
- `gh search issues ... churn_flag` → 0 resultados.
- PRs do Challenge 001: 44; o mantenedor `joaovitor2763` (autor dos commits do repositório) fez 32 comentários ou reviews neles. Não li o conteúdo das submissões nem das reviews, para não contaminar a solução.
- Recomendação dada: seguir com premissas explícitas e, se quisesse, perguntar em paralelo; texto da issue rascunhado com números exatos. **Decisão do candidato: não perguntar, seguir com as premissas e registrá-las na entrega (DEC-015).**

### Base analítica
- `clean_data.py`: `dtype_label`, `to_csv_text` e o novo `read_typed` passaram a ser públicos, para reúso sem duplicar código. Testes seguiram passando (13).
- Criado `solution/src/analytic_base.py`. Execução → `snapshots` 5.254 linhas (`be5f439a83ac…`), `accounts_retrospective` 500 linhas (`6e61dcdaae08…`), 15/15 reconciliações ok, em 0,6 s.
- Reconciliação: 600 eventos, 4.996 assinaturas sem duplicatas, 25.000 linhas de uso, usage_count 250.525, error_count 14.107, 2.000 tickets. MRR ativo no fim = 10.151.064 = 10.159.608 (soma bruta da S-003) − 8.544 (as 4 duplicatas: 5.572 + 931 + 228 + 1.813).
- Recomputação independente, com código separado do script:
  - conta A-0aaf6e no corte 2024-06-30: 13 features, 0 divergências;
  - conta A-f19409 (eventos em 2023-03-26 e 2023-05-25): histórico de churn, dias desde o último churn, rótulos e censura no corte final conferem.
- `label_counts.csv` igual à tabela de viabilidade da S-003 nos cortes comuns (por exemplo, nov/2024: 475 elegíveis e 75 positivos; out/2024: 439, 48 e 97).

## Verificações
- `pytest` → 20 passed. Os 7 testes novos cobrem: elegibilidade; duplicata fora do MRR; rótulos olhando para frente e nulos quando censurados; features que ignoram tudo depois de t; janelas recente × anterior; reconciliação no fixture; reconciliação, determinismo e números de referência nos dados reais.
- **Mutação do teste de vazamento:** com `_until` e `_window` alterados para aceitar datas futuras (só no scratchpad), 3 testes falharam (rótulos, vazamento, janelas); sem a alteração, os 3 passaram.

## Erros reais e correções
1. Teste `test_windows_split_recent_and_previous_usage`: eu esperava `usage_count_prev_30d = 0`, mas a janela (t−60, t−30] para t = 2024-02-29 contém o uso de 2024-01-05, então o valor certo é 3. O erro estava no teste, não no código; corrigi a expectativa e comentei o cálculo.
2. `docs/data-contract.md`: escrevi "22 cortes rotulados" com H=30; conferido em `label_counts.csv`, são 23 (só o corte final fica sem rótulo). Corrigido.
3. Decision log: DEC-015/016 inseridas antes da DEC-014; as linhas DEC agora são ordenadas por número via script.

## Decisões
- Do candidato: premissas P-01 a P-03, sem consultar o responsável pelo case (DEC-015).
- Do Claude Code, revisão pendente: unidade, elegibilidade, rótulos e regras de disponibilidade (DEC-016).
- Em aberto para a DAV-189: escopo preditivo e horizonte H.

## Tempo
Não cronometrado. Timestamps observados (-03:00): DAV-181 retomada 17:50:56.

## Commit
SHA no comentário de fechamento da DAV-181.
