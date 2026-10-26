#!/bin/sh
# Prepara (git add) as mudanças desta submissão para commit.
# O .gitignore raiz do repositório oficial ignora submissions/, então arquivos
# novos só entram com `git add -f`. Este script aplica antes o .gitignore desta
# pasta, para não forçar .venv/ nem dados locais, e falha se houver algo
# preparado fora da pasta. Não faz commit.
set -eu

SUB_ABS=$(cd "$(dirname "$0")/.." && pwd -P)
ROOT=$(git -C "$SUB_ABS" rev-parse --show-toplevel)
SUB=${SUB_ABS#"$ROOT"/}
cd "$ROOT"

git ls-files -z --others --exclude-from="$SUB/.gitignore" -- "$SUB" | xargs -0 -r git add -f --
git add -u -- "$SUB"

outside=$(git diff --cached --name-only | grep -v "^$SUB/" || true)
if [ -n "$outside" ]; then
  printf 'ERRO: arquivos fora de %s estão preparados:\n%s\n' "$SUB" "$outside" >&2
  exit 1
fi
git diff --cached --name-status
