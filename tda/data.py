"""Carga de datos: red urbana desde OpenStreetMap (OSMnx) y nubes de puntos CSV.

Todas las funciones devuelven un diccionario ligero (arrays de numpy) para que
pueda cachearse sin coste en Streamlit:

    lon, lat : coordenadas geográficas (EPSG:4326) de los vértices
    x, y     : coordenadas proyectadas en metros (UTM local)
    graph_edges, graph_len : aristas del grafo primario (sólo red OSM)
    streets  : geometrías de las calles en lon/lat (sólo red OSM)
"""
from __future__ import annotations

import hashlib
import io
import unicodedata

import numpy as np
import pandas as pd
from pyproj import Transformer

# --------------------------------------------------------------------------- #
# Utilidades geográficas
# --------------------------------------------------------------------------- #
NETWORK_TYPES = {
    "drive": "drive · calles transitables en automóvil",
    "drive_service": "drive_service · incluye vías de servicio",
    "walk": "walk · red peatonal",
    "bike": "bike · red ciclable",
    "all_public": "all_public · todas las vías públicas",
    "all": "all · todas las vías (incl. privadas)",
}


def utm_epsg(lon: float, lat: float) -> int:
    """Código EPSG de la zona UTM que contiene el punto (Lima → 32718)."""
    zone = int((lon + 180.0) // 6.0) + 1
    return (32700 if lat < 0 else 32600) + zone


def haversine(lat0, lon0, lat, lon):
    """Distancia ortodrómica en metros (vectorizada)."""
    r = 6_371_008.8
    p0, p = np.radians(lat0), np.radians(lat)
    dphi = p - p0
    dlmb = np.radians(lon) - np.radians(lon0)
    a = np.sin(dphi / 2) ** 2 + np.cos(p0) * np.cos(p) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def _points_dict(lon, lat, *, key, source, labels=None, meta=None):
    lon = np.asarray(lon, float)
    lat = np.asarray(lat, float)
    epsg = utm_epsg(float(lon.mean()), float(lat.mean()))
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    x, y = tr.transform(lon, lat)
    return dict(
        key=key, source=source, lon=lon, lat=lat,
        x=np.asarray(x, float), y=np.asarray(y, float), epsg=epsg,
        graph_edges=None, graph_len=None, streets=None,
        center=(float(lat.mean()), float(lon.mean())), radius=None,
        labels=labels, meta=meta or {},
    )


# --------------------------------------------------------------------------- #
# Red urbana OSM
# --------------------------------------------------------------------------- #
def download_osm_network(lat: float, lon: float, radius: float,
                         network_type: str = "drive",
                         consolidation: float = 10.0) -> dict:
    """Descarga la red de OSM, la recorta a un círculo y consolida los nodos.

    Incluye:
      1. Caché persistente en disco (data/cache_osm/) para carga instantánea offline.
      2. Rotación de servidores espejo (mirrors) internacionales independientes.
      3. Restauración de DNS por si un servidor rechaza la conexión.
    """
    import pickle
    from pathlib import Path
    import socket
    import networkx as nx
    import osmnx as ox

    # Comprobación de caché en disco (evita saturar Overpass)
    cache_dir = Path(__file__).resolve().parent.parent / "data" / "cache_osm"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key = hashlib.sha256(
        f"{lat:.5f}_{lon:.5f}_{int(radius)}_{network_type}_{float(consolidation):.1f}".encode()
    ).hexdigest()[:16]
    cache_file = cache_dir / f"osm_{cache_key}.pkl"

    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
            return cached_data
        except Exception:
            pass  # Si el archivo está corrupto, se vuelve a descargar

    ox.settings.use_cache = True
    ox.settings.log_console = False
    ox.settings.requests_timeout = 180
    ox.settings.overpass_rate_limit = False

    # Servidores espejo independientes en distintas geografías
    endpoints = [
        "https://maps.mail.ru/osm/tools/overpass/api",
        "https://overpass.kumi.systems/api",
        "https://overpass.private.coffee/api",
        "https://overpass-api.de/api",
    ]

    G = None
    last_err = None
    for ep in endpoints:
        try:
            # Restaurar socket.getaddrinfo si OSMnx lo modificó para una IP previa
            if hasattr(socket, "_original_getaddrinfo"):
                socket.getaddrinfo = socket._original_getaddrinfo

            ox.settings.overpass_url = ep
            G = ox.graph_from_point(
                (lat, lon), dist=float(radius), dist_type="bbox",
                network_type=network_type, simplify=True, retain_all=True,
                truncate_by_edge=True,
            )
            if G is not None and G.number_of_nodes() > 0:
                break
        except Exception as err:
            last_err = err
            continue

    if G is None:
        raise RuntimeError(
            f"Los servidores públicos de OpenStreetMap (Overpass API) están temporalmente saturados "
            f"o han rechazado la descarga para un radio de {int(radius)} m (área de {int(2*radius)}x{int(2*radius)} m).\n\n"
            f"💡 Recomendaciones:\n"
            f"1. Para radios grandes (1000 m o 1500 m), el servidor puede tardar entre 20 y 45 segundos según la cola.\n"
            f"2. Puedes usar radios de 400 m a 800 m para una respuesta casi instantánea.\n"
            f"3. Si deseas analizar nubes de puntos de gran escala sin depender de los servidores públicos de OSM, "
            f"puedes usar la pestaña de Dataset CSV propio o el dataset de ejemplo.\n\n"
            f"Detalle técnico original: {last_err}"
        )

    # Recorte circular (el bbox es un cuadrado de lado 2r)
    nodes = np.fromiter(G.nodes, dtype=np.int64, count=G.number_of_nodes())
    nlon = np.array([G.nodes[n]["x"] for n in nodes])
    nlat = np.array([G.nodes[n]["y"] for n in nodes])
    outside = nodes[haversine(lat, lon, nlat, nlon) > radius]
    G.remove_nodes_from(outside.tolist())
    G.remove_nodes_from(list(nx.isolates(G)))
    if G.number_of_nodes() < 3:
        raise ValueError("La red descargada tiene menos de 3 nodos. "
                         "Aumente el radio o cambie el tipo de red.")

    epsg = utm_epsg(lon, lat)
    Gp = ox.project_graph(G, to_crs=f"EPSG:{epsg}")
    n_raw = Gp.number_of_nodes()
    if consolidation and consolidation > 0:
        Gp = ox.consolidate_intersections(
            Gp, tolerance=float(consolidation) / 2.0, rebuild_graph=True,
            dead_ends=True, reconnect_edges=True,
        )
    Gu = ox.convert.to_undirected(Gp)

    node_ids = list(Gu.nodes)
    index = {n: i for i, n in enumerate(node_ids)}
    x = np.array([Gu.nodes[n]["x"] for n in node_ids], float)
    y = np.array([Gu.nodes[n]["y"] for n in node_ids], float)

    gdf = ox.graph_to_gdfs(Gu, nodes=False, fill_edge_geometry=True)
    edge_len: dict[tuple[int, int], float] = {}
    for (u, v, _k), geom in zip(gdf.index, gdf.geometry):
        if u == v:
            continue
        a, b = index[u], index[v]
        key = (a, b) if a < b else (b, a)
        L = float(geom.length) if geom is not None else float(np.hypot(x[a] - x[b], y[a] - y[b]))
        if key not in edge_len or L < edge_len[key]:
            edge_len[key] = L
    E = np.array(list(edge_len.keys()), dtype=np.int64).reshape(-1, 2)
    L = np.array(list(edge_len.values()), dtype=float)

    # Geometría de calles simplificada (1 m) en lon/lat para dibujar
    geoms = gdf.geometry.simplify(1.0).to_crs(4326)
    streets = []
    for g in geoms:
        if g is None or g.is_empty:
            continue
        parts = getattr(g, "geoms", [g])
        for p in parts:
            streets.append(np.round(np.asarray(p.coords)[:, :2], 6))

    inv = Transformer.from_crs(epsg, 4326, always_xy=True)
    nlon, nlat = inv.transform(x, y)

    res = dict(
        key=f"osm|{lat:.6f}|{lon:.6f}|{radius}|{network_type}|{consolidation}",
        source="osm", lon=np.asarray(nlon), lat=np.asarray(nlat), x=x, y=y,
        epsg=epsg, graph_edges=E, graph_len=L, streets=streets,
        center=(lat, lon), radius=float(radius), labels=None,
        meta=dict(n_raw=n_raw, n_nodes=len(node_ids), n_edges=len(E),
                  network_type=network_type, consolidation=consolidation),
    )

    try:
        with open(cache_file, "wb") as f:
            pickle.dump(res, f)
    except Exception:
        pass

    return res


# --------------------------------------------------------------------------- #
# CSV
# --------------------------------------------------------------------------- #
LON_ALIASES = ("lon", "lng", "long", "longitud", "longitude", "x", "coordx", "lonx")
LAT_ALIASES = ("lat", "latitud", "latitude", "y", "coordy", "laty")
NAME_ALIASES = ("nombre", "name", "id", "establecimiento", "descripcion", "label")


def _norm(name) -> str:
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _find_column(columns, aliases, prefixes=()):
    norm = {c: _norm(c) for c in columns}
    for a in aliases:
        for c, n in norm.items():
            if n == a:
                return c
    for p in prefixes:
        for c, n in norm.items():
            if n.startswith(p):
                return c
    return None


def _detect_sep(text: str) -> str:
    sample = "\n".join(text.splitlines()[:6])
    counts = {s: sample.count(s) for s in (";", ",", "\t", "|")}
    # Con decimales con coma el separador suele ser ';'
    if counts[";"] > 0 and counts[";"] >= counts["\t"]:
        return ";"
    return max(counts, key=counts.get)


def _to_float(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    s = s.astype(str).str.strip().str.replace(" ", "", regex=False)
    return pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")


def parse_points_csv(raw: bytes, max_points: int = 6000) -> dict:
    """Lee un CSV separado por ',' o ';' con columnas lon/longitud y lat/latitud."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    sep = _detect_sep(text)
    df = pd.read_csv(io.StringIO(text), sep=sep, engine="python")

    lon_col = _find_column(df.columns, LON_ALIASES, ("lon", "lng"))
    lat_col = _find_column(df.columns, LAT_ALIASES, ("lat",))
    if lon_col is None or lat_col is None:
        raise ValueError(
            "No se encontraron columnas de coordenadas. Use nombres como "
            "'lon'/'longitud' y 'lat'/'latitud'. Columnas detectadas: "
            + ", ".join(map(str, df.columns)))
    name_col = _find_column(df.columns, NAME_ALIASES)

    lon = _to_float(df[lon_col])
    lat = _to_float(df[lat_col])
    ok = lon.between(-180, 180) & lat.between(-90, 90)
    n_total = len(df)
    df = df.loc[ok].assign(_lon=lon[ok].values, _lat=lat[ok].values)
    n_invalid = n_total - len(df)
    before = len(df)
    df = df.drop_duplicates(subset=["_lon", "_lat"])
    n_dup = before - len(df)
    n_sub = 0
    if len(df) > max_points:
        n_sub = len(df) - max_points
        df = df.sample(max_points, random_state=0)
    if len(df) < 3:
        raise ValueError("El dataset debe contener al menos 3 puntos válidos.")

    labels = df[name_col].astype(str).tolist() if name_col else None
    key = "csv|" + hashlib.md5(raw).hexdigest()
    return _points_dict(
        df["_lon"].values, df["_lat"].values, key=key, source="csv",
        labels=labels,
        meta=dict(sep=sep, lon_col=str(lon_col), lat_col=str(lat_col),
                  n_total=n_total, n_invalid=n_invalid, n_dup=n_dup,
                  n_sub=n_sub, n_points=len(df)),
    )
