"""Generación de archivos descargables (Excel y PDF) a partir de un DataFrame."""
import io
from datetime import date

import pandas as pd
from fpdf import FPDF


def build_excel_bytes(df: pd.DataFrame, sheet_name: str = "Reporte") -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def build_pdf_bytes(df: pd.DataFrame, titulo: str, subtitulo: str = "") -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, titulo, ln=1)
    if subtitulo:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, subtitulo, ln=1)
    pdf.ln(4)

    columnas = list(df.columns)
    ancho = 190 / max(len(columnas), 1)

    pdf.set_font("Helvetica", "B", 9)
    for col in columnas:
        pdf.cell(ancho, 8, str(col).capitalize(), border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for _, fila in df.iterrows():
        for col in columnas:
            valor = str(fila[col])
            if len(valor) > 28:
                valor = valor[:25] + "..."
            pdf.cell(ancho, 7, valor, border=1)
        pdf.ln()

    pdf.set_font("Helvetica", "I", 8)
    pdf.ln(4)
    pdf.cell(0, 6, f"Generado el {date.today().strftime('%d/%m/%Y')}", ln=1)

    return bytes(pdf.output())
