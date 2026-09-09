"""Gestión de Stock e Inventario — ingreso de resmas y configuración."""
from datetime import date

import streamlit as st

from core.database import TIPOS_RESMA, init_db
from core.theme import inject_custom_theme
from core.queries import (
    add_gerencia,
    eliminar_gerencia,
    get_gerencias,
    get_ingresos_df,
    get_stock_actual,
    get_stock_por_tipo,
    get_umbral_stock_bajo,
    registrar_ingreso,
    set_umbral_stock_bajo,
)

st.set_page_config(page_title="Gestión de Stock", page_icon="📦", layout="wide")
init_db()
inject_custom_theme()

st.title("📦 Gestión de Stock e Inventario")

stock_actual = get_stock_actual()
stock_por_tipo = get_stock_por_tipo()
umbral = get_umbral_stock_bajo()

col1, col2 = st.columns(2)
col1.metric("Stock actual (total)", f"{stock_actual} resmas")
col2.metric("Umbral de alerta", f"{umbral} resmas")

cols_tipo = st.columns(len(TIPOS_RESMA))
for col, tipo in zip(cols_tipo, TIPOS_RESMA):
    col.metric(tipo, f"{stock_por_tipo[tipo]} resmas")

tipos_bajos = [t for t, c in stock_por_tipo.items() if c <= umbral]
if tipos_bajos:
    detalle = " · ".join(f"{t}: {stock_por_tipo[t]}" for t in tipos_bajos)
    st.error(
        f"⚠️ Stock bajo (umbral: {umbral} resmas) → {detalle}. "
        "Registra un nuevo ingreso a continuación."
    )

tab_ingreso, tab_config = st.tabs(["➕ Ingresar Stock", "⚙️ Gerencias y Configuración"])

with tab_ingreso:
    with st.form("form_ingreso", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input(
                "Fecha de ingreso", value=date.today(), format="DD/MM/YYYY"
            )
            tipo_sel = st.selectbox("Tipo de resma", options=TIPOS_RESMA)
            cantidad = st.number_input(
                "Cantidad de resmas ingresadas", min_value=1, step=1, value=1
            )
        with col2:
            observacion = st.text_area(
                "Observación / Proveedor",
                placeholder="Ej: Compra a Papelería XYZ, factura 1234",
            )

        enviado = st.form_submit_button(
            "Registrar ingreso", type="primary", width="stretch"
        )
        if enviado:
            registrar_ingreso(fecha, tipo_sel, int(cantidad), observacion.strip())
            st.success(f"Ingreso registrado: {cantidad} resmas de {tipo_sel}.")
            st.rerun()

    st.divider()
    st.subheader("Historial de ingresos")
    df_ing = get_ingresos_df()
    if df_ing.empty:
        st.info("Todavía no hay ingresos registrados.")
    else:
        st.dataframe(
            df_ing[["fecha", "tipo_resma", "cantidad", "observacion"]],
            width="stretch",
            hide_index=True,
        )

with tab_config:
    st.subheader("Umbral de alerta de stock bajo")
    nuevo_umbral = st.number_input(
        "Notificar cuando el stock sea menor o igual a:",
        min_value=0,
        step=10,
        value=umbral,
    )
    if st.button("Guardar umbral"):
        set_umbral_stock_bajo(int(nuevo_umbral))
        st.success("Umbral actualizado.")
        st.rerun()

    st.divider()
    st.subheader("Gerencias registradas")
    gerencias = get_gerencias()
    st.write(", ".join(gerencias) if gerencias else "No hay gerencias registradas.")

    col1, col2 = st.columns(2)
    with col1:
        nueva = st.text_input("Agregar nueva gerencia")
        if st.button("Agregar gerencia") and nueva.strip():
            add_gerencia(nueva.strip())
            st.success(f"Gerencia '{nueva.strip()}' agregada.")
            st.rerun()
    with col2:
        if gerencias:
            a_eliminar = st.selectbox("Eliminar gerencia", options=gerencias)
            if st.button("Eliminar gerencia"):
                ok = eliminar_gerencia(a_eliminar)
                if ok:
                    st.success(f"Gerencia '{a_eliminar}' eliminada.")
                    st.rerun()
                else:
                    st.error(
                        "No se puede eliminar: tiene entregas registradas asociadas."
                    )
