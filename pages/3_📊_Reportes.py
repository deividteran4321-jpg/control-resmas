"""Módulo de Reportes — filtros, resúmenes y exportación."""
from datetime import date

import pandas as pd
import streamlit as st

from core.database import init_db
from core.theme import inject_custom_theme
from core.exports import build_excel_bytes, build_pdf_bytes
from core.queries import get_empleados_conocidos, get_entregas_df, get_gerencias

st.set_page_config(page_title="Reportes", page_icon="📊", layout="wide")
init_db()
inject_custom_theme()

st.title("📊 Módulo de Reportes")

gerencias = get_gerencias()
empleados = get_empleados_conocidos()

col1, col2, col3, col4 = st.columns(4)
with col1:
    fecha_desde = st.date_input(
        "Desde", value=date.today().replace(day=1), format="DD/MM/YYYY"
    )
with col2:
    fecha_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY")
with col3:
    gerencias_sel = st.multiselect("Gerencia(s)", options=gerencias, default=[])
with col4:
    empleados_sel = st.multiselect("Empleado(s)", options=empleados, default=[])

df = get_entregas_df(
    fecha_desde=fecha_desde,
    fecha_hasta=fecha_hasta,
    gerencias=gerencias_sel or None,
    empleados=empleados_sel or None,
)

st.divider()
c1, c2 = st.columns(2)
c1.metric("Total de resmas entregadas", int(df["cantidad"].sum()) if not df.empty else 0)
c2.metric("Cantidad de entregas", len(df))

columnas = ["fecha", "dia", "gerencia", "empleado", "cantidad"]

st.subheader("Detalle de entregas")
if df.empty:
    st.info("No hay datos para los filtros seleccionados.")
else:
    st.dataframe(df[columnas], use_container_width=True, hide_index=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.subheader("Resumen por gerencia")
        resumen_gerencia = (
            df.groupby("gerencia")["cantidad"]
            .sum()
            .reset_index()
            .sort_values("cantidad", ascending=False)
        )
        st.dataframe(resumen_gerencia, use_container_width=True, hide_index=True)

    with col_res2:
        st.subheader("Conteo mensual")
        df_mes = df.copy()
        df_mes["mes"] = pd.to_datetime(df_mes["fecha"]).dt.to_period("M").astype(str)
        resumen_mensual = df_mes.groupby("mes")["cantidad"].sum().reset_index()
        st.dataframe(resumen_mensual, use_container_width=True, hide_index=True)

    st.subheader("Exportar reporte")
    subtitulo = (
        f"Periodo: {fecha_desde.strftime('%d/%m/%Y')} - {fecha_hasta.strftime('%d/%m/%Y')}"
    )
    col_csv, col_xlsx, col_pdf = st.columns(3)
    with col_csv:
        st.download_button(
            "⬇️ Descargar CSV",
            data=df[columnas].to_csv(index=False).encode("utf-8-sig"),
            file_name=f"reporte_resmas_{fecha_desde}_{fecha_hasta}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_xlsx:
        st.download_button(
            "⬇️ Descargar Excel",
            data=build_excel_bytes(df[columnas], sheet_name="Entregas"),
            file_name=f"reporte_resmas_{fecha_desde}_{fecha_hasta}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col_pdf:
        st.download_button(
            "⬇️ Descargar PDF",
            data=build_pdf_bytes(
                df[columnas], "Reporte de Consumo de Resmas", subtitulo
            ),
            file_name=f"reporte_resmas_{fecha_desde}_{fecha_hasta}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
