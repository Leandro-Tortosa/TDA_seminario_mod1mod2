"""Gráficos de homología persistente con Plotly (diagramas, códigos de barras, curvas de Betti)."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

DIM_COLORS = {0: "#22d3ee", 1: "#f97316", 2: "#a78bfa"}
DIM_NAMES = {0: "H₀ · componentes", 1: "H₁ · ciclos / agujeros", 2: "H₂ · cavidades"}


def _style(fig, title, xt, yt, height=430):
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=15)),
        template="plotly_dark", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.025)",
        margin=dict(l=10, r=10, t=48, b=10),
        font=dict(family="Inter, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title=xt, gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        yaxis=dict(title=yt, gridcolor="rgba(255,255,255,0.06)", zeroline=False),
    )
    return fig


def persistence_diagram(dgms: dict, cap: float, unit: str):
    top = cap * 1.06 if cap > 0 else 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, top], y=[0, top], mode="lines",
                             line=dict(color="rgba(255,255,255,.35)", dash="dot"),
                             hoverinfo="skip", showlegend=False))
    fig.add_hline(y=top, line=dict(color="rgba(255,255,255,.25)", dash="dash"),
                  annotation_text="∞ (no muere)", annotation_position="top left")
    for dim, arr in dgms.items():
        if len(arr) == 0:
            continue
        fin = np.isfinite(arr[:, 1])
        b, d = arr[:, 0], np.where(fin, arr[:, 1], top)
        pers = np.where(fin, arr[:, 1] - arr[:, 0], np.inf)
        txt = [f"b = {bb:.3g}<br>d = {'∞' if not f else f'{dd:.3g}'}<br>persistencia = "
               f"{'∞' if not f else f'{p:.3g}'} {unit}" for bb, dd, p, f in zip(b, arr[:, 1], pers, fin)]
        fig.add_trace(go.Scattergl(
            x=b, y=d, mode="markers", name=DIM_NAMES[dim], text=txt,
            hovertemplate="%{text}<extra></extra>",
            marker=dict(color=DIM_COLORS[dim], size=np.where(fin, 8, 11),
                        symbol=np.where(fin, "circle", "triangle-up"),
                        line=dict(color="rgba(0,0,0,.6)", width=0.6), opacity=0.85)))
    fig = _style(fig, "Diagrama de persistencia", f"Nacimiento b ({unit})", f"Muerte d ({unit})")
    fig.update_xaxes(range=[-0.02 * top, top * 1.02])
    fig.update_yaxes(range=[-0.02 * top, top * 1.04], scaleanchor="x", scaleratio=1)
    return fig


def barcode(dgms: dict, cap: float, unit: str, top_n: int = 60):
    top = cap * 1.06 if cap > 0 else 1
    fig = go.Figure()
    y0 = 0
    for dim in sorted(dgms):
        arr = dgms[dim]
        if len(arr) == 0:
            continue
        d = np.where(np.isfinite(arr[:, 1]), arr[:, 1], top)
        order = np.argsort(-(d - arr[:, 0]), kind="stable")[:top_n]
        xs, ys, txt = [], [], []
        for j, i in enumerate(order):
            yy = y0 + j
            xs += [arr[i, 0], d[i], None]
            ys += [yy, yy, None]
            dd = "∞" if not np.isfinite(arr[i, 1]) else f"{arr[i, 1]:.3g}"
            t = f"{DIM_NAMES[dim]}<br>[{arr[i, 0]:.3g}, {dd}) {unit}"
            txt += [t, t, None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=DIM_NAMES[dim],
                                 line=dict(color=DIM_COLORS[dim], width=4),
                                 text=txt, hovertemplate="%{text}<extra></extra>"))
        y0 += len(order) + 3
    fig = _style(fig, f"Código de barras (top {top_n} por dimensión)",
                 f"Escala de filtración ({unit})", "")
    fig.update_yaxes(showticklabels=False, autorange="reversed")
    fig.update_xaxes(range=[-0.01 * top, top * 1.01])
    return fig


def betti_curves(grid, curves: dict, unit: str, threshold=None, title="Curvas de Betti",
                 height=330):
    fig = go.Figure()
    for dim, c in curves.items():
        if np.any(c):
            fig.add_trace(go.Scatter(x=grid, y=c, mode="lines", line_shape="hv",
                                     name=f"β{'₀₁₂'[dim]}", line=dict(color=DIM_COLORS[dim], width=2.5),
                                     fill="tozeroy", fillcolor=_alpha(DIM_COLORS[dim], .12)))
    if threshold is not None:
        fig.add_vline(x=threshold, line=dict(color="#f8fafc", dash="dash", width=1.5),
                      annotation_text="umbral actual", annotation_position="top right")
    return _style(fig, title, f"Escala de filtración ({unit})", "Número de Betti", height)


def histogram(values, title, xt, color="#22d3ee", height=300):
    fig = go.Figure(go.Histogram(x=values, nbinsx=40, marker=dict(color=color,
                                 line=dict(color="rgba(0,0,0,.4)", width=0.5))))
    fig = _style(fig, title, xt, "Frecuencia", height)
    fig.update_yaxes(type="log")
    return fig


def _alpha(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"
