# 📄 Control de Inventario y Consumo de Resmas

Aplicación web para llevar el stock de resmas de papel de la empresa, registrar
las entregas a empleados/gerencias, y generar reportes para las jefaturas.

Construida con **Streamlit** (Python) porque permite tener Dashboard + formularios
+ gráficos + exportación de reportes con un único lenguaje, sin separar frontend
y backend, y porque se despliega gratis en minutos.

## Estructura del proyecto

```
control-resmas/
├── Control_de_Resmas.py            Dashboard principal (KPIs + gráficos)
├── core/
│   ├── database.py                 Conexión a BD + modelos (SQLAlchemy)
│   ├── queries.py                  Toda la lógica de negocio (altas, KPIs, filtros)
│   └── exports.py                  Generación de archivos Excel y PDF
├── pages/
│   ├── 1_📥_Registro_de_Entregas.py   Formulario rápido de carga de entregas
│   ├── 2_📦_Gestion_de_Stock.py       Ingreso de stock + alertas + catálogo de gerencias
│   └── 3_📊_Reportes.py               Filtros, resúmenes y exportación CSV/Excel/PDF
├── .streamlit/
│   ├── config.toml                 Tema visual de la app
│   └── secrets.toml.example        Plantilla para configurar la base de datos
├── requirements.txt
├── Dockerfile
└── data/                           Carpeta para la BD SQLite en uso local
```

Streamlit detecta automáticamente los archivos dentro de `pages/` y genera el
menú de navegación lateral en el orden numérico del nombre de archivo. Para
agregar una funcionalidad nueva, solo hay que crear un archivo más en `pages/`
y reutilizar las funciones de `core/queries.py`.

## Modelo de datos (resumen)

- **Ingreso**: fecha, cantidad, observación → suma al stock global.
- **Entrega**: fecha, día, gerencia, empleado, cantidad → resta del stock global.
- **Stock actual** = total ingresado − total entregado (se calcula al vuelo, no
  se guarda como número aparte, así nunca se desincroniza).
- **Gerencia**: catálogo editable (con datos por defecto ya cargados).
- **Configuracion**: guarda el umbral de alerta de stock bajo.

## 1. Ejecutar en tu computadora

Requiere Python 3.10 o superior.

```bash
cd control-resmas
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run Control_de_Resmas.py
```

Se abrirá en `http://localhost:8501`. La primera vez se crea automáticamente
`data/inventario.db` (SQLite) con el catálogo de gerencias por defecto.

## 2. Importante antes de desplegar: dónde vive la base de datos

Por defecto la app usa un archivo **SQLite local** (`data/inventario.db`). Esto
funciona perfecto en tu computadora, **pero no en la nube**: tanto Streamlit
Community Cloud como el plan gratuito de Render usan almacenamiento **efímero**
— cuando la app se reinicia (duerme por inactividad, se redespliega, etc.) el
archivo SQLite vuelve a su estado original y **se pierden los datos cargados**.

Para uso en equipo con datos persistentes, la app ya está preparada para
apuntar a un **Postgres gratuito** simplemente configurando una variable
`DATABASE_URL` — no hay que tocar código. Opciones gratuitas recomendadas:

- [Neon](https://neon.tech) (Postgres serverless, capa gratuita generosa)
- [Supabase](https://supabase.com) (Postgres + panel de administración)
- Postgres gratuito de Render (si despliegas también en Render)

Al crear la base, copia la cadena de conexión y transfórmala a este formato:

```
postgresql+psycopg2://usuario:password@host:5432/nombre_bd
```

## 3. Despliegue rápido en Streamlit Community Cloud (recomendado)

1. Crea un repositorio en GitHub y sube el contenido de esta carpeta
   (`control-resmas/`) como raíz del repo:
   ```bash
   cd control-resmas
   git init
   git add .
   git commit -m "Control de inventario de resmas"
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
   git push -u origin main
   ```
2. Entra a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con
   GitHub.
3. Clic en **"New app"**, selecciona el repositorio y la rama `main`, y en
   "Main file path" escribe `Control_de_Resmas.py`.
4. Antes de darle a **Deploy**, abre **"Advanced settings" → "Secrets"** y pega:
   ```toml
   DATABASE_URL = "postgresql+psycopg2://usuario:password@host:5432/nombre_bd"
   ```
   (usa la cadena de tu Neon/Supabase del paso 2; si la omites, la app funciona
   igual pero con SQLite efímero — solo para pruebas).
5. Dale a **Deploy**. En 1-2 minutos tendrás una URL pública tipo
   `https://tu-app.streamlit.app` para compartir con tu equipo.

Para actualizar la app después: simplemente haz `git push` — Streamlit Cloud
redespliega automáticamente.

## 4. Alternativa: despliegue en Render (con Docker)

1. Sube el repo a GitHub (igual que el paso 1 anterior).
2. En [render.com](https://render.com) → **New → Web Service**, conecta el
   repositorio y elige **Docker** como entorno (usará el `Dockerfile` incluido).
3. En **Environment → Environment Variables** agrega:
   - `DATABASE_URL` → tu cadena de Postgres (Neon/Supabase, o el Postgres
     gratuito que Render también ofrece como servicio aparte).
4. Deja el puerto por defecto (el Dockerfile expone `8501`); Render lo detecta
   solo. Al desplegar obtienes una URL pública `https://tu-app.onrender.com`.

## 5. Uso diario de la aplicación

- **Dashboard**: stock actual, alerta visual si el stock cae al o por debajo
  del umbral configurado, consumo del mes, top empleado y top gerencia del
  mes, y los dos gráficos (evolución mensual y comparativa por gerencia).
- **Registro de Entregas**: formulario de 4 campos pensado para cargar en
  segundos; permite agregar gerencias o empleados nuevos al vuelo sin salir
  del formulario, y bloquea la carga si no hay stock suficiente.
- **Gestión de Stock**: pestaña para ingresar resmas nuevas (suman al stock
  global de inmediato) y pestaña de configuración para ajustar el umbral de
  alerta y administrar el catálogo de gerencias.
- **Reportes**: filtra por rango de fechas, gerencia(s) y empleado(s); muestra
  resumen por gerencia y por mes; exporta el detalle filtrado en CSV, Excel o
  PDF con un clic, listo para enviar a las jefaturas.

## 6. Notas técnicas

- El día de la semana de cada entrega se calcula automáticamente a partir de
  la fecha (no se escribe a mano).
- Borrar una gerencia solo se permite si no tiene entregas asociadas, para no
  perder la trazabilidad histórica de los reportes.
- Los archivos `.streamlit/secrets.toml` y `data/*.db` están en `.gitignore`:
  nunca se suben credenciales ni la base local al repositorio.
