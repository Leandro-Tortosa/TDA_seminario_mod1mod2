"""Filtraciones y homología persistente (GUDHI)."""
from __future__ import annotations

import gudhi
import numpy as np


def simplex_tree(n, E, fE, T, fT, fV=None) -> gudhi.SimplexTree:
    st = gudhi.SimplexTree()
    fV = np.zeros(n) if fV is None else np.asarray(fV, float)
    st.insert_batch(np.arange(n, dtype=np.int64)[None, :], fV)
    if len(E):
        st.insert_batch(np.ascontiguousarray(E.T), np.asarray(fE, float))
    if len(T):
        st.insert_batch(np.ascontiguousarray(T.T), np.asarray(fT, float))
    st.make_filtration_non_decreasing()
    return st


def lower_star_values(fV, E, T):
    """Filtración 'lower-star': cada símplex entra con el máximo de sus vértices."""
    fE = fV[E].max(axis=1) if len(E) else np.empty(0)
    fT = fV[T].max(axis=1) if len(T) else np.empty(0)
    return fE, fT


def persistence(n, E, fE, T, fT, fV=None) -> dict:
    """Intervalos de persistencia H0, H1 (y H2) + generadores de H1.

    Para cada clase de H1 se guarda la arista que la crea y el triángulo que la
    rellena (si muere): permiten localizar el 'agujero' en el mapa.
    """
    st = simplex_tree(n, E, fE, T, fT, fV)
    st.compute_persistence(homology_coeff_field=2, persistence_dim_max=True)
    rows = {0: [], 1: [], 2: []}
    h1 = []
    for b, d in st.persistence_pairs():
        dim = len(b) - 1
        if dim > 2:
            continue
        fb = st.filtration(b)
        fd = st.filtration(d) if len(d) else np.inf
        if fd - fb <= 0:
            continue
        rows[dim].append((fb, fd))
        if dim == 1:
            h1.append((fb, fd, tuple(b), tuple(d) if len(d) else None))
    dgms = {k: np.asarray(v, float).reshape(-1, 2) for k, v in rows.items()}
    h1.sort(key=lambda r: -(r[1] - r[0]) if np.isfinite(r[1]) else -1e18)
    return dict(dgms=dgms, h1=h1)


def betti_at(dgm: np.ndarray, t: float) -> int:
    if len(dgm) == 0:
        return 0
    return int(((dgm[:, 0] <= t) & (dgm[:, 1] > t)).sum())


def betti_curve(dgm: np.ndarray, grid: np.ndarray) -> np.ndarray:
    if len(dgm) == 0:
        return np.zeros_like(grid, dtype=int)
    b = dgm[:, 0][None, :]
    d = dgm[:, 1][None, :]
    g = grid[:, None]
    return ((b <= g) & (d > g)).sum(axis=1)


def persistent_entropy(dgm: np.ndarray) -> float:
    if len(dgm) == 0:
        return 0.0
    L = dgm[:, 1] - dgm[:, 0]
    L = L[np.isfinite(L) & (L > 0)]
    if len(L) == 0:
        return 0.0
    p = L / L.sum()
    return float(-(p * np.log(p)).sum())


def capped(dgm: np.ndarray, cap: float) -> np.ndarray:
    out = dgm.copy()
    if len(out):
        out[~np.isfinite(out[:, 1]), 1] = cap
    return out


def bottleneck(d1: np.ndarray, d2: np.ndarray, cap: float) -> float:
    return float(gudhi.bottleneck_distance(capped(d1, cap), capped(d2, cap)))
