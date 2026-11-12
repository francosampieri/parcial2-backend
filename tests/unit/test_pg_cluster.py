"""Protecciones de infraestructura: destinos redirigidos no se operan."""
import os
from pathlib import Path
import uuid

import pytest

from tests import pg_cluster


def junction(source: Path, target: Path) -> None:
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(source), str(target))
    else:
        target.symlink_to(source, target_is_directory=True)


def test_tmp_redirigido_rechazado_antes_de_crear(monkeypatch, tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    junction(external, root / "tmp")
    monkeypatch.setattr(pg_cluster, "ROOT", root)
    def forbidden(*args, **kwargs):
        pytest.fail("No debe crear ningún clúster dentro de tmp redirigido")
    monkeypatch.setattr(pg_cluster.tempfile, "mkdtemp", forbidden)
    try:
        with pytest.raises(RuntimeError, match="permitido|redirigido"):
            pg_cluster.create_cluster()
        assert list(external.iterdir()) == []
    finally:
        (root / "tmp").rmdir() if os.name == "nt" else (root / "tmp").unlink()


def test_pgdata_redirigido_rechazado_antes_de_operar(monkeypatch, tmp_path):
    root = tmp_path / "project"
    target = root / "tmp" / "pg-foundation-owned"
    target.mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    marker = uuid.uuid4().hex
    (target / "owner").write_text(marker)
    junction(external, target / "data")
    monkeypatch.setattr(pg_cluster, "ROOT", root)
    cluster = pg_cluster.PrivatePostgres(target, marker, 5433, "ficticia")
    try:
        with pytest.raises(RuntimeError, match="permitido|redirigido"):
            cluster.verify_owner()
        assert list(external.iterdir()) == []
    finally:
        (target / "data").rmdir() if os.name == "nt" else (target / "data").unlink()
