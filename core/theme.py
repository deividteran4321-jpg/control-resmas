"""Tema visual: tipografías, fondo blanco con marco de franjas diagonales
azules (estilo sobre de correo aéreo) y pequeñas animaciones. Se inyecta como
CSS/HTML dentro de Streamlit — no requiere ningún paquete adicional.
"""
import streamlit as st


def inject_custom_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, [data-testid="stMetricLabel"] {
            font-family: 'Sora', sans-serif !important;
            letter-spacing: -0.01em;
        }

        html, body, .stApp {
            background: repeating-linear-gradient(
                45deg,
                #1d4ed8 0px, #1d4ed8 9px,
                #ffffff 9px, #ffffff 27px
            ) !important;
        }

        [data-testid="stAppViewContainer"] {
            background: #ffffff;
            margin: 12px;
            border-radius: 16px;
            box-shadow: 0 10px 34px rgba(29,78,216,0.16);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(37,99,235,0.06), rgba(255,255,255,0));
            border-right: 1px solid rgba(37,99,235,0.08);
            border-radius: 16px 0 0 16px;
        }

        .block-container {
            animation: fadeInUp 0.5s ease-out;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .franja-exportacion {
            position: relative;
            height: 34px;
            overflow: hidden;
            margin-bottom: 6px;
            background: linear-gradient(90deg, #eff6ff, #e0e7ff, #eff6ff);
            background-size: 200% 100%;
            border-radius: 10px;
            border: 1px solid rgba(37,99,235,0.14);
            animation: brillo 6s ease-in-out infinite;
        }
        @keyframes brillo {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        .resma-volando {
            position: absolute;
            left: -8%;
            font-size: 16px;
            animation-name: volar;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }
        .resma-volando.r1 { top: 3px;  animation-duration: 13s; animation-delay: 0s; }
        .resma-volando.r2 { top: 12px; animation-duration: 16s; animation-delay: 3s; }
        .resma-volando.r3 { top: 18px; animation-duration: 14s; animation-delay: 6.5s; }
        .resma-volando.r4 { top: 7px;  animation-duration: 18s; animation-delay: 9s; }
        @keyframes volar {
            from { left: -8%; transform: translateY(0); }
            50%  { transform: translateY(-4px); }
            to   { left: 106%; transform: translateY(0); }
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid rgba(37,99,235,0.16);
            border-radius: 14px;
            padding: 12px 16px 10px 16px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.05);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 22px rgba(29,78,216,0.16);
        }

        div[data-testid="stForm"] {
            background: rgba(37,99,235,0.03);
            border-radius: 16px;
            border: 1px solid rgba(37,99,235,0.12);
        }

        .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
            border-radius: 10px !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(37,99,235,0.30);
        }
        </style>

        <div class="franja-exportacion">
            <span class="resma-volando r1">📄</span>
            <span class="resma-volando r2">📄</span>
            <span class="resma-volando r3">📄</span>
            <span class="resma-volando r4">📄</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
