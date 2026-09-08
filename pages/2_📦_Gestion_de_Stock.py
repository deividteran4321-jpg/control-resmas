"""Gestión de Stock e Inventario — ingreso de resmas y configuración."""
from datetime import date

import streamlit as st

from core.database import init_db
from core.theme import inject_custom_theme, render_sidebar_mascota
from core.queries import (
    add_gerencia,
    eliminar_gerencia,
    get_gerencias,
    get_ingresos_df,
    get_stock_actual,
    get_umbral_stock_bajo,
    registrar_ingreso,
    set_umbral_stock_bajo,
)

st.set_page_config(page_title="Gestión de Stock", page_icon="📦", layout="wide")
init_db()
inject_custom_theme()
render_sidebar_mascota()

st.title("📦 Gestión de Stock e Inventario")

stock_actual = get_stock_actual()
umbral = get_umbral_stock_bajo()

col1, col2 = st.columns(2)
col1.metric("Stock actual", f"{stock_actual} resmas")
col2.metric("Umbral de alerta", f"{umbral} resmas")

if stock_actual <= umbral:
    st.error(
        f"⚠️ Stock bajo: quedan {stock_actual} resmas (umbral: {umbral}). "
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
            cantidad = st.number_input(
                "Cantidad de resmas ingresadas", min_value=1, step=1, value=1
            )
        with col2:
            observacion = st.text_area(
                "Observación / Proveedor",
                placeholder="Ej: Compra a Papelería XYZ, factura 1234",
            )

        enviado = st.form_submit_button(
            "Registrar ingreso", type="primary", use_container_width=True
        )
        if enviado:
            registrar_ingreso(fecha, int(cantidad), observacion.strip())
            st.success(f"Ingreso registrado: {cantidad} resmas.")
            st.rerun()

    st.divider()
    st.subheader("Historial de ingresos")
    df_ing = get_ingresos_df()
    if df_ing.empty:
        st.info("Todavía no hay ingresos registrados.")
    else:
        st.dataframe(
            df_ing[["fecha", "cantidad", "observacion"]],
            use_container_width=True,
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
