"""Estilos CSS y componentes HTML de la interfaz (Tema Claro, Alta Legibilidad)."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stText { font-family: 'Inter', sans-serif; color: #0f172a; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }

/* ------------------------------------------------------------------------- */
/* Panel lateral de opciones: FONDO CLARO Y ALTA LEGIBILIDAD                */
/* ------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
  background-color: #f8fafc !important;
  border-right: 1px solid #e2e8f0 !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
  color: #0f172a !important;
  font-weight: 500;
}

section[data-testid="stSidebar"] .stWidgetLabel label,
section[data-testid="stSidebar"] label[data-baseweb="checkbox"],
section[data-testid="stSidebar"] label[data-baseweb="radio"],
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label {
  color: #0f172a !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: #475569 !important;
  font-size: 0.82rem !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background-color: #ffffff !important;
  border-color: #cbd5e1 !important;
  color: #0f172a !important;
  border-radius: 8px !important;
}

section[data-testid="stSidebar"] input {
  background-color: #ffffff !important;
  color: #0f172a !important;
  border-color: #cbd5e1 !important;
  border-radius: 8px !important;
}

/* Encabezados de sección del panel lateral */
.side-h {
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 0.98rem;
  color: #0f172a !important;
  margin: 20px 0 8px;
  display: flex;
  gap: 8px;
  align-items: center;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 4px;
}
.side-h .n {
  background: #0284c7;
  color: #ffffff !important;
  border-radius: 6px;
  width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
}
.brand {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a !important;
  padding-bottom: 4px;
}
.brand small {
  display: block;
  font-family: 'Inter';
  font-weight: 500;
  font-size: 0.76rem;
  color: #64748b !important;
  margin-top: 2px;
}

/* ------------------------------------------------------------------------- */
/* Hero Header y Chips                                                       */
/* ------------------------------------------------------------------------- */
.hero {
  padding: 22px 28px;
  border-radius: 18px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border: 1px solid #334155;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
}
.hero h1 {
  font-family: 'Outfit', sans-serif;
  font-size: 1.95rem;
  font-weight: 800;
  margin: 8px 0 6px;
  line-height: 1.15;
  background: linear-gradient(90deg, #f8fafc, #38bdf8, #c084fc);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero p { color: #cbd5e1; margin: 0; max-width: 980px; font-size: .95rem; }
.badge {
  display: inline-block; font-size: .7rem; letter-spacing: .08em; text-transform: uppercase;
  color: #38bdf8; border: 1px solid rgba(56,189,248,.4); padding: 3px 10px;
  border-radius: 999px; background: rgba(56,189,248,.12); font-weight: 600;
}
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 12px; }
.chips span {
  font-size: .78rem; color: #334155; background: #ffffff; border: 1px solid #cbd5e1;
  padding: 4px 12px; border-radius: 999px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.chips span b { color: #0284c7; font-weight: 700; }

/* ------------------------------------------------------------------------- */
/* Tarjetas KPI de métricas                                                  */
/* ------------------------------------------------------------------------- */
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
  gap: 12px;
  margin: 14px 0 10px;
}
.kpi {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  border-radius: 14px;
  padding: 12px 16px;
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.kpi:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-color: #0284c7;
}
.kpi .l {
  font-size: .7rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: .06em;
  font-weight: 600;
}
.kpi .v {
  font-family: 'Outfit', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.25;
}
.kpi .s { font-size: .74rem; color: #64748b; margin-top: 2px; }
.kpi.c0 .v { color: #0284c7; }
.kpi.c1 .v { color: #ea580c; }
.kpi.c2 .v { color: #7c3aed; }

/* ------------------------------------------------------------------------- */
/* Pestañas (Tabs) y Pie de página                                          */
/* ------------------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #e2e8f0; }
.stTabs [data-baseweb="tab"] {
  background: #f1f5f9;
  border-radius: 10px 10px 0 0;
  padding: 10px 20px;
  color: #475569 !important;
  font-weight: 600;
}
.stTabs [aria-selected="true"] {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-bottom: 2px solid #0284c7 !important;
  color: #0284c7 !important;
}
.footer { text-align: center; color: #64748b; font-size: .8rem; margin-top: 32px; padding-top: 14px; border-top: 1px solid #e2e8f0; }
</style>
"""


def kpis(items) -> str:
    """items: lista de (etiqueta, valor, subtítulo, clase)."""
    cells = "".join(
        f"<div class='kpi {c}'><div class='l'>{l}</div><div class='v'>{v}</div>"
        f"<div class='s'>{s}</div></div>" for l, v, s, c in items)
    return f"<div class='kpis'>{cells}</div>"


def chips(items) -> str:
    return "<div class='chips'>" + "".join(f"<span>{k}: <b>{v}</b></span>" for k, v in items) + "</div>"


def side_header(n, text) -> str:
    return f"<div class='side-h'><span class='n'>{n}</span>{text}</div>"


def fmt_int(n) -> str:
    return f"{int(n):,}".replace(",", ".")
