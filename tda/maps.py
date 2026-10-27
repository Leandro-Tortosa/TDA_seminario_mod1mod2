"""Mapas interactivos (Folium/Leaflet) optimizados para complejos simpliciales.

Optimización: las aristas y los triángulos se agrupan por color (32 clases) en
una única geometría Multi* por clase, de modo que el HTML es muy ligero aunque
haya decenas de miles de símplices. Leaflet dibuja en <canvas> (prefer_canvas).
"""
from __future__ import annotations

import html as _html

import folium
import matplotlib as mpl
import numpy as np
from branca.element import Element, MacroElement
from jinja2 import Template

N_BINS = 32
NODE_TOOLTIP_MAX = 3500

BASEMAPS = {
    "Esri topográfico": dict(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, USGS, NRCAN",
        dark=False, native=19),
    "OpenStreetMap estándar": dict(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
        dark=False, native=19),
    "OpenStreetMap Humanitario (HOT)": dict(
        tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team",
        dark=False, native=19),
    "OpenTopoMap (Topográfico libre)": dict(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="Kartendaten: &copy; OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: &copy; OpenTopoMap (CC-BY-SA)",
        dark=False, native=17),
    "Esri claro (Gris neutro)": dict(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Esri, HERE, Garmin, &copy; OpenStreetMap",
        dark=False, native=16),
    "Lienzo en blanco (Blank Canvas)": dict(tiles=None, attr="", dark=False, native=20),
}

COLORMAPS = ["viridis", "plasma", "inferno", "magma", "cividis", "turbo"]


# --------------------------------------------------------------------------- #
# Escala de color + leyenda
# --------------------------------------------------------------------------- #
class ColorScale:
    """Escala continua (lineal o por cuantiles) con paleta de matplotlib."""

    def __init__(self, values, cmap="viridis", mode="quantile", title="",
                 fmt="{:.3f}", vmin=None, vmax=None):
        v = np.asarray(values, float)
        v = v[np.isfinite(v)]
        lo = float(np.min(v)) if vmin is None and len(v) else (vmin or 0.0)
        hi = float(np.max(v)) if vmax is None and len(v) else (vmax or 1.0)
        if hi <= lo:
            hi = lo + 1e-9
        idx = None
        if mode == "quantile" and len(v) > 8:
            q = np.quantile(np.clip(v, lo, hi), np.linspace(0, 1, 9))
            q[0], q[-1] = lo, hi
            if np.all(np.diff(q) > 0):
                idx = q
        self.mode = "quantile" if idx is not None else "linear"
        self.idx = idx if idx is not None else np.linspace(lo, hi, 9)
        self.cmap = mpl.colormaps[cmap]
        self.palette = [mpl.colors.to_hex(c) for c in self.cmap(np.linspace(0, 1, N_BINS))]
        self.title, self.fmt = title, fmt

    def t(self, values):
        return np.interp(np.asarray(values, float), self.idx,
                         np.linspace(0, 1, len(self.idx)))

    def bins(self, values):
        return np.clip(np.rint(self.t(values) * (N_BINS - 1)).astype(int), 0, N_BINS - 1)

    def legend_html(self) -> str:
        stops = ", ".join(self.palette[:: max(1, N_BINS // 16)] + [self.palette[-1]])
        ticks = "".join(f"<span>{_html.escape(self.fmt.format(v))}</span>"
                        for v in self.idx[::2])
        sub = "escala por cuantiles" if self.mode == "quantile" else "escala lineal"
        return (f"<div class='tl-title'>{_html.escape(self.title)}</div>"
                f"<div class='tl-bar' style='background:linear-gradient(to right,{stops})'></div>"
                f"<div class='tl-ticks'>{ticks}</div><div class='tl-sub'>{sub}</div>")


class _Legend(MacroElement):
    _template = Template("""
    {% macro script(this, kwargs) %}
    var {{ this.get_name() }} = L.control({position: '{{ this.position }}'});
    {{ this.get_name() }}.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'tda-legend {{ this.theme }}');
        div.innerHTML = {{ this.content|tojson }};
        L.DomEvent.disableClickPropagation(div);
        return div;
    };
    {{ this.get_name() }}.addTo({{ this._parent.get_name() }});
    {% endmacro %}
    """)

    def __init__(self, content, dark=False, position="bottomright"):
        super().__init__()
        self._name = "TdaLegend"
        self.content, self.position = content, position
        self.theme = "dark" if dark else "light"


def _css(dark: bool, blank: bool) -> str:
    return f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body {{ margin:0; padding:0; height:100%; background:transparent; }}
.folium-map {{
  width: min(100%, calc(100vh * 4 / 3)) !important;
  height: min(100vh, calc(100vw * 3 / 4)) !important;
  margin: 0 auto; border-radius: 14px; overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
}}
{'.leaflet-container { background:#ffffff !important; }' if blank else ''}
.leaflet-control-layers {{ font: 11px/1.35 Inter, sans-serif !important;
  border-radius: 9px !important; border: none !important;
  box-shadow: 0 2px 10px rgba(0,0,0,.25) !important; }}
.leaflet-control-layers-expanded {{ padding: 4px 8px 4px 6px !important; }}
.leaflet-control-layers label {{ margin: 1px 0; }}
.leaflet-control-layers-separator {{ margin: 3px -8px 3px -6px !important; }}
.tda-legend {{ font: 11px Inter, sans-serif; padding: 8px 11px 6px; border-radius: 10px;
  min-width: 240px; box-shadow: 0 2px 12px rgba(0,0,0,.28); }}
.tda-legend.light {{ background: rgba(255,255,255,.93); color:#1b2233; }}
.tda-legend.dark {{ background: rgba(14,19,33,.9); color:#e9edf7; }}
.tda-legend .tl-title {{ font-weight:700; font-size:12px; margin-bottom:4px; }}
.tda-legend .tl-bar {{ height: 12px; border-radius: 6px; }}
.tda-legend .tl-ticks {{ display:flex; justify-content:space-between; margin-top:3px;
  font-variant-numeric: tabular-nums; }}
.tda-legend .tl-sub {{ opacity:.65; font-size:10px; margin-top:2px; text-align:right; }}
.leaflet-tooltip {{ font: 11px Inter, sans-serif; }}
</style>"""


def _feat(geom_type, coords, **props):
    return {"type": "Feature", "properties": props,
            "geometry": {"type": geom_type, "coordinates": coords}}


# --------------------------------------------------------------------------- #
# Constructor de mapas
# --------------------------------------------------------------------------- #
class MapBuilder:
    def __init__(self, lon, lat, basemap: str, center=None):
        self.lon, self.lat = np.asarray(lon), np.asarray(lat)
        self.ll = np.column_stack([self.lon, self.lat]).round(6)
        bm = BASEMAPS[basemap]
        self.dark = bm["dark"]
        c = center or (float(self.lat.mean()), float(self.lon.mean()))
        self.m = folium.Map(location=c, zoom_start=15, tiles=None,
                            prefer_canvas=True, control_scale=True,
                            width="100%", height="100%", max_zoom=20)
        if bm["tiles"]:
            folium.TileLayer(tiles=bm["tiles"], attr=bm["attr"], name=basemap,
                             control=False, max_zoom=20,
                             max_native_zoom=bm["native"]).add_to(self.m)
        self.m.get_root().header.add_child(Element(_css(self.dark, bm["tiles"] is None)))
        pad = 0.0004
        self.m.fit_bounds([[float(self.lat.min()) - pad, float(self.lon.min()) - pad],
                           [float(self.lat.max()) + pad, float(self.lon.max()) + pad]])

    # -- capas auxiliares ---------------------------------------------------- #
    def add_area(self, center, radius):
        fg = folium.FeatureGroup(name="Área de estudio", show=True)
        folium.Circle(center, radius=radius, color="#64748b" if not self.dark else "#cbd5e1",
                      weight=1.4, dash_array="6 6", fill=False, interactive=False).add_to(fg)
        fg.add_to(self.m)

    def add_streets(self, streets, name="Grafo primario (OSM)", show=True):
        if not streets:
            return
        color = "#8a94a8" if not self.dark else "#6b7590"
        gj = {"type": "Feature", "properties": {},
              "geometry": {"type": "MultiLineString",
                           "coordinates": [s.tolist() for s in streets]}}
        folium.GeoJson(gj, name=name, show=show, interactive=False,
                       style_function=lambda f, c=color: {"color": c, "weight": 1.2,
                                                          "opacity": 0.75}).add_to(self.m)

    def add_ghost(self, E, T, name="Complejo completo K_α", show=True):
        """Capa de referencia del complejo simplicial completo en la Pestaña 2."""
        fg = folium.FeatureGroup(name=name, show=show)
        if len(T):
            ring = self.ll[np.c_[T, T[:, :1]]]
            folium.GeoJson(_feat("MultiPolygon", [[r] for r in ring.tolist()]),
                           interactive=False,
                           style_function=lambda f: {
                               "fillColor": "#60a5fa" if self.dark else "#3b82f6",
                               "fillOpacity": 0.22,
                               "color": "#93c5fd" if self.dark else "#2563eb",
                               "weight": 0.8,
                               "opacity": 0.5
                           }).add_to(fg)
        if len(E):
            seg = self.ll[E]
            folium.GeoJson(_feat("MultiLineString", seg.tolist()),
                           interactive=False,
                           style_function=lambda f: {
                               "color": "#94a3b8" if self.dark else "#334155",
                               "weight": 1.4,
                               "opacity": 0.75,
                               "dashArray": "4, 4"
                           }).add_to(fg)
        fg.add_to(self.m)

    # -- complejo coloreado -------------------------------------------------- #
    def _binned(self, coords, bins, scale, geom_type):
        feats = []
        for b in np.unique(bins):
            sel = coords[bins == b]
            if geom_type == "MultiPolygon":
                cc = [[r] for r in sel.tolist()]
            else:
                cc = sel.tolist()
            feats.append({"type": "Feature", "properties": {"c": scale.palette[int(b)]},
                          "geometry": {"type": geom_type, "coordinates": cc}})
        return {"type": "FeatureCollection", "features": feats}

    def add_complex(self, V_idx, E, T, vV, vE, vT, scale: ColorScale,
                    node_size=3.5, value_label="valor", fmt="{:.4f}",
                    labels=None, show_tri=True):
        # 2-símplices
        if len(T):
            ring = self.ll[np.c_[T, T[:, :1]]]
            folium.GeoJson(self._binned(ring, scale.bins(vT), scale, "MultiPolygon"),
                           name=f"2-símplices · triángulos ({len(T):,})", show=show_tri,
                           interactive=False,
                           style_function=lambda f: {"fillColor": f["properties"]["c"],
                                                     "fillOpacity": 0.38, "stroke": False}
                           ).add_to(self.m)
        # 1-símplices
        if len(E):
            seg = self.ll[E]
            folium.GeoJson(self._binned(seg, scale.bins(vE), scale, "MultiLineString"),
                           name=f"1-símplices · aristas ({len(E):,})", interactive=False,
                           style_function=lambda f: {"color": f["properties"]["c"],
                                                     "weight": 2.0, "opacity": 0.92}
                           ).add_to(self.m)
        # 0-símplices
        V_idx = np.asarray(V_idx)
        if len(V_idx) == 0:
            return
        stroke = "#0b1020" if not self.dark else "#e2e8f0"
        cols = np.array(scale.palette)[scale.bins(vV)]
        name = f"0-símplices · vértices ({len(V_idx):,})"
        marker = folium.CircleMarker(radius=node_size, fill=True, fill_opacity=0.95,
                                     weight=0.5)
        if len(V_idx) <= NODE_TOOLTIP_MAX:
            feats = []
            for i, c, v in zip(V_idx.tolist(), cols.tolist(), np.asarray(vV).tolist()):
                props = {"c": c, "id": int(i), "v": fmt.format(v)}
                if labels is not None:
                    props["nombre"] = str(labels[i])[:60]
                feats.append({"type": "Feature", "properties": props,
                              "geometry": {"type": "Point", "coordinates": self.ll[i].tolist()}})
            fields, aliases = ["id", "v"], ["Vértice", value_label]
            if labels is not None:
                fields.insert(1, "nombre"); aliases.insert(1, "Nombre")
            folium.GeoJson(
                {"type": "FeatureCollection", "features": feats}, name=name,
                marker=marker,
                style_function=lambda f, s=stroke: {"fillColor": f["properties"]["c"],
                                                    "color": s},
                tooltip=folium.GeoJsonTooltip(fields=fields, aliases=aliases, sticky=False),
            ).add_to(self.m)
        else:
            bins = scale.bins(vV)
            feats = []
            for b in np.unique(bins):
                feats.append({"type": "Feature", "properties": {"c": scale.palette[int(b)]},
                              "geometry": {"type": "MultiPoint",
                                           "coordinates": self.ll[V_idx[bins == b]].tolist()}})
            folium.GeoJson({"type": "FeatureCollection", "features": feats}, name=name,
                           marker=marker, interactive=False,
                           style_function=lambda f, s=stroke: {"fillColor": f["properties"]["c"],
                                                               "color": s}).add_to(self.m)

    def add_h1(self, gens, cap, unit="m", fmt="{:.1f}", max_n=15,
               name="Agujeros H₁ más persistentes"):
        """Marca las clases H1: arista que crea el ciclo (discontinua) y triángulo
        que lo rellena (rojo). Si el ciclo no muere antes de α sólo hay arista."""
        gens = list(gens)[:max_n]
        if not gens:
            return
        fg = folium.FeatureGroup(name=f"{name} ({len(gens)})", show=True)
        pers_all = [min(g[1], cap) - g[0] for g in gens]
        pmax = max(max(pers_all), 1e-9)
        for rank, ((b, d, edge, tri), pers) in enumerate(zip(gens, pers_all), 1):
            dtxt = fmt.format(d) if np.isfinite(d) else "∞ (no se rellena)"
            ptxt = fmt.format(d - b) if np.isfinite(d) else "∞"
            tip = (f"<b>H₁ #{rank}</b><br>nacimiento: {fmt.format(b)} {unit}<br>"
                   f"muerte: {dtxt}<br>persistencia: {ptxt}")
            e = self.ll[list(edge)]
            folium.PolyLine([[p[1], p[0]] for p in e.tolist()], color="#f43f5e",
                            weight=3.5, dash_array="5 4", tooltip=tip).add_to(fg)
            if tri is not None:
                ring = self.ll[list(tri) + [tri[0]]]
                cen = self.ll[list(tri)].mean(axis=0)
                folium.Polygon([[p[1], p[0]] for p in ring.tolist()], color="#ef4444",
                               weight=2, fill=True, fill_color="#ef4444", fill_opacity=0.18,
                               tooltip=tip).add_to(fg)
            else:
                cen = e.mean(axis=0)
            folium.CircleMarker([cen[1], cen[0]], radius=5 + 9 * pers / pmax,
                                color="#ffffff", weight=1.5, fill=True,
                                fill_color="#ef4444", fill_opacity=0.9,
                                tooltip=tip).add_to(fg)
        fg.add_to(self.m)

    def add_legend(self, scale: ColorScale):
        self.m.add_child(_Legend(scale.legend_html(), dark=self.dark))

    def html(self) -> str:
        folium.LayerControl(collapsed=False, position="topright").add_to(self.m)
        return self.m.get_root().render()
