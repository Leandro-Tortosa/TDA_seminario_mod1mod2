"""Estilos CSS y componentes HTML de la interfaz."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, .stText { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1426 0%,#0a0f1d 100%);
  border-right: 1px solid rgba(255,255,255,.06); }
.hero { padding: 22px 28px; border-radius: 18px; margin-bottom: 12px; position: relative; overflow: hidden;
  background: radial-gradient(900px 260px at 0% 0%, rgba(34,211,238,.22), transparent 60%),
              radial-gradient(800px 260px at 100% 0%, rgba(167,139,250,.25), transparent 60%),
              linear-gradient(135deg,#0f172a,#111a33);
  border: 1px solid rgba(255,255,255,.08); }
.hero h1 { font-family: 'Outfit', sans-serif; font-size: 1.95rem; font-weight: 800; margin: 8px 0 6px; line-height: 1.15;
  background: linear-gradient(90deg,#e0f2fe,#67e8f9,#c4b5fd); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { color: #b6c2d9; margin: 0; max-width: 980px; font-size: .95rem; }
.badge { display: inline-block; font-size: .7rem; letter-spacing: .08em; text-transform: uppercase; color: #67e8f9;
  border: 1px solid rgba(103,232,249,.35); padding: 3px 10px; border-radius: 999px; background: rgba(103,232,249,.08); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 2px 0 10px; }
.chips span { font-size: .75rem; color: #cbd5e1; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08);
  padding: 3px 10px; border-radius: 999px; }
.chips span b { color: #67e8f9; font-weight: 600; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(128px, 1fr)); gap: 10px; margin: 12px 0 8px; }
.kpi { background: linear-gradient(160deg, rgba(255,255,255,.065), rgba(255,255,255,.02));
  border: 1px solid rgba(255,255,255,.08); border-radius: 14px; padding: 10px 14px;
  transition: transform .15s ease, border-color .15s ease; }
.kpi:hover { transform: translateY(-2px); border-color: rgba(34,211,238,.5); }
.kpi .l { font-size: .68rem; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
.kpi .v { font-family: 'Outfit', sans-serif; font-size: 1.45rem; font-weight: 700; color: #f1f5f9; line-height: 1.25; }
.kpi .s { font-size: .7rem; color: #64748b; }
.kpi.c0 .v { color: #22d3ee; } .kpi.c1 .v { color: #fb923c; } .kpi.c2 .v { color: #c4b5fd; }
.side-h { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: .95rem; color: #e2e8f0;
  margin: 18px 0 6px; display: flex; gap: 8px; align-items: center; }
.side-h .n { background: linear-gradient(135deg,#22d3ee,#a78bfa); color: #0b1020; border-radius: 6px;
  width: 21px; height: 21px; display: inline-flex; align-items: center; justify-content: center; font-size: .75rem; }
.brand { font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 800; color: #f1f5f9; }
.brand small { display: block; font-family: 'Inter'; font-weight: 400; font-size: .72rem; color: #94a3b8; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background: rgba(255,255,255,.04); border-radius: 10px 10px 0 0; padding: 8px 18px; }
.stTabs [aria-selected="true"] { background: linear-gradient(180deg, rgba(34,211,238,.2), rgba(34,211,238,.03)); }
.note { font-size: .8rem; color: #94a3b8; }
.footer { text-align: center; color: #64748b; font-size: .75rem; margin-top: 28px; }
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
