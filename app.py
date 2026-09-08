"""Dashboard principal — Control de Inventario y Consumo de Resmas."""
import plotly.express as px
import streamlit as st

from core.database import init_db
from core.theme import inject_custom_theme, render_sidebar_mascota
from core.queries import (
    get_consumo_mensual,
    get_consumo_mes_actual,
    get_consumo_por_gerencia,
    get_stock_actual,
    get_top_empleado,
    get_top_gerencia,
    get_umbral_stock_bajo,
)

st.set_page_config(page_title="Control de Resmas", page_icon="📄", layout="wide")
init_db()
inject_custom_theme()
render_sidebar_mascota()

st.title("📄 Control de Inventario y Consumo de Resmas")
st.caption(
    "Usa el menú lateral para registrar entregas, gestionar el stock o generar reportes."
)

stock_actual = get_stock_actual()
umbral = get_umbral_stock_bajo()
consumo_mes = get_consumo_mes_actual()
top_empleado, cant_empleado = get_top_empleado(mes_actual=True)
top_gerencia, cant_gerencia = get_top_gerencia(mes_actual=True)

if stock_actual <= umbral:
    st.error(
        f"⚠️ Stock bajo: quedan **{stock_actual} resmas** "
        f"(umbral configurado: {umbral}). Ve a **Gestión de Stock** para ingresar más."
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Stock actual", f"{stock_actual} resmas")
col2.metric("🗓️ Consumido este mes", f"{consumo_mes} resmas")
col3.metric(
    "🏆 Usuario que más gastó (mes)",
    top_empleado or "—",
    f"{cant_empleado} resmas" if top_empleado else None,
)
col4.metric(
    "🏢 Gerencia con mayor consumo (mes)",
    top_gerencia or "—",
    f"{cant_gerencia} resmas" if top_gerencia else None,
)

st.divider()

col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Evolución del consumo mensual")
    df_mensual = get_consumo_mensual(meses=12)
    if df_mensual.empty:
        st.info("Aún no hay entregas registradas para graficar.")
    else:
        fig = px.line(
            df_mensual,
            x="periodo",
            y="cantidad",
            markers=True,
            labels={"periodo": "Mes", "cantidad": "Resmas"},
        )
        st.plotly_chart(fig, use_container_width=True)

with col_der:
    st.subheader("Consumo total por gerencia")
    df_gerencia = get_consumo_por_gerencia()
    if df_gerencia.empty:
        st.info("Aún no hay entregas registradas para graficar.")
    else:
        fig2 = px.bar(
            df_gerencia,
            x="gerencia",
            y="cantidad",
            labels={"gerencia": "Gerencia", "cantidad": "Resmas"},
        )
        st.plotly_chart(fig2, use_container_width=True)
