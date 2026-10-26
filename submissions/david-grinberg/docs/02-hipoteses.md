# Hipóteses — versão pré-análise
Registradas em 26/10/2026, antes de adquirir ou examinar os CSVs nesta organização. Todas têm status NÃO TESTADA. Origem U = usuário; P = proposta de ampliação no planejamento com ChatGPT, ainda sujeita à revisão do candidato.

## Registro
| ID / origem | Hipótese | Teste planejado | Atenção |
|---|---|---|---|
| H01 / U | Queda de uso antecede churn e permite alerta ao CS. | Janelas candidatas de 7/14/30 dias versus período anterior equivalente; frequência, volume, amplitude e recência de uso; estimar antecedência e dose-resposta; comparar futuros churners com elegíveis retidos. | Janelas propostas, sem limiar definido. Ausência de linha não é automaticamente zero; excluir pós-churn; comparar tempo de vida e sazonalidade; avaliar falsos alertas. |
| H02 / U | Experiências de suporte se associam ao churn posterior. | Tickets pré-corte, resolução, resposta, recorrência e escalação; normalizar por exposição e comparar coortes semelhantes; separar clientes sem ticket. | Satisfação apenas entre respondentes; data de resposta/resolução pode ser posterior ao corte; maior uso também gera mais tickets. |
| H03 / U | Problemas técnicos se associam a maior risco. | Taxa de erros por oportunidades/uso, persistência e features afetadas antes do corte; cruzar com suporte e churn. | Contagem de erro e taxa são diferentes; verificar denominador e disponibilidade temporal; não inferir causa por importância de feature. |
| H04 / U | Perfis diferem na realização de valor e retenção. | Indústria, plano, canal, trial, porte se existir e tenure; proxies de adoção/profundidade/recorrência e churn, MRR e renovação. | “Valor percebido” não é observado diretamente por uso/receita; sinalizar proxies; feedback pós-churn serve ao diagnóstico, não à previsão. |
| H05 / P | Crescimento do uso agregado esconde deterioração de coortes. | Uso total versus por conta ativa e coorte, concentração, clientes novos/antigos, clientes retidos/perdidos. | Mudança de composição pode explicar a aparente contradição do brief. |
| H06 / P | Plano, cobrança e renovação alteram exposição ao churn. | Mensal/anual, proximidade de renovação, mudanças de plano, tenure; separar quantidade de contas e receita perdida. | Plano final e end_date podem conter futuro; mensal/anual exigem denominadores e exposição coerentes. |
| H07 / P | Fraca ativação no início é sinal de risco posterior. | Adoção inicial e diversidade de features em janela fixa; comparar com resultados posteriores e H01. | Separar clientes novos sem histórico; não classificar pouco histórico como desengajamento. |
| H08 / P | Reativação e múltiplos eventos distorcem uma leitura simples do churn. | Reconciliar churn_flag, churn_events, estado das assinaturas e reativações por data e grão. | Eventos não equivalem a contas; churn de assinatura não implica necessariamente churn da conta. |
| H09 / P | Alguns motivos registrados não se sustentam no comportamento. | Contrastar reason code/feedback com uso, erros, suporte e receita anteriores ao evento; codificação de texto rastreável. | Motivo declarado não é prova causal; texto pós-evento é proibido como feature de previsão. |

## Registro inicial e descoberta
Este é o registro inicial deste fluxo, não uma alegação de pesquisa cega: se já houve exploração ou uso de IA sobre estes dados antes desta etapa, declarar essa atividade e sua influência nas hipóteses. Não reconstruir evidências inexistentes.
Fixar a versão inicial no primeiro commit do fork. Novas hipóteses recebem H10+ e data; marcar como exploratórias quando surgirem ao olhar os dados. Não reescrever retrospectivamente a hipótese para parecer previsão acertada.
Classificações finais: apoiada, refutada, inconclusiva ou não testável. Associação não prova causalidade.
Registrar n, denominador, período, magnitude, incerteza e limitações; priorizar tamanho de efeito e utilidade de decisão. Tratar exploração múltipla e grupos pequenos com cautela.

## Contrato temporal a decidir em M1
- Unidade candidata: conta elegível em uma data de corte t. Verificar se churn deve ser da conta ou da assinatura.
- Alvo candidato: primeiro churn relevante em (t, t+H], H inicial a avaliar = 30 dias; justificar e versionar H antes do treino.
- Features: apenas eventos e atributos comprovadamente conhecidos até t.
- Histórico: janela de observação e critério mínimo de dados. Sem acompanhamento completo até t+H, não rotular “não churn”; tratar censura.
- Churners anteriores, reativações, trial e múltiplas assinaturas exigem política explícita.
- Validar coerência entre churn_flag e eventos; não usar flag atual como target futuro sem comprovação temporal.
- Coortes comparáveis: mesma elegibilidade e acompanhamento, evitando comparar toda vida de churners com período parcial de retidos.

## Teste do limiar de queda
Definir queda relativa apenas com base anterior positiva e exposição comparável; documentar base zero, clientes novos, dados ausentes e queda absoluta.
Explorar faixas na parte de desenvolvimento. Escolher corte por validação + capacidade CS, sem otimizar no teste final.
Reportar precision@K, recall@K, falsos alertas, antecedência do sinal e MRR coberto para políticas candidatas. Não prometer um “percentual mágico” universal.

## Previsão e inferência causal
Churn_events e feedback podem informar diagnóstico retrospectivo. Features para inferência não podem conter churn_flag, motivo, refund, feedback de saída, status final, cancelamento ou end_date que só ficaram conhecidos depois de t.
Split temporal com janelas de labels sem sobreposição indevida entre treino, validação e teste; purgar fronteiras quando necessário. Preprocessamento ajustado só no treino. Não usar account_id como preditor.
Se várias linhas por conta, controlar dependência nas métricas/incerteza e reportar desempenho em novas contas quando pertinente.
Predição indica risco, não efeito de uma intervenção. Uplift e retenção incremental exigem validação posterior, por exemplo teste controlado.

## Gate de honestidade
Se datas, labels ou cobertura forem insuficientes, marcar limitação, rever alvo e decidir escopo. Não camuflar classificação retrospectiva como previsão operacional. Evidências de dados sintéticos, se confirmadas na fonte, limitam generalização para produção.


## Revisão do candidato — 2026-10-26 (sessão S-002, DAV-178)
Registrada antes de qualquer leitura do conteúdo dos CSVs neste fluxo. O texto das hipóteses acima é o do kit S-001, fixado sem alteração no commit 930e594.
- Decisão do candidato: H01–H09 aprovadas como registro pré-análise. Todas permanecem NÃO TESTADAS. Origem mantida: H01–H04 = U (pedido original do candidato); H05–H09 = P (propostas do ChatGPT no planejamento, agora aceitas pelo candidato).
- Exploração anterior declarada pelo candidato: antes deste fluxo, abriu/olhou os CSVs e usou IA sobre os dados. Quando, com qual ferramenta e o que foi observado não foram detalhados (pendente). Portanto, este não é um registro cego e as hipóteses podem ter sido influenciadas por essa exploração. Ver DEC-008.
- Neste fluxo, até a revisão, os dados foram só baixados e conferidos por tamanho e SHA-256; nenhum valor foi lido.

Documento no Linear: https://linear.app/david-grinberg/document/02-hipoteses-pre-analise-e-protocolo-de-validacao-7e2fa1da7520
