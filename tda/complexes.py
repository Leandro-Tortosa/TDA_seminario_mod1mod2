"""Construcción de complejos simpliciales (Alpha, Flag, Vietoris–Rips) con GUDHI.

Convención de escala (común a los tres complejos, en metros):
    α = distancia máxima entre vértices de un símplex.
    * Vietoris–Rips: arista si d(u, v) ≤ α  (bolas de radio α/2 que se cortan dos a dos).
    * Alpha complex: bolas de radio α/2 truncadas por las celdas de Voronoi
      (GUDHI usa α² = radio², por eso valor = 2·√filtración).
    * Flag (clique): grafo primario (calles OSM o triangulación de Delaunay para
      nubes de puntos) restringido a aristas de longitud ≤ α y relleno de cliques.

El resultado es un diccionario de arrays que sirve para dibujar, filtrar y
calcular homología sin volver a construir el complejo.
"""
from __future__ import annotations

import gudhi
import numpy as np
from scipy.spatial import Delaunay, cKDTree

KINDS = {
    "alpha": "Alpha complejo",
    "flag": "Complejo Flag (clique)",
    "rips": "Vietoris–Rips",
}

MAX_TRIANGLES = 350_000  # protección frente a la explosión combinatoria


def _extract(st: gudhi.SimplexTree):
    E, fE, T, fT = [], [], [], []
    for s, f in st.get_simplices():
        k = len(s)
        if k == 2:
            E.append(s); fE.append(f)
        elif k == 3:
            T.append(s); fT.append(f)
    E = np.asarray(E, dtype=np.int64).reshape(-1, 2)
    T = np.asarray(T, dtype=np.int64).reshape(-1, 3)
    return E, np.asarray(fE, float), T, np.asarray(fT, float)


def _triangles_by_expansion(n, E, fE, warnings):
    """Triángulos del complejo clique (flag) del 1-esqueleto (E, fE)."""
    if len(E) == 0:
        return np.empty((0, 3), np.int64), np.empty(0)
    deg = np.bincount(E.ravel(), minlength=n).astype(float)
    bound = float((deg * (deg - 1) / 2).sum() / 3)
    if bound > MAX_TRIANGLES * 1.6:
        warnings.append(
            f"Se omiten los 2-símplices: el complejo tendría del orden de "
            f"{bound:,.0f} triángulos (explosión combinatoria). Reduzca α o use "
            f"el Alpha complejo.")
        return np.empty((0, 3), np.int64), np.empty(0)
    st = gudhi.SimplexTree()
    st.insert_batch(np.arange(n, dtype=np.int64)[None, :], np.zeros(n))
    st.insert_batch(E.T.copy(), fE)
    st.expansion(2)
    _, _, T, fT = _extract(st)
    return T, fT


def build_complex(x, y, kind: str, alpha: float,
                  graph_edges=None, graph_len=None) -> dict:
    pts = np.column_stack([x, y]).astype(float)
    n = len(pts)
    warnings: list[str] = []
    base = None

    if kind == "alpha":
        st = gudhi.AlphaComplex(points=pts).create_simplex_tree(
            max_alpha_square=(alpha / 2.0) ** 2)
        E, fE, T, fT = _extract(st)
        fE = 2.0 * np.sqrt(np.maximum(fE, 0.0))
        fT = 2.0 * np.sqrt(np.maximum(fT, 0.0))
        Elen = np.hypot(*(pts[E[:, 0]] - pts[E[:, 1]]).T) if len(E) else np.empty(0)
        base = "Triangulación de Delaunay ∩ bolas de radio α/2"

    elif kind == "rips":
        tree = cKDTree(pts)
        E = tree.query_pairs(r=alpha, output_type="ndarray").astype(np.int64)
        E.sort(axis=1)
        Elen = np.hypot(*(pts[E[:, 0]] - pts[E[:, 1]]).T) if len(E) else np.empty(0)
        fE = Elen.copy()
        T, fT = _triangles_by_expansion(n, E, fE, warnings)
        base = "Distancia euclídea entre pares de puntos"

    elif kind == "flag":
        if graph_edges is not None and len(graph_edges):
            E0, L0 = np.asarray(graph_edges), np.asarray(graph_len, float)
            base = "Grafo primario de calles (longitud real del tramo)"
        else:
            tri = Delaunay(pts)
            s = tri.simplices
            E0 = np.vstack([s[:, [0, 1]], s[:, [1, 2]], s[:, [0, 2]]])
            E0.sort(axis=1)
            E0 = np.unique(E0, axis=0)
            L0 = np.hypot(*(pts[E0[:, 0]] - pts[E0[:, 1]]).T)
            base = "Grafo de Delaunay de la nube de puntos"
        keep = L0 <= alpha
        E, Elen = E0[keep].astype(np.int64), L0[keep]
        fE = Elen.copy()
        T, fT = _triangles_by_expansion(n, E, fE, warnings)
    else:
        raise ValueError(kind)

    return dict(kind=kind, alpha=float(alpha), n=n, E=E, fE=fE, Elen=Elen,
                T=T, fT=fT, warnings=warnings, base=base)


def euler_characteristic(n_v: int, n_e: int, n_t: int) -> int:
    return int(n_v - n_e + n_t)
