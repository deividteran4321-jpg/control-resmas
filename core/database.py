"""Capa de acceso a datos: motor de conexión y modelos ORM.

La URL de conexión se resuelve en este orden:
1. st.secrets["DATABASE_URL"]        (recomendado para despliegue en la nube)
2. variable de entorno DATABASE_URL  (recomendado para Docker/Render)
3. sqlite local en ./data/inventario.db (por defecto, solo para uso local)

Ver README.md para por qué SQLite local NO es apto para Streamlit Community
Cloud (almacenamiento efímero) y cómo apuntar a un Postgres gratuito.
"""
import os
from datetime import datetime

import streamlit as st
from sqlalchemy import Column, Integer, String, Date, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Gerencia(Base):
    __tablename__ = "gerencias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), unique=True, nullable=False)


class Ingreso(Base):
    __tablename__ = "ingresos"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    tipo_resma = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False)
    observacion = Column(String(255), default="")
    creado_en = Column(DateTime, default=datetime.utcnow)


class Entrega(Base):
    __tablename__ = "entregas"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    dia = Column(String(20), nullable=False)
    gerencia = Column(String(120), nullable=False)
    empleado = Column(String(120), nullable=False)
    tipo_resma = Column(String(30), nullable=False)
    cantidad = Column(Integer, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)


class Configuracion(Base):
    __tablename__ = "configuracion"
    clave = Column(String(60), primary_key=True)
    valor = Column(String(255))


DEFAULT_GERENCIAS = [
    "Administración",
    "Comercial",
    "Operaciones",
    "Logística",
    "Recursos Humanos",
    "Sistemas",
    "Finanzas",
    "Gerencia General",
]

DEFAULT_CONFIG = {
    "umbral_stock_bajo": "100",
}

TIPOS_RESMA = ["Carta", "Carta Ecológica", "Oficio"]


def _get_database_url() -> str:
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    return os.environ.get("DATABASE_URL", "sqlite:///data/inventario.db")


def _build_engine():
    url = _get_database_url()
    if url.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Crea las tablas si no existen y siembra datos base. Idempotente."""
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.query(Gerencia).count() == 0:
            session.add_all([Gerencia(nombre=n) for n in DEFAULT_GERENCIAS])
        for clave, valor in DEFAULT_CONFIG.items():
            if session.get(Configuracion, clave) is None:
                session.add(Configuracion(clave=clave, valor=valor))
        session.commit()
