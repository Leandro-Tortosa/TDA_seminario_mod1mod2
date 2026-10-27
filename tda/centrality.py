"""Centralidad betweenness y estadísticas del 1-esqueleto del complejo."""
from __future__ import annotations

import networkx as nx
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def betweenness(n: int, E: np.ndarray, w: np.ndarray, k: int | None = None,
                seed: int = 42) -> np.ndarray:
    """Betweenness de los 0-símplices sobre el grafo (0-símplices, 1-símplices).

    Si ``k`` no es None se usa la aproximación de Brandes con ``k`` nodos fuente
    muestreados (mucho más rápida en redes con miles de nodos).
    """
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_weighted_edges_from(zip(E[:, 0].tolist(), E[:, 1].tolist(),
                                  np.maximum(w, 1e-6).tolist()))
    kk = None if (k is None or k >= n) else int(k)
    bc = nx.betweenness_centrality(G, k=kk, weight="weight",
                                   normalized=True, seed=seed)
    return np.fromiter((bc[i] for i in range(n)), float, count=n)


def graph_stats(n_total: int, V_mask: np.ndarray, E: np.ndarray) -> dict:
    """Componentes, grado medio y tamaño de la componente gigante."""
    idx = np.flatnonzero(V_mask)
    nv = len(idx)
    if nv == 0:
        return dict(nv=0, ne=0, comps=0, giant=0.0, mean_deg=0.0)
    remap = -np.ones(n_total, np.int64)
    remap[idx] = np.arange(nv)
    if len(E):
        a, b = remap[E[:, 0]], remap[E[:, 1]]
        A = coo_matrix((np.ones(len(E)), (a, b)), shape=(nv, nv))
    else:
        A = coo_matrix((nv, nv))
    ncomp, labels = connected_components(A, directed=False)
    giant = np.bincount(labels).max() / nv
    return dict(nv=nv, ne=int(len(E)), comps=int(ncomp), giant=float(giant),
                mean_deg=float(2 * len(E) / nv))
