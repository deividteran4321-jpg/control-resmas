"""Lógica de negocio: todas las consultas y escrituras pasan por aquí.

Las páginas de Streamlit solo deberían importar funciones de este módulo,
nunca tocar los modelos ORM directamente.
"""
from datetime import date
from typing import Iterable, Optional

import pandas as pd
from sqlalchemy import func, select

from core.database import (
    TIPOS_RESMA,
    Configuracion,
    Entrega,
    Gerencia,
    Ingreso,
    SessionLocal,
    engine,
)

DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def dia_semana(fecha: date) -> str:
    return DIAS_ES[fecha.weekday()]


# --- Gerencias -------------------------------------------------------------

def get_gerencias() -> list[str]:
    with SessionLocal() as s:
        filas = s.query(Gerencia).order_by(Gerencia.nombre).all()
        return [g.nombre for g in filas]


def add_gerencia(nombre: str) -> None:
    nombre = nombre.strip()
    if not nombre:
        return
    with SessionLocal() as s:
        existe = s.query(Gerencia).filter(Gerencia.nombre.ilike(nombre)).first()
        if not existe:
            s.add(Gerencia(nombre=nombre))
            s.commit()


def eliminar_gerencia(nombre: str) -> bool:
    """Devuelve False si la gerencia tiene entregas asociadas (no se borra)."""
    with SessionLocal() as s:
        en_uso = s.query(Entrega).filter(Entrega.gerencia == nombre).count()
        if en_uso:
            return False
        g = s.query(Gerencia).filter(Gerencia.nombre == nombre).first()
        if g:
            s.delete(g)
            s.commit()
        return True


def get_empleados_conocidos() -> list[str]:
    with SessionLocal() as s:
        filas = s.query(Entrega.empleado).distinct().order_by(Entrega.empleado).all()
        return [r[0] for r in filas]


# --- Configuración -----------------------------------------------------------

def get_umbral_stock_bajo() -> int:
    with SessionLocal() as s:
        c = s.get(Configuracion, "umbral_stock_bajo")
        return int(c.valor) if c else 100


def set_umbral_stock_bajo(valor: int) -> None:
    with SessionLocal() as s:
        c = s.get(Configuracion, "umbral_stock_bajo")
        if c:
            c.valor = str(valor)
        else:
            s.add(Configuracion(clave="umbral_stock_bajo", valor=str(valor)))
        s.commit()


# --- Stock -------------------------------------------------------------------

def registrar_ingreso(
    fecha: date, tipo_resma: str, cantidad: int, observacion: str = ""
) -> None:
    with SessionLocal() as s:
        s.add(
            Ingreso(
                fecha=fecha,
                tipo_resma=tipo_resma,
                cantidad=cantidad,
                observacion=observacion,
            )
        )
        s.commit()


def get_total_ingresos() -> int:
    with SessionLocal() as s:
        return s.query(func.coalesce(func.sum(Ingreso.cantidad), 0)).scalar()


def get_total_entregado() -> int:
    with SessionLocal() as s:
        return s.query(func.coalesce(func.sum(Entrega.cantidad), 0)).scalar()


def get_stock_actual() -> int:
    """Stock total sumando todos los tipos de resma."""
    return get_total_ingresos() - get_total_entregado()


def get_stock_por_tipo() -> dict:
    """Devuelve {tipo_resma: stock_disponible} para cada tipo conocido."""
    with SessionLocal() as s:
        ingresos = dict(
            s.query(Ingreso.tipo_resma, func.coalesce(func.sum(Ingreso.cantidad), 0))
            .group_by(Ingreso.tipo_resma)
            .all()
        )
        entregas = dict(
            s.query(Entrega.tipo_resma, func.coalesce(func.sum(Entrega.cantidad), 0))
            .group_by(Entrega.tipo_resma)
            .all()
        )
    return {
        tipo: ingresos.get(tipo, 0) - entregas.get(tipo, 0) for tipo in TIPOS_RESMA
    }


def get_ingresos_df() -> pd.DataFrame:
    stmt = select(Ingreso).order_by(Ingreso.fecha.desc())
    return pd.read_sql(stmt, engine)


# --- Entregas ------------------------------------------------------------------

def registrar_entrega(
    fecha: date, gerencia: str, empleado: str, tipo_resma: str, cantidad: int
) -> None:
    with SessionLocal() as s:
        s.add(
            Entrega(
                fecha=fecha,
                dia=dia_semana(fecha),
                gerencia=gerencia,
                empleado=empleado,
                tipo_resma=tipo_resma,
                cantidad=cantidad,
            )
        )
        s.commit()


def eliminar_entrega(entrega_id: int) -> None:
    """Elimina una entrega registrada por error; el stock se recalcula solo."""
    with SessionLocal() as s:
        entrega = s.get(Entrega, entrega_id)
        if entrega:
            s.delete(entrega)
            s.commit()


def get_entregas_df(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    gerencias: Optional[Iterable[str]] = None,
    empleados: Optional[Iterable[str]] = None,
    tipos_resma: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    stmt = select(Entrega)
    if fecha_desde:
        stmt = stmt.where(Entrega.fecha >= fecha_desde)
    if fecha_hasta:
        stmt = stmt.where(Entrega.fecha <= fecha_hasta)
    if gerencias:
        stmt = stmt.where(Entrega.gerencia.in_(list(gerencias)))
    if empleados:
        stmt = stmt.where(Entrega.empleado.in_(list(empleados)))
    if tipos_resma:
        stmt = stmt.where(Entrega.tipo_resma.in_(list(tipos_resma)))
    stmt = stmt.order_by(Entrega.fecha.desc())
    return pd.read_sql(stmt, engine)


# --- KPIs y agregados para el dashboard ------------------------------------------

def get_consumo_mes_actual() -> int:
    hoy = date.today()
    df = get_entregas_df(fecha_desde=hoy.replace(day=1))
    return int(df["cantidad"].sum()) if not df.empty else 0


def get_top_empleado(mes_actual: bool = True):
    hoy = date.today()
    desde = hoy.replace(day=1) if mes_actual else None
    df = get_entregas_df(fecha_desde=desde)
    if df.empty:
        return None, 0
    agg = df.groupby("empleado")["cantidad"].sum().sort_values(ascending=False)
    return agg.index[0], int(agg.iloc[0])


def get_top_gerencia(mes_actual: bool = True):
    hoy = date.today()
    desde = hoy.replace(day=1) if mes_actual else None
    df = get_entregas_df(fecha_desde=desde)
    if df.empty:
        return None, 0
    agg = df.groupby("gerencia")["cantidad"].sum().sort_values(ascending=False)
    return agg.index[0], int(agg.iloc[0])


def get_consumo_mensual(meses: int = 12) -> pd.DataFrame:
    df = get_entregas_df()
    if df.empty:
        return pd.DataFrame(columns=["periodo", "cantidad"])
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["periodo"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
    agg = df.groupby("periodo")["cantidad"].sum().reset_index()
    return agg.sort_values("periodo").tail(meses)


def get_consumo_por_gerencia(
    fecha_desde: Optional[date] = None, fecha_hasta: Optional[date] = None
) -> pd.DataFrame:
    df = get_entregas_df(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    if df.empty:
        return pd.DataFrame(columns=["gerencia", "cantidad"])
    return (
        df.groupby("gerencia")["cantidad"]
        .sum()
        .reset_index()
        .sort_values("cantidad", ascending=False)
    )
