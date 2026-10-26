"""Aquisição e verificação dos arquivos originais do dataset (DAV-178).

Uso, a partir de submissions/david-grinberg/:
    python solution/src/raw_data.py verify                # presença, tamanho e SHA-256
    python solution/src/raw_data.py fetch                 # baixa do Kaggle e verifica
    python solution/src/raw_data.py fetch --archive X.zip # usa um zip já baixado

Só biblioteca padrão. Não lê o conteúdo dos CSVs; a análise começa na DAV-181.
Originais nunca são sobrescritos: um arquivo divergente em raw/ interrompe o fetch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
MANIFEST = DATA_DIR / "manifest.json"
RAW_DIR = DATA_DIR / "raw"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path = MANIFEST) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for spec in manifest["files"]:
        if Path(spec["name"]).name != spec["name"]:
            raise ValueError(f"nome com caminho no manifest: {spec['name']!r}")
    return manifest


def check(raw_dir: Path, files: list[dict]) -> list[str]:
    """Retorna um problema por arquivo divergente; lista vazia significa tudo confere."""
    problems = []
    for spec in files:
        path = raw_dir / spec["name"]
        if not path.is_file():
            problems.append(f"{spec['name']}: ausente")
        elif path.stat().st_size != spec["bytes"]:
            problems.append(f"{spec['name']}: {path.stat().st_size} bytes, esperado {spec['bytes']}")
        elif sha256(path) != spec["sha256"]:
            problems.append(f"{spec['name']}: SHA-256 diverge do manifest")
    return problems


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "ravenstack-case/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, dest.open("wb") as out:
        shutil.copyfileobj(response, out)


def fetch(raw_dir: Path, manifest: dict, archive: Path | None = None) -> list[str]:
    """Obtém o pacote, valida tudo numa área temporária e só então move para raw_dir.

    Retorna os nomes dos arquivos gravados (os que já existiam e conferem são mantidos).
    """
    files = manifest["files"]
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        if archive is None:
            archive = tmp_dir / "dataset.zip"
            download(manifest["dataset"]["download_url"], archive)
        staging = tmp_dir / "staging"
        staging.mkdir()
        with zipfile.ZipFile(archive) as zf:
            members = set(zf.namelist())
            missing = sorted({spec["name"] for spec in files} - members)
            if missing:
                raise SystemExit(f"pacote sem os arquivos esperados: {missing}")
            for spec in files:
                with zf.open(spec["name"]) as src, (staging / spec["name"]).open("wb") as dst:
                    shutil.copyfileobj(src, dst)
        problems = check(staging, files)
        if problems:
            raise SystemExit("pacote diverge do manifest:\n  " + "\n  ".join(problems))

        raw_dir.mkdir(parents=True, exist_ok=True)
        for spec in files:
            target = raw_dir / spec["name"]
            if target.exists() and check(raw_dir, [spec]):
                raise SystemExit(f"{target} já existe e diverge do manifest; nada foi sobrescrito")
        written = []
        for spec in files:
            target = raw_dir / spec["name"]
            if not target.exists():
                shutil.move(staging / spec["name"], target)
                target.chmod(0o444)
                written.append(spec["name"])
        return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify", help="confere raw/ contra o manifest")
    fetch_cmd = sub.add_parser("fetch", help="baixa o pacote do Kaggle e verifica")
    fetch_cmd.add_argument("--archive", type=Path, help="zip já baixado manualmente")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    if args.command == "fetch":
        written = fetch(RAW_DIR, manifest, args.archive)
        print(f"gravados: {', '.join(written) if written else 'nenhum (todos já presentes)'}")

    problems = check(RAW_DIR, manifest["files"])
    for spec in manifest["files"]:
        status = "ERRO" if any(p.startswith(spec["name"] + ":") for p in problems) else "ok"
        print(f"{status:4}  {spec['name']}  {spec['bytes']} bytes  {spec['sha256'][:12]}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"{len(manifest['files'])} arquivos conferem com {MANIFEST.name} em {RAW_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
