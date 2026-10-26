# Central do case — RavenStack / G4
Atualização: 26/10/2026. Fase: planejamento, sem dados analisados.
Projeto: https://linear.app/david-grinberg/project/g4-ravenstack-diagnostico-de-churn-e-cs-1a6781700e39

## Resultado esperado
Diagnóstico executivo que responda por que o churn ocorre, quais segmentos e contas merecem atenção e o que fazer com impacto estimado. Diferencial escolhido pelo candidato: painel interativo para CS apoiado por um modelo preditivo validado.

## Fonte oficial e congelamento do escopo
Repositório: https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge
Commit consultado: 4aed364d572fabe0f1fff1f0c6f32960b30fe575.
Arquivos lidos: README.md, CONTRIBUTING.md, submission-guide.md, templates/submission-template.md e challenges/data-001-churn/README.md.
Revalidar mudanças nas regras antes da submissão. As contagens de registros do brief são aproximadas, ainda não verificadas nos CSVs.

## Matriz de requisitos
| ID | Exigência / origem | Entrega e aceite |
|---|---|---|
| R01 | Explicar churn e investigar causa raiz / challenge | Relatório com mecanismos plausíveis, cruzamentos e alternativas; separar associação, precedência temporal e evidência causal. |
| R02 | Segmentos em risco e contas específicas / challenge | Taxas com denominadores, período, tamanho e incerteza; lista account_id elegíveis com score, motivos e limitações. |
| R03 | Ações concretas, priorizadas e impacto / challenge | Playbook com gatilho, responsável sugerido, ação, prazo operacional, indicador e cenários de impacto. |
| R04 | Cruzar 5 tabelas / qualidade | Mapa de relações, agregação correta por grão e rastreabilidade de cada conclusão; não juntar eventos de uso e tickets brutos e multiplicar valores. |
| R05 | Insights verificáveis / qualidade | Números reproduzíveis e fonte, consulta/script e versão dos dados para cada finding. |
| R06 | Leitura pelo CEO / qualidade | Resumo executivo curto, recomendações priorizadas e limites claros. |
| R07 | Evidências do processo / regras gerais | Prompts e saídas reais, verificações, decisões do candidato, erros observados e correções, iterações e commits. Sem process log a regra prevê desclassificação. |
| R08 | Submissão por PR / CONTRIBUTING | Fork, branch submission/<slug-do-candidato>, tudo em submissions/<slug-do-candidato>/; nenhum diff fora da pasta. README segue template oficial; título [Submission] Nome — Challenge 001. |
| D01 | Modelo funcional / diferencial escolhido | Referências + validação temporal, auditoria de vazamento, métricas fora do treino, pipeline de inferência e model card. |
| D02 | Painel para CS / diferencial escolhido | Fila priorizada, filtros, ficha de conta, histórico disponível, sinais de risco, recomendação, exportação e instruções de uso. |

## Cinco fontes esperadas — a verificar
- ravenstack_accounts.csv: perfil e aquisição; account_id.
- ravenstack_subscriptions.csv: histórico de assinaturas/receita; subscription_id e account_id.
- ravenstack_feature_usage.csv: uso e erros; subscription_id.
- ravenstack_support_tickets.csv: tickets e satisfação; account_id.
- ravenstack_churn_events.csv: eventos e motivos; account_id.
Fonte indicada pelo brief: https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset
Verificar procedência, licença e natureza dos dados na aquisição; não presumir que representem produção real.

## MVP escolhido
Stack sugerida, sujeita à auditoria: Python + pandas + scikit-learn + Streamlit local. Favorecer um pipeline pequeno e reproduzível.
Fluxo: snapshot de contas elegíveis → features anteriores à data de corte → modelo validado → fila CS → investigação e ação humana.
Sem CRM, mensagens automáticas, autenticação corporativa, retreinamento contínuo ou plataforma MLOps no MVP.
Publicação online é opcional; código e setup local são necessários.

## Gates e escopo de tempo
M0 25 min; M1 45; M2 65; M3 85; M4 85; M5 55. Total inicial 360 min. Orçamento é estimativa, não prazo confirmado.
Reservar o núcleo obrigatório antes de polimento. Se houver estouro, registrar decisão e estimativa de extensão; não esconder tempo adicional.
Não iniciar modelo antes de aprovar target e temporalidade. Não construir visuais com achados inventados.

## Decisões ainda abertas
Nome/slug e LinkedIn da submissão; deadline pessoal; acesso local ao fork e Kaggle; horizonte preditivo; disponibilidade de datas e labels; capacidade semanal de CS; limiar de risco/queda; algoritmo; viabilidade de score de probabilidade.
Nenhuma dessas lacunas impede organizar o projeto. Não inventar decisões ou contas reais.

## Aprovação de conclusões
Claude Code propõe e executa. O candidato decide o que aceita, rejeita ou altera e registra justificativa curta, evidência e consequência. Não atribuir ao candidato uma revisão que não ocorreu.


Documento no Linear: https://linear.app/david-grinberg/document/01-central-do-case-e-criterios-de-entrega-b0dc5ec98440
