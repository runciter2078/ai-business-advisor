"""
Configuración de la sesión de base de datos (async SQLAlchemy + aiosqlite).

Expone:
  - engine: instancia del motor async
  - AsyncSessionLocal: fábrica de sesiones
  - get_db: dependencia FastAPI para inyección de sesión
  - init_db: crea todas las tablas al arrancar
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.models import Base

# Garantizar que el directorio de datos existe antes de crear la BD
_db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
os.makedirs(os.path.dirname(os.path.abspath(_db_path)), exist_ok=True)

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Crea todas las tablas definidas en los modelos si no existen."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    Dependencia FastAPI. Proporciona una sesión async y garantiza su cierre.

    Uso:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
