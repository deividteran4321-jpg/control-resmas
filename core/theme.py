"""Tema visual: tipografías, fondo con motivo de embarques/exportación y
pequeñas animaciones. Se inyecta como CSS/HTML dentro de Streamlit — no
requiere ningún paquete adicional.
"""
from urllib.parse import quote

import streamlit as st

_PATTERN_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320' viewBox='0 0 320 320'>
  <g fill='none' stroke='#60a5fa' stroke-width='1.6' stroke-opacity='0.55'>
    <path d='M24 56 L66 56 L84 38 L90 38 L81 56 L114 56 L120 61 L81 61 L88 78 L82 78 L69 61 L24 61 Z'/>
  </g>
  <g fill='none' stroke='#34d399' stroke-width='1.6' stroke-opacity='0.5'>
    <rect x='200' y='170' width='46' height='34' rx='2'/>
    <line x1='200' y1='187' x2='246' y2='187'/>
    <line x1='223' y1='170' x2='223' y2='204'/>
  </g>
  <g fill='none' stroke='#93c5fd' stroke-width='1.4' stroke-opacity='0.45'>
    <path d='M190 50 L218 50 L230 37 L234 37 L228 50 L248 50 L252 54 L228 54 L233 65 L229 65 L220 54 L190 54 Z'/>
  </g>
  <g fill='none' stroke='#6ee7b7' stroke-width='1.4' stroke-opacity='0.42'>
    <rect x='50' y='210' width='34' height='26' rx='2'/>
    <line x1='50' y1='223' x2='84' y2='223'/>
    <line x1='67' y1='210' x2='67' y2='236'/>
  </g>
</svg>
"""
_PATTERN_DATA_URI = "data:image/svg+xml," + quote(_PATTERN_SVG)


def inject_custom_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        h1, h2, h3, h4, [data-testid="stMetricLabel"] {{
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: -0.01em;
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)),
                linear-gradient(135deg, #eef4ff 0%, #f7fbff 50%, #eafaf3 100%),
                url("{_PATTERN_DATA_URI}");
            background-size: auto, cover, 320px 320px;
            background-repeat: repeat, no-repeat, repeat;
            background-attachment: fixed, fixed, fixed;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(37,99,235,0.05), rgba(255,255,255,0.0));
        }}

        .block-container {{
            animation: fadeInUp 0.5s ease-out;
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .franja-exportacion {{
            position: relative;
            height: 30px;
            overflow: hidden;
            margin-bottom: 4px;
            background: linear-gradient(90deg, #eff6ff, #ecfdf5, #eff6ff);
            background-size: 200% 100%;
            border-radius: 10px;
            animation: brillo 6s ease-in-out infinite;
        }}
        @keyframes brillo {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}
        .avion-volando {{
            position: absolute;
            top: 4px;
            left: -8%;
            font-size: 18px;
            animation: volar 15s linear infinite;
        }}
        @keyframes volar {{
            from {{ left: -8%; }}
            to   {{ left: 106%; }}
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(37,99,235,0.14);
            border-radius: 14px;
            padding: 12px 16px 10px 16px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.05);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 22px rgba(15,23,42,0.12);
        }}

        div[data-testid="stForm"] {{
            background: rgba(255,255,255,0.7);
            border-radius: 16px;
            border: 1px solid rgba(37,99,235,0.10);
        }}

        .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {{
            border-radius: 10px !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(37,99,235,0.28);
        }}
        </style>

        <div class="franja-exportacion">
            <span class="avion-volando">✈️</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
