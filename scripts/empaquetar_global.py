"""Armar el ZIP de la evaluación global con la estructura pedida.

Uso:
    python scripts/empaquetar_global.py

Genera:
    dist/Parcial_Global_totones.zip
"""

from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
NAME = "Parcial_Global_totones"
STAGE = DIST / NAME
ZIP_PATH = DIST / f"{NAME}.zip"

BACKEND_DIRS = ("app", "tests", "test")
BACKEND_FILES = (
    "Dockerfile",
    ".dockerignore",
    "requirements.txt",
    "requirements-dev.txt",
    "env.example",
    "pytest.ini",
)
FRONTEND_DIRS = ("public",)
FRONTEND_FILES = (
    "Dockerfile",
    ".dockerignore",
    "default.conf.template",
    "env.example",
    "README.md",
)

FORBIDDEN_NAMES = {
    ".env",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "tmp",
}
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".log", ".sqlite", ".db")


def ignorar(directorio: str, nombres: list[str]) -> set[str]:
    """Excluir entornos, cachés, secretos y archivos temporales."""
    excluidos = set()
    for nombre in nombres:
        if nombre in FORBIDDEN_NAMES or nombre.endswith(FORBIDDEN_SUFFIXES):
            excluidos.add(nombre)
        elif nombre.startswith(".env") and nombre != ".env.example":
            excluidos.add(nombre)
    return excluidos


def copiar_arbol(origen: Path, destino: Path) -> None:
    if not origen.is_dir():
        raise SystemExit(f"Falta el directorio requerido: {origen}")
    shutil.copytree(origen, destino, ignore=ignorar)


def copiar_archivo(origen: Path, destino: Path) -> None:
    if not origen.is_file():
        raise SystemExit(f"Falta el archivo requerido: {origen}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origen, destino)


def preparar_escenario() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    for nombre in BACKEND_DIRS:
        copiar_arbol(ROOT / nombre, STAGE / "backend" / nombre)
    for nombre in BACKEND_FILES:
        copiar_archivo(ROOT / nombre, STAGE / "backend" / nombre)

    for nombre in FRONTEND_DIRS:
        copiar_arbol(ROOT / "frontend" / nombre, STAGE / "frontend" / nombre)
    for nombre in FRONTEND_FILES:
        copiar_archivo(ROOT / "frontend" / nombre, STAGE / "frontend" / nombre)

    copiar_archivo(ROOT / "docs" / "global" / "README.md", STAGE / "README.md")
    copiar_archivo(ROOT / "docs" / "global" / "DEPLOY.md", STAGE / "DEPLOY.md")

    evidencia_destino = STAGE / "evidencia"
    evidencia_destino.mkdir()
    for archivo in sorted((ROOT / "docs" / "evidencia").glob("*.md")):
        copiar_archivo(archivo, evidencia_destino / archivo.name)


def verificar_escenario() -> None:
    requeridos = (
        STAGE / "frontend" / "Dockerfile",
        STAGE / "frontend" / "default.conf.template",
        STAGE / "frontend" / "env.example",
        STAGE / "backend" / "Dockerfile",
        STAGE / "backend" / "env.example",
        STAGE / "README.md",
        STAGE / "DEPLOY.md",
        STAGE / "evidencia" / "G-global.md",
    )
    faltantes = [str(ruta.relative_to(STAGE)) for ruta in requeridos if not ruta.is_file()]
    if faltantes:
        raise SystemExit("Faltan archivos en el paquete: " + ", ".join(faltantes))

    for ruta in STAGE.rglob("*"):
        partes = set(ruta.parts)
        if partes & FORBIDDEN_NAMES:
            raise SystemExit(f"Archivo prohibido en el paquete: {ruta}")
        if ruta.name.startswith(".env") and ruta.name != ".env.example":
            raise SystemExit(f"Archivo de entorno privado en el paquete: {ruta}")


def crear_zip() -> None:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archivo:
        for ruta in sorted(STAGE.rglob("*")):
            if ruta.is_file():
                archivo.write(ruta, arcname=str(Path(NAME) / ruta.relative_to(STAGE)))


def verificar_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH) as archivo:
        nombres = archivo.namelist()
    for nombre in nombres:
        partes = set(Path(nombre).parts)
        if partes & FORBIDDEN_NAMES:
            raise SystemExit(f"Archivo prohibido dentro del ZIP: {nombre}")
        if Path(nombre).name.startswith(".env") and Path(nombre).name != ".env.example":
            raise SystemExit(f"Archivo privado dentro del ZIP: {nombre}")
    if not any(nombre.endswith("frontend/Dockerfile") for nombre in nombres):
        raise SystemExit("El ZIP no contiene frontend/Dockerfile")
    if not any(nombre.endswith("backend/Dockerfile") for nombre in nombres):
        raise SystemExit("El ZIP no contiene backend/Dockerfile")


def main() -> None:
    preparar_escenario()
    verificar_escenario()
    crear_zip()
    verificar_zip()

    with zipfile.ZipFile(ZIP_PATH) as archivo:
        cantidad = len(archivo.namelist())
    tamano = ZIP_PATH.stat().st_size
    print(f"Paquete: {ZIP_PATH.relative_to(ROOT)}")
    print(f"Archivos: {cantidad}")
    print(f"Tamaño: {tamano / 1024:.1f} KiB")
    print("Estructura: frontend/, backend/, README.md, DEPLOY.md, evidencia/")


if __name__ == "__main__":
    main()
