# Contrato de dados
Estado em 2026-10-26: definido na DAV-181 (S-004) sobre a base limpa da DAV-201. O horizonte H e o split final são escolhidos na DAV-189.

## Premissas sobre os dados (decisão do candidato, DEC-015)
Adotadas porque os dados não resolvem estas ambiguidades e o responsável pelo case não foi consultado. Devem constar na entrega como premissas, não como fatos.

| ID | Premissa | Por que é necessária |
|---|---|---|
| P-01 | **Churn = evento em `churn_events`**, com data. `accounts.churn_flag` fica só como campo descritivo e é proibido como alvo ou preditor. | É a única fonte de churn com data e motivo. `churn_flag` contradiz os eventos em 312 de 500 contas, e nenhuma conta encerra todas as assinaturas (A-04, C-11). |
| P-02 | **MRR da conta em t = soma do `mrr_amount` das assinaturas ativas em t.** As 4 cópias exatas (S-03) contam como assinaturas legítimas (DEC-018, que revisa a versão inicial "sem duplicatas"). | 4.992 de 5.000 assinaturas se sobrepõem a outra da mesma conta (S-09). O valor absoluto é alto (US$ 10,16 milhões/mês no fim de 2024) e deve ser lido como artefato do dataset simulado. As cópias somam US$ 8.544 e só existem no corte de 2024-12-31. |
| P-03 | **Uso e tickets entram pela data do próprio evento**, mesmo quando ela cai fora do ciclo da conta ou da assinatura. | 52,8% do uso e 53,9% dos tickets são anteriores ao signup (U-05, T-03). Apagar essas linhas eliminaria metade dos dados; mover as datas inventaria dados. |

## Fontes e estrutura
- Arquivos: Kaggle `rivalytics/saas-subscription-and-churn-analytics-dataset`, versão 1 (21/07/2025), licença MIT, dados simulados, crédito a River @ Rivalytics. Hashes em `solution/data/manifest.json` (`raw_data.py verify`).
- Grão e chaves (DAV-201):
  - accounts: 1 linha por conta;
  - subscriptions: 1 linha por assinatura, várias e sobrepostas por conta;
  - feature_usage: 1 linha por evento, chave `usage_row_id`, ligado à conta via `subscription_id`;
  - support_tickets: 1 linha por ticket;
  - churn_events: 1 linha por evento, até 5 por conta.
- Qualidade e tratamento: `docs/data-quality-report.md` e `docs/data-treatment-log.md`. Leitura: `clean_data.load_clean()`.

## Unidade, população e datas (DEC-016; elegibilidade aprovada pelo candidato em DEC-017)
- **Unidade de previsão:** conta × data de corte t. As datas de corte são os fins de mês de 31/01/2023 a 31/12/2024 (24 cortes). Tudo o que é conhecido "em t" tem data ≤ t, considerando o dia t inteiro.
- **Elegível em t:** `signup_date` ≤ t e pelo menos uma assinatura com `start_date` ≤ t e `end_date` vazio ou > t. Parâmetro em `analytic_base.eligible_accounts`.
- **Rótulo:** `churn_next_{H}d` = algum evento de churn em (t, t+H], para H ∈ {30, 60, 90}. Fica **nulo** (censurado) quando t+H passa do fim dos dados (2024-12-31): o rótulo nunca é "não churn" sem acompanhamento completo.
- **Reativação e múltiplos eventos:** a conta continua elegível depois de um churn, porque segue com assinatura ativa, e pode churnar de novo. O histórico entra como `prior_churn_events` e `days_since_last_churn`. Usa-se `event_seq`, nunca `is_reactivation`, que é contraditório (C-05, C-06).
- **Trial:** contas e assinaturas em trial são elegíveis; `n_active_trial_subs` identifica esses casos.
- **Corte de pontuação:** 2024-12-31 (500 contas, sem rótulo) é a carteira atual que o modelo pontua para o painel.

## Features e disponibilidade temporal
Dicionário completo em `docs/analytic-base-dictionary.md`.

| Situação | Campos |
|---|---|
| Permitidos | atributos de cadastro (industry, country, referral_source, plan_tier inicial, tenure); assinaturas ativas, iniciadas ou encerradas até t; uso em janelas (t−30, t], (t−60, t−30] e (t−90, t]; tickets abertos até t; resolução, primeira resposta, escalonamento e satisfação **só de tickets fechados até t**; eventos de churn anteriores a t |
| Permitidos com restrição | `upgrade_flag` e `downgrade_flag` não têm data: só contam para assinaturas já encerradas até t |
| Proibidos como preditor | `accounts.churn_flag`; `accounts.is_trial` ("currently trialing": estado atual, não em t); `accounts.seats` (momento desconhecido); `reason_code`, `feedback_text`, `refund_amount_usd`, `preceding_*_flag` e `is_reactivation` de eventos; `end_date` ou status de assinaturas ainda ativas em t; `account_id` |
| Retrospectivos | `accounts_retrospective.csv` mistura o período inteiro, antes e depois do churn. Serve só para diagnóstico, nunca para alimentar o modelo |

- **Uso zero versus ausência:** contagens de janela sem eventos valem 0; `days_since_last_usage` fica nulo quando nunca houve uso até t. As 33 assinaturas sem nenhum uso (U-10) não equivalem a uso zero da conta, porque o uso é atribuído por conta.
- **Médias sem base** (resolução, satisfação) ficam nulas, não zero.

## Validação temporal (orientação para a DAV-189)
- O rótulo do corte t ocupa (t, t+H]. Um corte de treino só pode ser usado se t + H ≤ primeiro corte de validação, e o mesmo vale entre validação e teste (purga das fronteiras).
- Linhas da mesma conta em cortes diferentes são dependentes: reportar métricas com essa ressalva e, quando possível, em contas novas.
- **A prevalência cresce muito:** com H=30, de 1 positivo em 21 elegíveis (mar/2023) para 75 em 475 (nov/2024) (`label_counts.csv`). Comparar sempre com a prevalência do período avaliado e ajustar o limiar só na validação.

## Gate de viabilidade
- **Volume:** suficiente para um modelo simples. Com H=30 há 23 cortes rotulados e 4.754 linhas rotuladas, com 437 positivos; os positivos crescem ao longo do tempo (`outputs/analytic_base/label_counts.csv`).
- **Risco principal:** as datas de uso e tickets não seguem o ciclo da conta (P-03). Features de comportamento recente podem ser ruído. A DAV-189 deve comparar com um baseline simples e aceitar "não supera o baseline" como resultado válido.
- **Escopo preditivo:** a decisão do candidato fica pendente para a DAV-189.

## Reconciliação
`solution/outputs/analytic_base/reconciliation.csv`: 15 checagens, todas iguais às das tabelas limpas. Totais conferidos: contas, eventos, assinaturas, MRR ativo, linhas e contagens de uso, tickets; e, no corte final, uso, tickets e churn acumulados. Isso confirma que nada foi multiplicado nem perdido.

## Decisões e evidências
DEC-015 (premissas), DEC-016 (unidade, elegibilidade, rótulos, disponibilidade); sessões S-003 e S-004; testes em `solution/tests/test_analytic_base.py`, incluindo um teste de vazamento validado por mutação (S-004).
