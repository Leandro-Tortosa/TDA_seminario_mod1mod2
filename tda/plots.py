"""Gráficos de homología persistente con Plotly (Estilo Claro, Ejes Nítidos y Alta Legibilidad)."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

DIM_COLORS = {0: "#0284c7", 1: "#dc2626", 2: "#7c3aed"}
DIM_NAMES = {0: "H₀ · componentes conexas", 1: "H₁ · ciclos / agujeros", 2: "H₂ · cavidades 3D"}


def _style(fig, title, xt, yt, height=450):
    """Estilo claro de alta precisión con ejes nítidos, cuadrícula visible y tipografía legible."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.01,
            font=dict(size=16, color="#0f172a", family="Outfit, Inter, sans-serif")
        ),
        template="plotly_white",
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8fafc",
        margin=dict(l=55, r=20, t=55, b=50),
        font=dict(family="Inter, sans-serif", size=12, color="#0f172a"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#cbd5e1",
            borderwidth=1,
            font=dict(size=11, color="#0f172a")
        ),
        xaxis=dict(
            title=dict(text=f"<b>{xt}</b>", font=dict(size=13, color="#0f172a")),
            showline=True,
            linewidth=1.5,
            linecolor="#334155",
            showgrid=True,
            gridcolor="#e2e8f0",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#94a3b8",
            zerolinewidth=1.5,
            ticks="outside",
            ticklen=5,
            tickwidth=1.5,
            tickcolor="#334155",
            tickfont=dict(size=11, color="#334155", family="Inter, sans-serif"),
        ),
        yaxis=dict(
            title=dict(text=f"<b>{yt}</b>", font=dict(size=13, color="#0f172a")),
            showline=True,
            linewidth=1.5,
            linecolor="#334155",
            showgrid=True,
            gridcolor="#e2e8f0",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="#94a3b8",
            zerolinewidth=1.5,
            ticks="outside",
            ticklen=5,
            tickwidth=1.5,
            tickcolor="#334155",
            tickfont=dict(size=11, color="#334155", family="Inter, sans-serif"),
        ),
    )
    return fig


def persistence_diagram(dgms: dict, cap: float, unit: str):
    """Diagrama de persistencia (nacimiento vs muerte) con diagonal y clases esenciales."""
    top = cap * 1.06 if cap > 0 else 1
    fig = go.Figure()

    # Diagonal y = x (línea de muerte instantánea)
    fig.add_trace(go.Scatter(
        x=[0, top], y=[0, top], mode="lines",
        name="y = x (diagonal)",
        line=dict(color="#64748b", dash="dash", width=1.8),
        hoverinfo="skip"
    ))

    # Línea de persistencia infinita (clases que no mueren antes del umbral)
    fig.add_hline(
        y=top,
        line=dict(color="#94a3b8", dash="dot", width=1.5),
        annotation_text="∞ (clases esenciales / no mueren)",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#475569")
    )

    for dim in sorted(dgms):
        arr = dgms[dim]
        if len(arr) == 0:
            continue
        fin = np.isfinite(arr[:, 1])
        b = arr[:, 0]
        d = np.where(fin, arr[:, 1], top)
        pers = np.where(fin, arr[:, 1] - arr[:, 0], np.inf)

        txt = [
            f"<b>{DIM_NAMES[dim]}</b><br>"
            f"Nacimiento (b): {bb:.3g} {unit}<br>"
            f"Muerte (d): {'∞' if not f else f'{dd:.3g}'} {unit}<br>"
            f"Persistencia: {'∞ (esencial)' if not f else f'{p:.3g}'} {unit}"
            for bb, dd, p, f in zip(b, arr[:, 1], pers, fin)
        ]

        fig.add_trace(go.Scattergl(
            x=b, y=d, mode="markers",
            name=DIM_NAMES[dim],
            text=txt,
            hovertemplate="%{text}<extra></extra>",
            marker=dict(
                color=DIM_COLORS[dim],
                size=np.where(fin, 9, 13),
                symbol=np.where(fin, "circle", "triangle-up"),
                line=dict(color="#0f172a", width=1),
                opacity=0.88
            )
        ))

    fig = _style(fig, "Diagrama de Persistencia", f"Nacimiento b ({unit})", f"Muerte d ({unit})")
    fig.update_xaxes(range=[-0.02 * top, top * 1.02])
    fig.update_yaxes(range=[-0.02 * top, top * 1.04], scaleanchor="x", scaleratio=1)
    return fig


def barcode(dgms: dict, cap: float, unit: str, top_n: int = 60):
    """Código de barras de persistencia ordenado por vida útil."""
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
            pers = "∞" if not np.isfinite(arr[i, 1]) else f"{(arr[i, 1] - arr[i, 0]):.3g}"
            t = f"<b>{DIM_NAMES[dim]}</b><br>[{arr[i, 0]:.3g}, {dd}) {unit}<br>Persistencia: {pers} {unit}"
            txt += [t, t, None]

        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines",
            name=DIM_NAMES[dim],
            line=dict(color=DIM_COLORS[dim], width=4.5),
            text=txt,
            hovertemplate="%{text}<extra></extra>"
        ))
        y0 += len(order) + 3

    fig = _style(
        fig,
        f"Código de Barras (top {top_n} intervalos)",
        f"Escala de filtración ({unit})",
        "Intervalos de persistencia [b, d)"
    )
    fig.update_yaxes(showticklabels=False, autorange="reversed")
    fig.update_xaxes(range=[-0.01 * top, top * 1.01])
    return fig


def betti_curves(grid, curves: dict, unit: str, threshold=None, title="Curvas de Betti", height=350):
    """Curvas continuas de los números de Betti a lo largo de la filtración."""
    fig = go.Figure()
    for dim, c in curves.items():
        if np.any(c):
            fig.add_trace(go.Scatter(
                x=grid, y=c, mode="lines", line_shape="hv",
                name=f"β{'₀₁₂'[dim]} ({DIM_NAMES[dim].split('·')[1].strip()})",
                line=dict(color=DIM_COLORS[dim], width=3),
                fill="tozeroy",
                fillcolor=_alpha(DIM_COLORS[dim], 0.14)
            ))

    if threshold is not None:
        fig.add_vline(
            x=threshold,
            line=dict(color="#0f172a", dash="dash", width=2),
            annotation_text=f"Umbral actual: {threshold:.2f} {unit}",
            annotation_position="top right",
            annotation_font=dict(size=11, color="#0f172a", family="Inter, sans-serif")
        )

    return _style(fig, title, f"Escala de filtración ({unit})", "Número de Betti", height)


def histogram(values, title, xt, color="#0284c7", height=320):
    """Histograma en escala logarítmica con bordes definidos."""
    fig = go.Figure(go.Histogram(
        x=values,
        nbinsx=40,
        marker=dict(
            color=color,
            line=dict(color="#0f172a", width=0.8),
            opacity=0.85
        )
    ))
    fig = _style(fig, title, xt, "Frecuencia (escala log)", height)
    fig.update_yaxes(type="log")
    return fig


def _alpha(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"
