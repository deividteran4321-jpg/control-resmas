"""Dashboard principal — Control de Inventario y Consumo de Resmas."""
from datetime import date, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.database import TIPOS_RESMA, init_db
from core.theme import inject_custom_theme
from core.queries import (
    get_consumo_mensual,
    get_consumo_por_gerencia,
    get_consumo_por_tipo,
    get_consumo_total,
    get_empleados_de_gerencia,
    get_serie_diaria,
    get_stock_actual,
    get_stock_historico,
    get_stock_por_tipo,
    get_top_empleado,
    get_top_gerencia,
    get_umbral_stock_bajo,
    periodo_anterior,
)

st.set_page_config(page_title="Control de Resmas", page_icon="📄", layout="wide")
init_db()
inject_custom_theme()

st.title("📄 Control de Inventario y Consumo de Resmas")

PALETA = ["#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd"]

PERIODOS = {
    "Este mes": lambda hoy: (hoy.replace(day=1), hoy),
    "Últimos 3 meses": lambda hoy: (hoy - timedelta(days=89), hoy),
    "Este año": lambda hoy: (date(hoy.year, 1, 1), hoy),
    "Todo": lambda hoy: (None, None),
}

col_caption, col_periodo = st.columns([3, 1])
with col_caption:
    st.caption(
        "Usa el menú lateral para registrar entregas, gestionar el stock o generar reportes."
    )
with col_periodo:
    periodo_sel = st.selectbox(
        "Periodo", options=list(PERIODOS.keys()), index=0, label_visibility="collapsed"
    )

hoy = date.today()
fecha_desde, fecha_hasta = PERIODOS[periodo_sel](hoy)
desde_ant, hasta_ant = periodo_anterior(fecha_desde, fecha_hasta)


def _delta(actual: int, anterior):
    if not anterior:
        return None
    signo = "+" if actual >= anterior else ""
    return f"{signo}{actual - anterior} vs. periodo anterior"


def _sparkline(df, x, y, color, relleno):
    fig = go.Figure(
        go.Scatter(
            x=df[x],
            y=df[y],
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=relleno,
        )
    )
    fig.update_layout(
        height=48,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


_CHART_CONFIG = {"displayModeBar": False}

# --- KPIs --------------------------------------------------------------------

stock_actual = get_stock_actual()
stock_por_tipo = get_stock_por_tipo()
umbral = get_umbral_stock_bajo()
consumo_periodo = get_consumo_total(fecha_desde, fecha_hasta)
consumo_anterior = get_consumo_total(desde_ant, hasta_ant) if desde_ant else None
top_empleado, cant_empleado = get_top_empleado(fecha_desde, fecha_hasta)
top_gerencia, cant_gerencia = get_top_gerencia(fecha_desde, fecha_hasta)

tipos_bajos = [t for t, c in stock_por_tipo.items() if c <= umbral]
if tipos_bajos:
    detalle = " · ".join(f"{t}: {stock_por_tipo[t]} resmas" for t in tipos_bajos)
    st.error(
        f"⚠️ Stock bajo (umbral: {umbral} resmas) → {detalle}. "
        "Ve a **Gestión de Stock** para ingresar más."
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Stock actual", f"{stock_actual} resmas")
    df_stock_hist = get_stock_historico(dias=30)
    if not df_stock_hist.empty:
        st.plotly_chart(
            _sparkline(df_stock_hist, "fecha", "stock", "#1d4ed8", "rgba(29,78,216,0.15)"),
            use_container_width=True,
            config=_CHART_CONFIG,
        )
with col2:
    st.metric(
        f"🗓️ Consumido ({periodo_sel.lower()})",
        f"{consumo_periodo} resmas",
        _delta(consumo_periodo, consumo_anterior),
    )
    df_serie = get_serie_diaria(fecha_desde, fecha_hasta)
    if not df_serie.empty:
        st.plotly_chart(
            _sparkline(df_serie, "fecha", "cantidad", "#10b981", "rgba(16,185,129,0.15)"),
            use_container_width=True,
            config=_CHART_CONFIG,
        )
with col3:
    st.metric(
        "🏆 Usuario que más gastó",
        top_empleado or "—",
        f"{cant_empleado} resmas" if top_empleado else None,
    )
with col4:
    st.metric(
        "🏢 Gerencia con mayor consumo",
        top_gerencia or "—",
        f"{cant_gerencia} resmas" if top_gerencia else None,
    )

st.divider()

tab_resumen, tab_tipo, tab_gerencia = st.tabs(
    ["📈 Resumen", "📄 Por tipo de resma", "🏢 Por gerencia"]
)

with tab_resumen:
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Evolución del consumo mensual")
        df_mensual = get_consumo_mensual(meses=12)
        if df_mensual.empty:
            st.info("Aún no hay entregas registradas para graficar.")
        else:
            fig = px.area(
                df_mensual,
                x="periodo",
                y="cantidad",
                labels={"periodo": "Mes", "cantidad": "Resmas"},
                color_discrete_sequence=["#1d4ed8"],
            )
            fig.update_traces(line=dict(width=3))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(gridcolor="rgba(37,99,235,0.10)"),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_der:
        st.subheader("Consumo por gerencia")
        st.caption("Haz clic en una barra para ver sus empleados.")
        df_gerencia = get_consumo_por_gerencia(fecha_desde, fecha_hasta)
        gerencia_clic = None
        if df_gerencia.empty:
            st.info("Aún no hay entregas registradas para graficar.")
        else:
            fig2 = px.bar(
                df_gerencia,
                x="gerencia",
                y="cantidad",
                labels={"gerencia": "Gerencia", "cantidad": "Resmas"},
                color_discrete_sequence=["#2563eb"],
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(gridcolor="rgba(37,99,235,0.10)"),
            )
            evento = st.plotly_chart(
                fig2,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key="chart_gerencia",
            )
            puntos = (evento or {}).get("selection", {}).get("points", [])
            if puntos:
                gerencia_clic = puntos[0].get("x")

        if gerencia_clic:
            df_emp = get_empleados_de_gerencia(gerencia_clic, fecha_desde, fecha_hasta)
            st.markdown(f"**Top empleados en {gerencia_clic}:**")
            if df_emp.empty:
                st.info("Sin entregas en ese periodo.")
            else:
                st.dataframe(
                    df_emp.head(8),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "cantidad": st.column_config.ProgressColumn(
                            "Resmas",
                            min_value=0,
                            max_value=int(df_emp["cantidad"].max()),
                            format="%d",
                        )
                    },
                )

with tab_tipo:
    cols_tipo = st.columns(len(TIPOS_RESMA))
    for col, tipo in zip(cols_tipo, TIPOS_RESMA):
        col.metric(tipo, f"{stock_por_tipo[tipo]} resmas")

    st.subheader("Consumo por tipo de resma")
    df_tipo = get_consumo_por_tipo(fecha_desde, fecha_hasta)
    if df_tipo.empty:
        st.info("Aún no hay entregas registradas para graficar.")
    else:
        col_pie, col_tabla = st.columns([1, 1])
        with col_pie:
            fig3 = px.pie(
                df_tipo,
                names="tipo_resma",
                values="cantidad",
                hole=0.55,
                color_discrete_sequence=PALETA,
            )
            fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig3, use_container_width=True)
        with col_tabla:
            st.dataframe(
                df_tipo,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "cantidad": st.column_config.ProgressColumn(
                        "Resmas",
                        min_value=0,
                        max_value=int(df_tipo["cantidad"].max()),
                        format="%d",
                    )
                },
            )

with tab_gerencia:
    st.subheader("Ranking de gerencias")
    df_gerencia_full = get_consumo_por_gerencia(fecha_desde, fecha_hasta)
    if df_gerencia_full.empty:
        st.info("Aún no hay entregas registradas.")
    else:
        st.dataframe(
            df_gerencia_full,
            use_container_width=True,
            hide_index=True,
            column_config={
                "cantidad": st.column_config.ProgressColumn(
                    "Resmas consumidas",
                    min_value=0,
                    max_value=int(df_gerencia_full["cantidad"].max()),
                    format="%d",
                )
            },
        )
