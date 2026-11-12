"""PostgreSQL privado exclusivo de pytest; no opera servicios existentes."""
from dataclasses import dataclass, field
from pathlib import Path
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class PrivatePostgres:
    directory: Path
    token: str
    port: int
    password: str = field(repr=False)
    binaries: Path = field(default_factory=lambda: Path(os.environ.get("PG_BIN", r"C:\Program Files\PostgreSQL\17\bin")))
    running: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://foundation_test:{self.password}@127.0.0.1:{self.port}/libreria_test"

    def verify_owner(self) -> None:
        root = ROOT.resolve()
        temporary_root = root / "tmp"
        target = self.directory.resolve()
        data = self.directory / "data"
        paths = (temporary_root, self.directory, data, self.directory / "owner")
        if any(path.is_symlink() or path.is_junction() for path in paths):
            raise RuntimeError("Destino redirigido no permitido")
        if temporary_root.resolve() != temporary_root or data.resolve() != target / "data":
            raise RuntimeError("Destino redirigido no permitido")
        if target.parent != temporary_root or not target.name.startswith("pg-foundation-"):
            raise RuntimeError("Destino fuera del directorio permitido")
        if (target / "owner").read_text() != self.token:
            raise RuntimeError("El clúster no pertenece a esta ejecución")

    def run(self, name: str, *arguments: str, password: bool = False) -> str:
        self.verify_owner()
        environment = os.environ.copy()
        if password:
            environment["PGPASSWORD"] = self.password
        output = self.directory / f"command-{uuid.uuid4().hex}.tmp"
        try:
            with output.open("w+b") as stream:
                result = subprocess.run(
                    [str(self.binaries / name), *arguments], env=environment,
                    stdout=stream, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                    timeout=90,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                stream.seek(0)
                response = stream.read().decode("utf-8", errors="replace")
            if result.returncode:
                raise RuntimeError(f"Falló {name} en el clúster privado (sin mostrar secretos)")
            return response
        finally:
            try:
                output.unlink(missing_ok=True)
            except PermissionError:
                # PostgreSQL hereda el handle en Windows; se retira tras stop.
                pass

    def start(self) -> None:
        self.run("pg_ctl", "-D", str(self.directory / "data"), "-l", str(self.directory / "postgres.log"), "-w", "start")
        self.running = True

    def verify_process(self) -> None:
        self.verify_owner()
        lines = (self.directory / "data" / "postmaster.pid").read_text().splitlines()
        if Path(lines[1]).resolve() != (self.directory / "data").resolve() or int(lines[3]) != self.port or lines[5] != "127.0.0.1":
            raise RuntimeError("Proceso PostgreSQL ajeno al clúster privado")

    def stop(self) -> None:
        self.verify_owner()
        if self.running:
            self.verify_process()
            self.run("pg_ctl", "-D", str(self.directory / "data"), "-m", "fast", "-w", "stop")
            self.running = False

    def cleanup(self) -> None:
        self.verify_owner()
        if (self.directory / "data" / "postmaster.pid").exists() and not self.running:
            self.verify_process()
            result = subprocess.run(
                [str(self.binaries / "pg_ctl"), "-D", str(self.directory / "data"), "status"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if result.returncode == 0:
                self.running = True
            elif result.returncode == 3:
                (self.directory / "data" / "postmaster.pid").unlink()
            else:
                raise RuntimeError("No se pudo verificar el proceso privado")
        self.stop()
        if (self.directory / "data" / "postmaster.pid").exists():
            raise RuntimeError("El proceso privado sigue activo; se conserva el directorio")
        shutil.rmtree(self.directory)


def create_cluster() -> PrivatePostgres:
    temporary_root = ROOT.resolve() / "tmp"
    if temporary_root.is_symlink() or temporary_root.is_junction() or temporary_root.resolve() != temporary_root:
        raise RuntimeError("Directorio tmp redirigido no permitido")
    temporary_root.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="pg-foundation-", dir=temporary_root))
    token = uuid.uuid4().hex
    (directory / "owner").write_text(token)
    with socket.socket() as listener:
        try:
            listener.bind(("127.0.0.1", 5433))
        except OSError:
            listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    cluster = PrivatePostgres(directory, token, port, secrets.token_hex(24))
    password_file = directory / "password.tmp"
    try:
        password_file.write_text(cluster.password)
        cluster.run("initdb", "-D", str(directory / "data"), "-U", "foundation_test", "--auth=scram-sha-256", "--encoding=UTF8", "--locale=C", f"--pwfile={password_file}")
        password_file.unlink()
        with (directory / "data" / "postgresql.conf").open("a") as config:
            config.write(
                f"\nlisten_addresses = '127.0.0.1'\nport = {port}\n"
                "unix_socket_directories = ''\n"
            )
        cluster.start()
        cluster.run("createdb", "-h", "127.0.0.1", "-p", str(port), "-U", "foundation_test", "libreria_test", password=True)
        result = cluster.run("psql", "-h", "127.0.0.1", "-p", str(port), "-U", "foundation_test", "-d", "libreria_test", "-Atc", "SELECT current_database(), current_setting('server_version'), inet_server_addr(), inet_server_port()", password=True)
        database, version, address, connected_port = result.strip().split("|")
        assert database == "libreria_test"
        assert int(version.split(".")[0]) >= 17
        assert (address, connected_port) == ("127.0.0.1", str(port))
        print(f"PostgreSQL {version} privado: conexión SQL verificada")
        return cluster
    except BaseException:
        cluster.cleanup()
        raise
    finally:
        password_file.unlink(missing_ok=True)
