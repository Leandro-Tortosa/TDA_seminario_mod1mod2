"""Genera el dataset sintético de ejemplo (Estrategias A y C del syllabus).

Simula establecimientos de salud/farmacias en Lima Centro:
  * núcleo denso en el Cercado de Lima,
  * un anillo de establecimientos alrededor de un 'desierto de cobertura'
    (vacío central → clase H1 muy persistente),
  * puntos dispersos en la periferia (La Victoria / Breña / Rímac).
Uso:  python scripts/generar_ejemplo.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
M_LAT = 1 / 110_574.0               # grados por metro (latitud)
M_LON = 1 / (111_320.0 * np.cos(np.radians(12.06)))


def offset(lat0, lon0, dx, dy):
    return lat0 + dy * M_LAT, lon0 + dx * M_LON


rows = []
# 1) Núcleo denso: Cercado de Lima
for i in range(150):
    dx, dy = rng.normal(0, 380, 2)
    rows.append(("Núcleo Cercado", *offset(-12.0500, -77.0330, dx, dy)))
# 2) Anillo con desierto central (La Victoria)
for i in range(64):
    th = rng.uniform(0, 2 * np.pi)
    r = rng.normal(520, 35)
    rows.append(("Anillo La Victoria", *offset(-12.0700, -77.0180, r * np.cos(th), r * np.sin(th))))
# 3) Segundo anillo menor (Breña)
for i in range(38):
    th = rng.uniform(0, 2 * np.pi)
    r = rng.normal(300, 22)
    rows.append(("Anillo Breña", *offset(-12.0590, -77.0520, r * np.cos(th), r * np.sin(th))))
# 4) Dispersos en la periferia (fuera de los dos 'desiertos')
holes = [((-12.0700, -77.0180), 600), ((-12.0590, -77.0520), 360)]
n_per = 0
while n_per < 60:
    dx, dy = rng.uniform(-2200, 2200, 2)
    la, lo = offset(-12.0600, -77.0300, dx, dy)
    if any(np.hypot((la - c[0]) / M_LAT, (lo - c[1]) / M_LON) < r for c, r in holes):
        continue
    rows.append(("Periferia", la, lo))
    n_per += 1

df = pd.DataFrame(rows, columns=["zona", "latitud", "longitud"])
df.insert(0, "nombre", [f"EESS-{i:03d}" for i in range(len(df))])
df["latitud"] = df["latitud"].round(6)
df["longitud"] = df["longitud"].round(6)
out = Path(__file__).resolve().parents[1] / "data" / "ejemplo_establecimientos_lima.csv"
out.parent.mkdir(exist_ok=True)
# Separador ';' y coma decimal (formato habitual en Excel en español)
df.to_csv(out, sep=";", decimal=",", index=False)
print(out, len(df))
