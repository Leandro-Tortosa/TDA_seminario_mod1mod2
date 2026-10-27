"""Pestañas 1 (complejo simplicial) y 2 (filtraciones) + utilidades compartidas."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from . import centrality as tcen
from . import homology as th
from . import maps as tm
from . import plots as tp
from . import ui
from .complexes import KINDS

MAP_HEIGHT = 760  # el mapa se ajusta a 4:3 dentro de esta altura


# --------------------------------------------------------------------------- #
# Cachés compartidas
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False, max_entries=24)
def _map_html(key, _builder):
    return _builder()


def show_map(key, builder):
    components.html(_map_html(key, builder), height=MAP_HEIGHT, scrolling=False)


def filtration(ctx, mode):
    """mode: 'dist' | 'bc_desc' | 'bc_asc' → (fV, fE, fT, cap, unit)."""
    cx, bc = ctx["cx"], ctx["bc"]
    if mode == "dist":
        return np.zeros(cx["n"]), cx["fE"], cx["fT"], ctx["alpha"], "m"
    g = bc / bc.max() if bc.max() > 0 else np.zeros_like(bc)
    fV = g if mode == "bc_asc" else 1.0 - g
    fE, fT = th.lower_star_values(fV, cx["E"], cx["T"])
    return fV, fE, fT, 1.0, "t"


@st.cache_resource(show_spinner=False, max_entries=24)
def _persistence(key, _n, _E, _fE, _T, _fT, _fV):
    return th.persistence(_n, _E, _fE, _T, _fT, _fV)


def get_persistence(ctx, mode):
    fV, fE, fT, cap, unit = filtration(ctx, mode)
    cx = ctx["cx"]
    key = f"{ctx['bc_key'] if mode != 'dist' else ctx['cx_key']}|{mode}"
    return _persistence(key, cx["n"], cx["E"], fE, cx["T"], fT, fV), cap, unit


def edge_tri_values(v, E, T):
    vE = v[E].mean(axis=1) if len(E) else np.empty(0)
    vT = v[T].mean(axis=1) if len(T) else np.empty(0)
    return vE, vT


# --------------------------------------------------------------------------- #
# PESTAÑA 1 · Complejo simplicial
# --------------------------------------------------------------------------- #
def render_complex_tab(ctx):
    d, cx, bc = ctx["d"], ctx["cx"], ctx["bc"]
    n, E, T = cx["n"], cx["E"], cx["T"]

    def build():
        scale = tm.ColorScale(bc, ctx["cmap"], ctx["scale_mode"], "Centralidad betweenness",
                              fmt="{:.3f}")
        mb = tm.MapBuilder(d["lon"], d["lat"], ctx["basemap"], center=d["center"])
        if d["radius"]:
            mb.add_area(d["center"], d["radius"])
        mb.add_streets(d["streets"])
        vE, vT = edge_tri_values(bc, E, T)
        mb.add_complex(np.arange(n), E, T, bc, vE, vT, scale, ctx["node_size"],
                       "Betweenness", "{:.4f}", d["labels"])
        mb.add_legend(scale)
        return mb.html()

    key = f"t1|{ctx['bc_key']}|{ctx['basemap']}|{ctx['cmap']}|{ctx['scale_mode']}|{ctx['node_size']}"
    show_map(key, build)

    pers, cap, _ = get_persistence(ctx, "dist")
    b0 = th.betti_at(pers["dgms"][0], cap)
    b1 = th.betti_at(pers["dgms"][1], cap)
    b2 = th.betti_at(pers["dgms"][2], cap)
    chi = n - len(E) + len(T)
    st_ = tcen.graph_stats(n, np.ones(n, bool), E)
    st.markdown(ui.kpis([
        ("0-símplices", ui.fmt_int(n), "vértices", ""),
        ("1-símplices", ui.fmt_int(len(E)), "aristas", ""),
        ("2-símplices", ui.fmt_int(len(T)), "triángulos", ""),
        ("χ = V − E + F", ui.fmt_int(chi), f"β₀ − β₁ + β₂ = {b0 - b1 + b2}", ""),
        ("β₀", ui.fmt_int(b0), "componentes conexas", "c0"),
        ("β₁", ui.fmt_int(b1), "agujeros / ciclos", "c1"),
        ("Grado medio", f"{st_['mean_deg']:.2f}", f"gigante: {100 * st_['giant']:.0f} %", ""),
        ("Betweenness máx.", f"{bc.max():.3f}", f"media {bc.mean():.4f}", "c2"),
    ]), unsafe_allow_html=True)
    if b2:
        st.caption(f"β₂ = {b2}: el 2-esqueleto de {KINDS[ctx['kind']]} contiene tetraedros «huecos» "
                   "(4-cliques sin 3-símplex); por eso χ incluye β₂.")

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.plotly_chart(tp.histogram(bc, "Distribución de la betweenness (escala log)",
                                     "Betweenness normalizada"), use_container_width=True)
    with c2:
        deg = np.bincount(E.ravel(), minlength=n) if len(E) else np.zeros(n, int)
        top = np.argsort(-bc)[:10]
        df = pd.DataFrame({"vértice": top, "betweenness": bc[top].round(4), "grado": deg[top],
                           "lat": d["lat"][top].round(5), "lon": d["lon"][top].round(5)})
        if d["labels"] is not None:
            df.insert(1, "nombre", [d["labels"][i] for i in top])
        st.markdown("**Top 10 vértices por betweenness**")
        st.dataframe(df, hide_index=True, use_container_width=True, height=300)

    with st.expander("📘 Conceptos del Módulo 1 · ¿qué estoy viendo?"):
        st.markdown(f"""
- **k-símplex**: 0-símplex = punto (intersección o establecimiento), 1-símplex = arista,
  2-símplex = triángulo. Un **complejo simplicial** es una colección de símplices cerrada por caras.
- **Complejo actual: {KINDS[ctx['kind']]}** — base: *{cx['base']}*.
  - *Alpha complejo*: nervio de las bolas de radio α/2 recortadas por las celdas de Voronoi;
    es un subcomplejo de la triangulación de Delaunay (≤ 2n − 5 triángulos en 2D) y tiene el
    mismo tipo de homotopía que la unión de bolas (Teorema del Nervio).
  - *Vietoris–Rips*: un símplex por cada conjunto de puntos a distancia ≤ α dos a dos; muy
    sencillo pero sufre **explosión combinatoria**.
  - *Flag (clique)*: se parte del **grafo primario** (calles de OSM, con su longitud real) y se
    rellenan los cliques; en redes urbanas casi no hay triángulos («degeneración por grado nodal»).
- **Betweenness** de un vértice v: fracción de caminos mínimos (ponderados por longitud) entre
  pares de vértices que pasan por v, calculada sobre el grafo (0-símplices, 1-símplices).
  Aristas y triángulos se colorean con la media de sus vértices.
- **Característica de Euler**: χ = V − E + F = β₀ − β₁ (+ β₂).
""")


# --------------------------------------------------------------------------- #
# PESTAÑA 2 · Filtraciones
# --------------------------------------------------------------------------- #
FILT_OPTIONS = {"dist": "📏 Distancia (m)", "bc_desc": "⭐ Betweenness (más centrales primero)",
                "bc_asc": "🔻 Betweenness (menos centrales primero)"}


def render_filtration_tab(ctx):
    d, cx, bc, alpha = ctx["d"], ctx["cx"], ctx["bc"], ctx["alpha"]
    n, E, T = cx["n"], cx["E"], cx["T"]

    c1, c2, c3 = st.columns([1.25, 1.6, 1.1])
    mode = c1.radio("Variable de filtración", list(FILT_OPTIONS), format_func=FILT_OPTIONS.get,
                    key="f_mode")
    fV, fE, fT, cap, unit = filtration(ctx, mode)
    if mode == "dist":
        t = c2.slider("Umbral de distancia ε (m)", 0.0, alpha, round(alpha * 0.6, 1),
                      max(0.5, round(alpha / 200, 1)), key=f"eps_{alpha}")
        c2.caption("K_ε contiene los símplices cuyo valor de filtración (diámetro / α del "
                   "símplex) es ≤ ε. Todos los vértices están presentes desde ε = 0.")
    else:
        t = c2.slider("Nivel de filtración t", 0.0, 1.0, 0.5, 0.01, key=f"t_{mode}")
        cond = (f"c̃(v) ≥ {1 - t:.2f}" if mode == "bc_desc" else f"c̃(v) ≤ {t:.2f}")
        c2.caption(f"Filtración *lower-star*: entran los vértices con **{cond}** "
                   "(c̃ = betweenness / máx.) y cada símplex entra con el máximo de sus vértices.")
    color_by = c3.selectbox("Colorear por", ["Valor de filtración", "Centralidad betweenness"],
                            key="f_color")
    show_h1 = c3.checkbox("Mostrar agujeros H₁ vivos en el umbral", value=True, key="f_h1")

    mV, mE, mT = fV <= t, fE <= t, fT <= t
    V_idx = np.flatnonzero(mV)
    Et, Tt = E[mE], T[mT]
    pers, _, _ = get_persistence(ctx, mode)

    def build():
        if color_by == "Valor de filtración":
            if mode == "dist":
                vcon = np.full(n, np.inf)
                if len(E):
                    np.minimum.at(vcon, E[:, 0], fE)
                    np.minimum.at(vcon, E[:, 1], fE)
                vcon[~np.isfinite(vcon)] = alpha
                vV, title, fmt = vcon, "Valor de filtración ε (m)", "{:.0f}"
            else:
                vV, title, fmt = fV, "Nivel de filtración t", "{:.2f}"
            scale = tm.ColorScale(np.r_[vV, fE, 0, cap], ctx["cmap"], ctx["scale_mode"], title,
                                  fmt=fmt, vmin=0.0, vmax=cap)
            vE, vT = fE[mE], fT[mT]
        else:
            vV = bc
            scale = tm.ColorScale(bc, ctx["cmap"], ctx["scale_mode"], "Centralidad betweenness",
                                  fmt="{:.3f}")
            vE, vT = edge_tri_values(bc, Et, Tt)
        mb = tm.MapBuilder(d["lon"], d["lat"], ctx["basemap"], center=d["center"])
        if d["radius"]:
            mb.add_area(d["center"], d["radius"])
        mb.add_streets(d["streets"], show=False)
        mb.add_ghost(E, T, show=True)
        mb.add_complex(V_idx, Et, Tt, vV[V_idx], vE, vT, scale, ctx["node_size"],
                       title if color_by == "Valor de filtración" else "Betweenness",
                       "{:.3f}", d["labels"])
        if show_h1:
            alive = [g for g in pers["h1"] if g[0] <= t < g[1]]
            mb.add_h1(alive, cap, unit if unit == "m" else "", "{:.1f}" if unit == "m" else "{:.2f}",
                      max_n=20, name="Agujeros H₁ vivos")
        mb.add_legend(scale)
        return mb.html()

    key = (f"t2|{ctx['bc_key']}|{mode}|{t}|{color_by}|{show_h1}|{ctx['basemap']}|{ctx['cmap']}|"
           f"{ctx['scale_mode']}|{ctx['node_size']}")
    show_map(key, build)

    b0, b1 = th.betti_at(pers["dgms"][0], t), th.betti_at(pers["dgms"][1], t)
    gs = tcen.graph_stats(n, mV, Et)
    st.markdown(ui.kpis([
        ("Vértices activos", ui.fmt_int(len(V_idx)), f"de {ui.fmt_int(n)}", ""),
        ("Aristas", ui.fmt_int(len(Et)), f"de {ui.fmt_int(len(E))}", ""),
        ("Triángulos", ui.fmt_int(len(Tt)), f"de {ui.fmt_int(len(T))}", ""),
        ("β₀", ui.fmt_int(b0), "componentes conexas", "c0"),
        ("β₁", ui.fmt_int(b1), "agujeros vivos", "c1"),
        ("χ", ui.fmt_int(len(V_idx) - len(Et) + len(Tt)), "V − E + F", ""),
        ("Componente gigante", f"{100 * gs['giant']:.0f} %", "de los vértices activos", "c2"),
        ("Grado medio", f"{gs['mean_deg']:.2f}", "del 1-esqueleto", ""),
    ]), unsafe_allow_html=True)

    grid = np.linspace(0, cap, 300)
    curves = {k: th.betti_curve(pers["dgms"][k], grid) for k in (0, 1)}
    st.plotly_chart(tp.betti_curves(grid, curves, unit, threshold=t,
                                    title="Curvas de Betti a lo largo de la filtración"),
                    use_container_width=True)

    with st.expander("📘 Conceptos del Módulo 2 · filtraciones"):
        st.markdown("""
- Una **filtración** es una sucesión anidada de complejos K₀ ⊆ K₁ ⊆ … ⊆ Kₙ = K_α.
- **Por distancia**: cada símplex entra cuando la escala alcanza su valor (longitud de la arista
  en Rips/Flag, 2·radio alpha en el Alpha complejo). Al crecer ε las componentes se fusionan
  (β₀ ↓) y aparecen y se rellenan ciclos (β₁).
- **Por betweenness** (*lower-star*): f(v) = centralidad normalizada; un símplex entra con el
  máximo de sus vértices. En orden *descendente* se construye primero el «esqueleto» de los
  corredores más centrales y después se añaden las calles locales.
- Los **agujeros H₁ vivos** marcan con línea discontinua la arista que cierra el ciclo y, en rojo,
  el triángulo que lo rellenará más adelante (aproxima el centro del «vacío»).
""")


# --------------------------------------------------------------------------- #
# PESTAÑA 3 · Homología persistente
# --------------------------------------------------------------------------- #
def render_homology_tab(ctx):
    cx = ctx["cx"]

    st.markdown("### 📊 Firma topológica y Homología persistente")
    st.caption("Estudio multiescala de componentes conexas (H₀) y ciclos/agujeros (H₁) mediante diagramas "
               "de persistencia, códigos de barras y entropía persistente.")

    c1, c2 = st.columns([1.5, 2.5])
    filt_choice = c1.selectbox(
        "Filtración a analizar",
        list(FILT_OPTIONS),
        format_func=FILT_OPTIONS.get,
        key="h_mode"
    )
    barcode_top = c2.slider("Nº máximo de intervalos en el código de barras", 10, 150, 50, 5, key="bc_top")

    pers, cap, unit = get_persistence(ctx, filt_choice)
    dgms = pers["dgms"]
    h1_gens = pers["h1"]

    n_h0 = len(dgms[0])
    n_h1 = len(dgms[1])
    n_h2 = len(dgms[2]) if 2 in dgms else 0

    ent_0 = th.persistent_entropy(dgms[0])
    ent_1 = th.persistent_entropy(dgms[1])

    max_p1 = 0.0
    if n_h1 > 0:
        fin_h1 = dgms[1][np.isfinite(dgms[1][:, 1])]
        if len(fin_h1) > 0:
            max_p1 = float(np.max(fin_h1[:, 1] - fin_h1[:, 0]))

    st.markdown(ui.kpis([
        ("Clases H₀", ui.fmt_int(n_h0), "nacimiento componentes", "c0"),
        ("Clases H₁", ui.fmt_int(n_h1), "ciclos formados", "c1"),
        ("Clases H₂", ui.fmt_int(n_h2), "cavidades 3D", "c2"),
        ("Persistencia H₁ máx.", f"{max_p1:.1f} {unit}", "mayor agujero cerrado", ""),
        ("Entropía H₀", f"{ent_0:.2f}", "dispersión de clusters", ""),
        ("Entropía H₁", f"{ent_1:.2f}", "complejidad de ciclos", ""),
    ]), unsafe_allow_html=True)

    # Gráficos interactivos en dos columnas
    col_diag, col_bar = st.columns(2)
    with col_diag:
        fig_diag = tp.persistence_diagram(dgms, cap, unit)
        st.plotly_chart(fig_diag, use_container_width=True)

    with col_bar:
        fig_bar = tp.barcode(dgms, cap, unit, top_n=barcode_top)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Detalle de los ciclos H1 más persistentes y tabla
    st.markdown("#### 🔍 Ciclos y agujeros H₁ más relevantes (Señal vs. Ruido)")
    if n_h1 > 0:
        rows = []
        for rank, item in enumerate(h1_gens[:15], 1):
            b, d, edge, tri = item
            pers_val = (d - b) if np.isfinite(d) else np.inf
            d_str = f"{d:.2f}" if np.isfinite(d) else "∞"
            p_str = f"{pers_val:.2f}" if np.isfinite(pers_val) else "∞ (esencial)"
            tri_str = f"{tri}" if tri else "Abierto (no se rellena)"
            rows.append({
                "Ranking": f"#{rank}",
                f"Nacimiento ({unit})": round(b, 2),
                f"Muerte ({unit})": d_str,
                f"Persistencia ({unit})": p_str,
                "Arista generadora": f"{edge}",
                "Triángulo relleno": tri_str,
                "Tipo": "Señal topológica" if (np.isinf(pers_val) or pers_val > 0.25 * cap) else "Ruido / manzana"
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        st.info("No se formaron ciclos H₁ unidimensionales en el rango de filtración evaluado.")

    # Comparación de estabilidad y distancia Bottleneck
    with st.expander("⚖️ Estabilidad y Distancia de Bottleneck (Módulo 2.1)"):
        st.markdown("""
        El **Teorema de Estabilidad** garantiza que pequeñas perturbaciones métricas no alteran drásticamente el
        diagrama de persistencia. La **distancia de Bottleneck** ($d_B$) mide la distancia máxima necesaria para
        emparejar las firmas topológicas (incluyendo proyecciones ortogonales a la diagonal $y=x$).
        """)
        c_b1, c_b2 = st.columns(2)
        with c_b1:
            st.markdown("**Comparativa con Filtración por Distancia vs. Betweenness**")
            p_dist, cap_dist, _ = get_persistence(ctx, "dist")
            p_bc, cap_bc, _ = get_persistence(ctx, "bc_desc")
            if len(p_dist["dgms"][1]) > 0 and len(p_bc["dgms"][1]) > 0:
                # Normalizar escalas para cálculo de bottleneck relativo
                d1_norm = p_dist["dgms"][1] / cap_dist
                d2_norm = p_bc["dgms"][1] / cap_bc
                db_h1 = th.bottleneck(d1_norm, d2_norm, cap=1.0)
                st.metric("Distancia Bottleneck relativa en H₁ (d_B)", f"{db_h1:.4f}")
                st.caption("Compara la firma multiescala métrica con la estructura xerárquica de centralidad.")
            else:
                st.caption("Se requieren clases H₁ en ambas filtraciones para calcular el emparejamiento.")

        with c_b2:
            st.markdown("**Interpretación didáctica**")
            st.markdown("""
            - Puntos **cerca de la diagonal** ($d - b \\approx 0$): fluctuaciones locales, pequeñas manzanas de la red o ruido de medición.
            - Puntos **lejos de la diagonal** ($d - b \\gg 0$): rasgos estructurales persistentes (grandes vacíos urbanos, cerros, ríos o desiertos de servicio).
            """)

    with st.expander("📘 Conceptos del Módulo 2 · homología persistente"):
        st.markdown(r"""
- **Homología simplicial**: detecta características topológicas invariantes:
  - $\beta_0$ = rango de $H_0$: cuenta el número de **componentes conexas**.
  - $\beta_1$ = rango de $H_1$: cuenta el número de **ciclos o lazos independientes** (vacíos rodeados de datos).
  - $\beta_2$ = rango de $H_2$: cuenta las **cavidades tridimensionales**.
- **Diagrama de Persistencia**: cada par $(b_i, d_i)$ representa una característica topológica que nace en la escala $b_i$ y muere en la escala $d_i$.
- **Código de Barras**: representación equivalente mediante intervalos horizontales $[b_i, d_i)$. La longitud de la barra $d_i - b_i$ mide la robustez o persistencia del rasgo.
- **Entropía persistente**: $E = -\sum p_i \log p_i$, donde $p_i = \frac{l_i}{\sum l_k}$. Mide la uniformidad en la duración de las características.
""")

