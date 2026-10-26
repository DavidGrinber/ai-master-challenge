# Contrato de dados — a preencher em M1
Estado: PENDENTE. Nenhum schema, taxa ou distribuição verificado. Só a aquisição foi feita (DAV-178).
- Arquivos, fontes, licença, versão, hashes: FEITO em 2026-10-26 (S-002). Kaggle rivalytics/saas-subscription-and-churn-analytics-dataset, versão 1 de 21/07/2025 ("Initial release"), licença MIT, dados simulados segundo a fonte. Seis arquivos (5 CSVs + README.md da fonte), com tamanho e SHA-256 em solution/data/manifest.json; conferência com `python solution/src/raw_data.py verify`. Contagens de registros do brief ainda não verificadas.
- Grão e chaves de cada tabela: FEITO (DAV-201). accounts = 1 linha por conta (`account_id`); subscriptions = 1 linha por assinatura (`subscription_id`, várias por conta, sobrepostas); feature_usage = 1 linha por evento de uso (`usage_id` não é único → `usage_row_id`), ligado à conta via `subscription_id`; support_tickets = 1 linha por ticket (`ticket_id`); churn_events = 1 linha por evento (`churn_event_id`, até 5 por conta).
- Cardinalidade, órfãos, duplicações e reconciliação: FEITO (DAV-201). Nenhum órfão; 4 assinaturas duplicadas; uso e tickets datados fora do ciclo da conta; churn contraditório entre fontes. Detalhes em docs/data-quality-report.md e docs/data-treatment-log.md. Base derivada: `load_clean()` em solution/src/clean_data.py.
- Definição de churn e reconciliação entre fontes:
- Unidade, população elegível, corte t e horizonte H:
- Janelas de observação, label e acompanhamento/censura:
- Política de múltiplas assinaturas, trial e reativação:
- Features, disponibilidade temporal e campos proibidos:
- Uso zero versus ausência de registro:
- Split temporal e controle de sobreposição:
- Gate de viabilidade da previsão:
- Decisões e evidências:
