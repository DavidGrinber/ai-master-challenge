# S-002 — Harness, fork e aquisição verificada dos dados (DAV-178)
Data/fuso: 2026-10-26, America/Sao_Paulo (-03:00).
Issue: https://linear.app/david-grinberg/issue/DAV-178/01-preparar-case-ambiente-e-arquivos-csv
Ferramenta/modelo: Claude Code, modelo claude-opus-5-5 (identificador informado pelo ambiente da sessão).
Prompt real: [S-002-prompt-usuario.md](S-002-prompt-usuario.md).

## Objetivo
Preparar fork, clone, remotes e branch; revisar as hipóteses com o candidato; adquirir e inventariar os CSVs; montar o harness (CLAUDE.md, README, ambiente, testes, registro). Parar antes de qualquer análise.

## Insumos e versões
- Repositório oficial: commit 4aed364d572fabe0f1fff1f0c6f32960b30fe575. Lidos README.md, CONTRIBUTING.md, submission-guide.md, templates/submission-template.md e challenges/data-001-churn/README.md (mais challenges/README.md).
- Linear, lido via integração: projeto P-DAV-4; documentos 01, 02 e 03; issues ativas DAV-178, 181, 184, 189, 193, 194, 198 e 199; DAV-177 (Done, histórico). Sem comentários em DAV-177/178. Canceled/Duplicate ignoradas.
- Kit do ChatGPT: `~/Downloads/G4_Churn_Kit_Inicial.zip` (sha256 c8c18e5df6acd24094cdcf21b599044f3a4719b2660781c107e45ef6a23ce5fd) e a pasta extraída `~/Downloads/g4-churn-starter`.

## Ações, comandos e saídas observadas

### Ambiente encontrado
- Pasta `~/Documents/Case` vazia; nenhum repositório local.
- `git 2.50.1`; `gh`: não instalado; `python3`: 3.9.6, do sistema e fora de suporte; `uv`: não instalado; Homebrew ausente.
- `ssh -T git@github.com` → `Hi DavidGrinber! You've successfully authenticated`. API pública: login DavidGrinber, id 152665223, sem nome nem e-mail públicos. `GET /repos/DavidGrinber/ai-master-challenge` → 404, ou seja, o fork ainda não existia.

### Documentos e kit
- `git clone git@github.com:Gestao-Quatro-Ponto-Zero/ai-master-challenge.git` em `~/Documents/Case/ai-master-challenge`. Observado: o `.gitignore` raiz ignora `submissions/`.
- `diff -r` entre a pasta extraída e o zip: idênticos, exceto `.DS_Store`. `cmp` de `docs/references/*` do kit contra o clone: os 5 arquivos são idênticos.
- O S-001 menciona "único time Sparring"; hoje o projeto aparece no time "David" (DAV). Não investigado.

### Ferramentas
- `gh` 2.102.0 (30/09) e `uv` 0.13.0 (09/10): versões com mais de duas semanas, baixadas dos releases oficiais. `shasum -a 256 -c` contra os checksums publicados: `OK` nos dois. Instalados em `~/.local/bin`.
- `uv python install 3.12` → `Installed Python 3.12.15`.

### Autenticação e GitHub
- `gh auth login --hostname github.com --git-protocol ssh --web --skip-ssh-key --scopes repo`, rodando em segundo plano; o código de dispositivo foi enviado ao candidato.
  - 1ª tentativa: `failed to authenticate via web browser: context deadline exceeded`. O código expirou antes de a autorização chegar.
  - 2ª tentativa: `✓ Authentication complete` / `✓ Logged in as DavidGrinber`. `gh auth status`: escopos `gist`, `read:org`, `repo`; token no keyring do macOS (não registrado aqui).
- `gh repo list DavidGrinber --fork` → `[]`. `gh repo fork Gestao-Quatro-Ponto-Zero/ai-master-challenge --clone=false --default-branch-only` → https://github.com/DavidGrinber/ai-master-challenge (`isFork: true`, parent oficial, default `main`).
- No clone: `git remote rename origin upstream`; `git remote add origin git@github.com:DavidGrinber/ai-master-challenge.git`; `git remote set-url --push upstream no_push_to_official_repo`. `git rev-parse origin/main upstream/main` → ambos `4aed364d…`.
- Identidade local (só neste repositório): `David Grinberg <152665223+DavidGrinber@users.noreply.github.com>`. O nome vem do perfil do Linear, porque o GitHub não tem nome público; o e-mail é o noreply derivado do id da conta autenticada.
- `git ls-remote --heads origin 'submission/*'` → vazio. `git switch -c submission/david-grinberg`.
- Slug `david-grinberg`, derivado do nome "David Grinberg" do perfil no Linear. Sem ambiguidade, então não foi pedida confirmação.

### Commit 1 — kit sem alteração
- `rsync -a --exclude .DS_Store <zip extraído>/submission/ submissions/david-grinberg/` + `diff -r` → idêntico. `INICIAR-AQUI.md` ficou de fora, como o próprio kit instrui.
- `git add -f -- submissions/david-grinberg`; nada fora da pasta. Commit `930e594` às 16:50:35. Fixa o texto pré-análise das hipóteses antes da aquisição.

### Revisão das hipóteses (antes de ler qualquer dado)
- Pergunta ao candidato → **aprovou H01–H09**, mantendo a origem U/P (DEC-007).
- Exploração anterior → o candidato declarou que **abriu/olhou os CSVs e usou IA sobre os dados** antes deste fluxo; detalhes não informados (DEC-008).

### Dados
- `GET https://www.kaggle.com/api/v1/datasets/view/rivalytics/saas-subscription-and-churn-analytics-dataset` → HTTP 200: `currentVersionNumber 1`, versão criada em `2025-07-21T23:53:44.247Z` ("Initial release"), `licenseName MIT`, `totalBytes 2073150`, subtítulo "Simulated data for SaaS user behavior analysis"; a descrição diz "simulated dataset was created using Python and ChatGPT".
- `curl -L .../api/v1/datasets/download/...` sem autenticação → HTTP 200, 600149 bytes, zip sha256 `ce6afd8d…15c0`. `unzip -l`: 6 membros sem caminho (README.md + 5 CSVs), totalizando 2073150 bytes, igual a `totalBytes`.
- Extração em pasta isolada; `file` → `CSV text` nos 5 CSVs. Tamanho e SHA-256 registrados em `solution/data/manifest.json`.
- Nenhum valor dos CSVs nem o README da fonte foram lidos nesta sessão. Contagens de registros não verificadas (fica para a DAV-181).

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| ravenstack_accounts.csv | 36649 | 348d8ba906b7776894b5236b2e7aa91a503d41670dbc9aad30c37b503c9abef5 |
| ravenstack_subscriptions.csv | 437566 | dcf1d93ca9a35e0dcba0ab686d255f0e9ec26512970bbf0944cf19cbef2d751a |
| ravenstack_feature_usage.csv | 1400898 | c081da2be8caf987d07f0f79ceb0619aba523d819529230ed6df77984fa21d4e |
| ravenstack_support_tickets.csv | 145598 | ba0006951479771ee9f93c98789c96bc5fec892cf11f867afb28194f0b76d220 |
| ravenstack_churn_events.csv | 44630 | 6391c41d8291b7b4845ec9a84d3837c2ed230a33a32a854ec33d4e66dc150940 |
| README.md (da fonte) | 7809 | ce1293cf6e484eda1c86b8f95bf9d3760ccb633f39327271a1925fe4eafbc0d0 |

### Ambiente Python
- `uv pip compile requirements.in --universal --python-version 3.12 --exclude-newer 2026-10-12 -o requirements.txt` → pandas 3.0.6, numpy 2.5.4, scikit-learn 1.9.1, scipy 1.18.1, streamlit 1.65.0, pytest 9.1.1 (127 linhas).
- `uv venv .venv --python 3.12` + `uv pip install -r requirements.txt`; import → `3.12.15 pandas 3.0.6 sklearn 1.9.1 streamlit 1.65.0 pytest 9.1.1 numpy 2.5.4`; `streamlit --version` → `1.65.0`.
- Caminho sem uv: `python3.12 -m venv` (pip 25.0.1) + `pip install --quiet --dry-run -r requirements.txt` → exit 0.

### Harness
- Criados: `solution/src/raw_data.py` (fetch/verify, só biblioteca padrão), `solution/tests/test_raw_data.py`, `pytest.ini`, `scripts/stage.sh`, `requirements.in`, `requirements.txt`, `.python-version`, `solution/data/manifest.json`, este registro e o prompt literal.
- Reescritos: `CLAUDE.md` (instruções vigentes), `README.md` (template oficial, pendências e "Como reproduzir"), `.gitignore` (padrões `**/` para funcionar com `--exclude-from`), `solution/README.md`, `process-log/README.md`.
- Atualizados: `docs/02-hipoteses.md` (seção de revisão), `docs/decision-log.md` (DEC-007 a DEC-011), `docs/data-contract.md` (aquisição), `docs/references/SOURCE.md` (reconferência), notas de snapshot em `docs/01`, `03`, `04` e `roadmap-linear.md`.
- Removido: `solution/src/.gitkeep`, porque a pasta passou a ter conteúdo.
- `.env.example` não foi criado: nenhuma variável é necessária, já que o download é público.

## Verificações
- `.venv/bin/python -m pytest` → `7 passed`: manifest com os 5 CSVs; rejeição de nomes com caminho; ausente/tamanho/hash; fetch grava arquivos verificados em modo somente leitura; idempotência; não sobrescreve original divergente; rejeita pacote divergente sem tocar em `raw/`.
- `raw_data.py fetch` (2º download, independente) → 6 arquivos gravados; `cmp` com o 1º download → todos iguais; `raw_data.py verify` → `ok` em 6/6, exit 0; novo `fetch` → `gravados: nenhum (todos já presentes)`.
- `git ls-files --others --exclude-from=.gitignore` antes do staging: lista só código e documentos; nenhum `.venv/`, CSV, README da fonte ou cache.

## Erros reais e correções
1. Autenticação do `gh`: o primeiro código de dispositivo expirou (`context deadline exceeded`). Gerei um novo código e enviei a pergunta logo em seguida; a autenticação concluiu.
2. Comando meu: `ls solution/data/raw/ -a && ... fetch`. O `ls` do macOS rejeita opção depois do caminho, então o `&&` impediu o fetch. O `verify` seguinte reportou os 6 arquivos ausentes com exit 1, o comportamento esperado. Repeti a sequência sem o `ls` e ela foi verificada (acima).

## Decisões
- Do candidato: autenticação realizada; H01–H09 aprovadas (DEC-007); exploração anterior declarada (DEC-008).
- Do Claude Code, revisão do candidato pendente: stack e lock (DEC-009); manter os dados fora do Git com manifest + script (DEC-010); fork, remotes, identidade e staging (DEC-011).

## Pendências
- Detalhar a exploração anterior: quando, qual IA, o que foi visto e a influência nas hipóteses (DEC-008).
- LinkedIn no README.
- Export desta conversa: não feito. A transcrição bruta da sessão inclui saídas locais sem relação com o case; decidir na DAV-199 o que exportar.
- O documento 02 no Linear ainda não registra a revisão; ela está neste repositório e no comentário da DAV-178.

## Tempo
Não cronometrado. Timestamps observados (-03:00): clone 16:28; commit 930e594 16:50:35; download 16:50; fetch pelo script 16:54.

## Commit
- 930e594: import do kit.
- Harness: SHA e verificação do push na seção "Fechamento", acrescentada no commit seguinte.
