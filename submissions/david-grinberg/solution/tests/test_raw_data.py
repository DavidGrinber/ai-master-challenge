import hashlib
import zipfile

import pytest

import raw_data

OFFICIAL_CSVS = {
    "ravenstack_accounts.csv",
    "ravenstack_subscriptions.csv",
    "ravenstack_feature_usage.csv",
    "ravenstack_support_tickets.csv",
    "ravenstack_churn_events.csv",
}


def spec_for(name: str, content: bytes) -> dict:
    return {"name": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


@pytest.fixture
def package(tmp_path):
    """Pacote falso com dois arquivos e o manifest correspondente."""
    contents = {"a.csv": b"id,x\n1,2\n", "b.csv": b"id,y\n3,4\n"}
    archive = tmp_path / "pkg.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for name, data in contents.items():
            zf.writestr(name, data)
    manifest = {"dataset": {"download_url": "unused"}, "files": [spec_for(n, d) for n, d in contents.items()]}
    return archive, manifest, contents


def test_real_manifest_lists_the_five_official_csvs():
    names = {spec["name"] for spec in raw_data.load_manifest()["files"]}
    assert OFFICIAL_CSVS <= names


def test_manifest_rejects_names_with_paths(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text('{"files": [{"name": "../x.csv", "bytes": 1, "sha256": "0"}]}')
    with pytest.raises(ValueError):
        raw_data.load_manifest(path)


def test_check_reports_missing_wrong_size_and_wrong_hash(tmp_path):
    good = b"abc"
    (tmp_path / "size.csv").write_bytes(b"abcd")
    (tmp_path / "hash.csv").write_bytes(b"xyz")
    (tmp_path / "ok.csv").write_bytes(good)
    files = [spec_for("missing.csv", good), spec_for("size.csv", good), spec_for("hash.csv", good), spec_for("ok.csv", good)]

    problems = raw_data.check(tmp_path, files)

    assert [p.split(":")[0] for p in problems] == ["missing.csv", "size.csv", "hash.csv"]


def test_fetch_from_archive_writes_verified_files(tmp_path, package):
    archive, manifest, contents = package
    raw = tmp_path / "raw"

    written = raw_data.fetch(raw, manifest, archive)

    assert sorted(written) == sorted(contents)
    assert raw_data.check(raw, manifest["files"]) == []
    assert all((raw / name).stat().st_mode & 0o222 == 0 for name in contents)


def test_fetch_keeps_matching_originals_and_is_idempotent(tmp_path, package):
    archive, manifest, _ = package
    raw = tmp_path / "raw"
    raw_data.fetch(raw, manifest, archive)

    assert raw_data.fetch(raw, manifest, archive) == []


def test_fetch_never_overwrites_a_divergent_original(tmp_path, package):
    archive, manifest, _ = package
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.csv").write_bytes(b"edited by hand\n")

    with pytest.raises(SystemExit):
        raw_data.fetch(raw, manifest, archive)

    assert (raw / "a.csv").read_bytes() == b"edited by hand\n"
    assert not (raw / "b.csv").exists()


def test_fetch_rejects_package_that_diverges_from_manifest(tmp_path, package):
    archive, manifest, _ = package
    manifest["files"][0]["sha256"] = "0" * 64
    raw = tmp_path / "raw"

    with pytest.raises(SystemExit):
        raw_data.fetch(raw, manifest, archive)

    assert not raw.exists()
