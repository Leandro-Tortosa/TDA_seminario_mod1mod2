"""App 1 · Seminario TDA (UP) — Módulos 1 y 2.

Complejos simpliciales (Alpha, Flag, Vietoris–Rips) sobre la red urbana de Lima
(OSMnx) o una nube de puntos CSV, centralidad betweenness, filtraciones por
distancia y por centralidad, y homología persistente (GUDHI).

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import streamlit as st

from tda import centrality as tcen
from tda import complexes as tcx
from tda import data as tdata
from tda import homology as th
from tda import maps as tm
from tda import tabs, ui

ROOT = Path(__file__).parent
SAMPLE_CSV = ROOT / "data" / "ejemplo_establecimientos_lima.csv"

st.set_page_config(
    page_title="TDA Lima · Complejos simpliciales y homología persistente",
    page_icon="🕸️", layout="wide", initial_sidebar_state="expanded",
    menu_items={"About": "Seminario de Análisis Topológico de Datos · Universidad del Pacífico"},
)
st.markdown(ui.CSS, unsafe_allow_html=True)

PRESETS = {
    "Plaza Mayor · Cercado de Lima": (-12.04637, -77.03019),
    "Universidad del Pacífico · Jesús María": (-12.08430, -77.04970),
    "Parque Kennedy · Miraflores": (-12.12110, -77.02970),
    "Centro financiero · San Isidro": (-12.09500, -77.02700),
    "Gamarra · La Victoria": (-12.06800, -77.01350),
    "Plaza de Armas · Barranco": (-12.14900, -77.02150),
    "Personalizado": None,
}


# --------------------------------------------------------------------------- #
# Cachés: cada etapa costosa se calcula una sola vez por combinación de parámetros
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False, max_entries=6, ttl=6 * 3600)
def load_osm(lat, lon, radius, net, cons):
    return tdata.download_osm_network(lat, lon, radius, net, cons)


@st.cache_resource(show_spinner=False, max_entries=6)
def load_csv(raw: bytes):
    return tdata.parse_points_csv(raw)


@st.cache_resource(show_spinner=False, max_entries=12)
def get_complex(data_key, kind, alpha, _d):
    return tcx.build_complex(_d["x"], _d["y"], kind, alpha, _d["graph_edges"], _d["graph_len"])


@st.cache_resource(show_spinner=False, max_entries=12)
def get_betweenness(cx_key, k, _cx):
    return tcen.betweenness(_cx["n"], _cx["E"], _cx["Elen"], k)


# --------------------------------------------------------------------------- #
# Panel lateral
# --------------------------------------------------------------------------- #
def _apply_preset():
    p = PRESETS.get(st.session_state.preset)
    if p:
        st.session_state.lat, st.session_state.lon = p


if "lat" not in st.session_state:
    st.session_state.lat, st.session_state.lon = PRESETS["Plaza Mayor · Cercado de Lima"]

with st.sidebar:
    st.markdown("<div class='brand'>🕸️ TDA · Lima<small>Seminario UP · Módulos 1 y 2</small></div>",
                unsafe_allow_html=True)

    st.markdown(ui.side_header(1, "Datos y red urbana"), unsafe_allow_html=True)
    source = st.radio("Fuente de datos", ["Red urbana (OpenStreetMap)", "Dataset CSV propio",
                                          "Dataset de ejemplo (sintético)"], key="source",
                      label_visibility="collapsed")
    if source.startswith("Red urbana"):
        st.selectbox("📍 Ubicación de referencia", list(PRESETS), key="preset",
                     on_change=_apply_preset)
        with st.form("osm_form", border=False):
            c1, c2 = st.columns(2)
            c1.number_input("Latitud", key="lat", min_value=-90.0, max_value=90.0,
                            step=0.0005, format="%.5f")
            c2.number_input("Longitud", key="lon", min_value=-180.0, max_value=180.0,
                            step=0.0005, format="%.5f")
            radius = st.slider("Radio r (m)", 300, 5000, 600, 50, key="radius",
                               help="Radio del círculo de red que se descarga de OpenStreetMap.")
            net = st.selectbox("Tipo de red OSM", list(tdata.NETWORK_TYPES), key="net",
                               format_func=tdata.NETWORK_TYPES.get)
            cons = st.slider("Consolidación de nodos (m)", 0, 50, 10, 1, key="cons",
                             help="Las intersecciones a menos de esta distancia se funden en un "
                                  "único nodo (simplifica glorietas y cruces dobles). 0 = sin consolidar.")
            go = st.form_submit_button("🌐 Descargar / actualizar red", type="primary",
                                       use_container_width=True)
        if go or "osm_params" not in st.session_state:
            st.session_state.osm_params = (round(st.session_state.lat, 6),
                                           round(st.session_state.lon, 6), radius, net, cons)
        if radius > 1000:
            st.caption("ℹ️ Un radio > 1.000 m abarca hasta 9 km² de trama urbana en Lima con miles de calles. Si el servidor público de OpenStreetMap tarda o rechaza la consulta, usa un radio de 500 a 800 m para una respuesta instantánea.")
        uploaded = None
    elif source.startswith("Dataset CSV"):
        uploaded = st.file_uploader("CSV con columnas lon/longitud y lat/latitud", type=["csv", "txt"],
                                    help="Separador ',' o ';'. Se admite coma decimal.")
    else:
        uploaded = None
        st.caption("Establecimientos de salud sintéticos en Lima Centro: núcleo denso, dos "
                   "anillos con «desiertos de cobertura» y puntos dispersos.")
    if not source.startswith("Red urbana"):
        st.download_button("⬇️ Descargar CSV de ejemplo", SAMPLE_CSV.read_bytes(),
                           file_name=SAMPLE_CSV.name, mime="text/csv", use_container_width=True)

    st.markdown(ui.side_header(2, "Cálculo y rendimiento"), unsafe_allow_html=True)
    sampling = st.checkbox("Aproximación por muestreo (k-fuentes)", value=True, key="sampling",
                           help="Betweenness aproximada de Brandes con k nodos fuente aleatorios.")
    k_src = st.slider("Número de nodos fuente (k)", 10, 200, 50, 5, key="k_src", disabled=not sampling)

    st.markdown(ui.side_header(3, "Visualización cartográfica"), unsafe_allow_html=True)
    basemap = st.selectbox("Mapa base", list(tm.BASEMAPS), key="basemap")
    cmap = st.selectbox("Paleta de color", tm.COLORMAPS, key="cmap")
    scale_mode = st.radio("Escala de color", ["Cuantiles", "Lineal"], horizontal=True, key="scale",
                          help="Por cuantiles reparte los colores de forma uniforme aunque la "
                               "betweenness sea muy asimétrica.")
    node_size = st.slider("Tamaño de los vértices", 1.0, 8.0, 3.5, 0.5, key="node_size")

    st.markdown(ui.side_header(4, "Complejo simplicial"), unsafe_allow_html=True)
    kind = st.radio("Tipo de complejo", list(tcx.KINDS), format_func=tcx.KINDS.get, key="kind")
    is_osm = source.startswith("Red urbana")
    alpha = st.slider("Parámetro α (m)", 10, 1500, 160 if is_osm else 300, 5,
                      key=f"alpha_{'osm' if is_osm else 'pts'}",
                      help="Distancia máxima entre los vértices de un símplex "
                           "(equivale a bolas de radio α/2).")

# --------------------------------------------------------------------------- #
# Carga de datos y cálculo
# --------------------------------------------------------------------------- #
st.markdown(
    "<div class='hero'><span class='badge'>Seminario TDA · Universidad del Pacífico · Módulos 1 y 2</span>"
    "<h1>Complejos simpliciales y homología persistente en Lima</h1>"
    "<p>Del grafo urbano de OpenStreetMap (o de tu propia nube de puntos) a los complejos "
    "Alpha, Flag y Vietoris–Rips, su centralidad <i>betweenness</i>, sus filtraciones y sus "
    "firmas topológicas: números de Betti, diagramas de persistencia y códigos de barras.</p></div>",
    unsafe_allow_html=True)

try:
    if is_osm:
        lat, lon, radius, net, cons = st.session_state.osm_params
        with st.spinner(f"Descargando la red «{net}» de OpenStreetMap (r = {radius} m)…"):
            d = load_osm(lat, lon, radius, net, cons)
    elif source.startswith("Dataset CSV"):
        if uploaded is None:
            st.info("⬅️ Sube un archivo CSV en el panel lateral (o usa el dataset de ejemplo).")
            st.stop()
        d = load_csv(uploaded.getvalue())
    else:
        d = load_csv(SAMPLE_CSV.read_bytes())
except Exception as exc:  # noqa: BLE001
    st.error(f"No se pudieron cargar los datos: {exc}")
    st.stop()

cx_key = f"{d['key']}|{kind}|{alpha}"
with st.spinner("Construyendo el complejo simplicial…"):
    cx = get_complex(d["key"], kind, float(alpha), d)
k_eff = k_src if sampling else None
bc_key = f"{cx_key}|k={k_eff}"
with st.spinner("Calculando la centralidad betweenness…"):
    bc = get_betweenness(cx_key, k_eff, cx)

for w in cx["warnings"]:
    st.warning(w)

ctx = dict(d=d, cx=cx, bc=bc, cx_key=cx_key, bc_key=bc_key, kind=kind, alpha=float(alpha),
           basemap=basemap, cmap=cmap, scale_mode="quantile" if scale_mode == "Cuantiles" else "linear",
           node_size=node_size, is_osm=is_osm, k_eff=k_eff)

meta = d["meta"]
if is_osm:
    info = [("Fuente", "OpenStreetMap"), ("Red", meta["network_type"]),
            ("Nodos OSM", ui.fmt_int(meta["n_raw"])),
            ("Tras consolidar", ui.fmt_int(meta["n_nodes"])),
            ("Tramos de calle", ui.fmt_int(meta["n_edges"]))]
else:
    info = [("Fuente", "CSV"), ("Columnas", f"{meta['lon_col']} / {meta['lat_col']}"),
            ("Separador", meta["sep"]), ("Puntos", ui.fmt_int(meta["n_points"]))]
    if meta["n_invalid"] or meta["n_dup"] or meta["n_sub"]:
        info.append(("Descartados", f"{meta['n_invalid']} inválidos · {meta['n_dup']} duplicados"
                                    f" · {meta['n_sub']} por submuestreo"))
info += [("Complejo", tcx.KINDS[kind]), ("α", f"{alpha} m"),
         ("Betweenness", f"k = {k_eff}" if k_eff else "exacta")]
st.markdown(ui.chips(info), unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🗺️ Complejo simplicial", "🎚️ Filtraciones", "📊 Homología persistente"])
with t1:
    tabs.render_complex_tab(ctx)
with t2:
    tabs.render_filtration_tab(ctx)
with t3:
    tabs.render_homology_tab(ctx)

st.markdown("<div class='footer'>Análisis Topológico de Datos y aplicaciones en Perú · "
            "OSMnx · GUDHI · NetworkX · Folium · Streamlit</div>", unsafe_allow_html=True)
