"""Registro de Entregas — formulario de carga rápida."""
from datetime import date

import streamlit as st

from core.database import TIPOS_RESMA, init_db
from core.theme import inject_custom_theme
from core.queries import (
    add_gerencia,
    dia_semana,
    eliminar_entrega,
    get_empleados_conocidos,
    get_entregas_df,
    get_gerencias,
    get_stock_por_tipo,
    registrar_entrega,
)

st.set_page_config(page_title="Registro de Entregas", page_icon="📥", layout="wide")
init_db()
inject_custom_theme()

st.title("📥 Registro de Entregas")
st.caption("Carga rápida de resmas entregadas por empleado y gerencia.")

stock_por_tipo = get_stock_por_tipo()
cols_stock = st.columns(len(TIPOS_RESMA))
for col, tipo in zip(cols_stock, TIPOS_RESMA):
    col.metric(tipo, f"{stock_por_tipo[tipo]} resmas")

gerencias = get_gerencias()
empleados = get_empleados_conocidos()

NUEVA_GERENCIA = "➕ Nueva gerencia..."
NUEVO_EMPLEADO = "➕ Nuevo empleado..."

with st.form("form_entrega", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
    with col2:
        st.text_input("Día", value=dia_semana(fecha), disabled=True)

    col3, col4 = st.columns(2)
    with col3:
        gerencia_sel = st.selectbox("Gerencia", options=[NUEVA_GERENCIA] + gerencias)
        gerencia_nueva = ""
        if gerencia_sel == NUEVA_GERENCIA:
            gerencia_nueva = st.text_input("Nombre de la nueva gerencia")
    with col4:
        empleado_sel = st.selectbox("Empleado", options=[NUEVO_EMPLEADO] + empleados)
        empleado_nuevo = ""
        if empleado_sel == NUEVO_EMPLEADO:
            empleado_nuevo = st.text_input("Nombre del nuevo empleado")

    col5, col6 = st.columns(2)
    with col5:
        tipo_sel = st.selectbox("Tipo de resma", options=TIPOS_RESMA)
    with col6:
        cantidad = st.number_input(
            "Cantidad de resmas entregadas", min_value=1, step=1, value=1
        )

    enviado = st.form_submit_button(
        "Registrar entrega", type="primary", width="stretch"
    )

    if enviado:
        gerencia_final = (
            gerencia_nueva.strip() if gerencia_sel == NUEVA_GERENCIA else gerencia_sel
        )
        empleado_final = (
            empleado_nuevo.strip() if empleado_sel == NUEVO_EMPLEADO else empleado_sel
        )
        stock_disponible_tipo = stock_por_tipo[tipo_sel]

        if not gerencia_final:
            st.error("Debes indicar una gerencia.")
        elif not empleado_final:
            st.error("Debes indicar el nombre del empleado.")
        elif cantidad > stock_disponible_tipo:
            st.error(
                f"No hay stock suficiente de {tipo_sel}. "
                f"Stock disponible: {stock_disponible_tipo} resmas."
            )
        else:
            if gerencia_sel == NUEVA_GERENCIA:
                add_gerencia(gerencia_final)
            registrar_entrega(
                fecha, gerencia_final, empleado_final, tipo_sel, int(cantidad)
            )
            st.success(
                f"Entrega registrada: {cantidad} resmas de {tipo_sel} para "
                f"{empleado_final} ({gerencia_final})."
            )
            st.rerun()

st.divider()
st.subheader("Últimas entregas registradas")
df = get_entregas_df()
if df.empty:
    st.info("Todavía no hay entregas registradas.")
else:
    columnas = ["fecha", "dia", "gerencia", "empleado", "tipo_resma", "cantidad"]
    ultimas = df.head(20)
    st.dataframe(ultimas[columnas], width="stretch", hide_index=True)

    st.markdown("##### ¿Cargaste algo por error?")
    opciones = {
        f"#{row.id} · {row.fecha} · {row.gerencia} · {row.empleado} · "
        f"{row.tipo_resma} · {row.cantidad} resmas": row.id
        for row in ultimas.itertuples()
    }
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        seleccion = st.selectbox(
            "Selecciona la entrega a eliminar",
            options=list(opciones.keys()),
            label_visibility="collapsed",
        )
    with col_btn:
        if st.button("🗑️ Eliminar", width="stretch"):
            eliminar_entrega(opciones[seleccion])
            st.success("Entrega eliminada. El stock se restauró automáticamente.")
            st.rerun()
