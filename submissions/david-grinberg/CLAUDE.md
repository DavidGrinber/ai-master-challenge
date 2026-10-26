# Instruções do case
Este arquivo pertence à pasta da submissão. Antes de agir, leia as regras oficiais do fork e docs/01-central-do-case.md, docs/02-hipoteses.md e docs/03-workflow-e-evidencias.md.
Se o Claude Code estiver aberto na raiz do fork e este arquivo não for carregado automaticamente, peça explicitamente para lê-lo no primeiro prompt.

## Escopo e primeira execução
- Inspecione fork, remote, branch e caminho real do candidato; não adivinhe identidade.
- Modifique apenas submissions/<slug-real>/, inclusive dependências e configurações.
- A primeira tarefa é DAV-178: somente setup. Não baixe dados, faça EDA, treine modelo ou construa painel nessa execução.
- Revise o registro de hipóteses com o candidato na DAV-179 antes de adquirir os CSVs.
- O planejamento e documentos iniciais foram feitos com ChatGPT; não os atribua ao Claude Code ou ao julgamento exclusivo do candidato.

## Processo
Execute uma issue por vez após verificar dependências e aceite. Salve prompt e saídas reais; registre ações, comandos, verificações, decisões, limites, tempo real e commit. Não invente exports, screenshots, erros, métricas, duração ou revisão humana.
Referencie issue, hipótese, experimento e evidência. Decisões do candidato só são finais após revisão real.
Um resumo verificável da decisão é suficiente; não peça nem exponha raciocínio interno privado.
Se não houver acesso ao Linear, produza o texto da atualização e mantenha o roadmap exportado coerente para atualização manual.

## Integridade analítica
Defina grão, target, horizonte, elegibilidade e datas em M1. Não use variáveis posteriores à data de decisão como preditores.
Mantenha observações retrospectivas separadas das features de previsão. churn_flag, reason code e status atual não são automaticamente labels temporais válidos.
Não multiplique eventos ao fazer joins. Diferencie uso ausente, zero uso e falta de histórico.
Treino/validação/teste temporais, janelas de labels auditadas e preprocessing ajustado no treino.
Selecione limiar na validação; não ajuste o teste final. Não chame score não calibrado de probabilidade.
Não trate correlação, importância de features ou motivo de cancelamento como prova causal.

## Entrega
Priorize o diagnóstico obrigatório e evidências. Diferenciais: modelo validado e MVP local de CS.
Não publique website, envie mensagens ou abra o PR durante setup. A tarefa final de PR só ocorre após validação e revisão da entrega.
README deve seguir o template oficial. Nunca altere arquivos fora da pasta do candidato para acomodar a aplicação.
