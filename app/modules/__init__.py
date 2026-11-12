"""Punto central de registro; C-02 agregará entidades en estos módulos."""


def register_models() -> None:
    """Importar todos los modelos antes de consultar SQLModel.metadata."""
    from app.modules.autores import models as autores
    from app.modules.clientes import models as clientes
    from app.modules.editoriales import models as editoriales
    from app.modules.generos import models as generos
    from app.modules.health import models as health
    from app.modules.libros import models as libros
    from app.modules.ventas import models as ventas
