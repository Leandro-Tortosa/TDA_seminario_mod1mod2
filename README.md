# 🕸️ Aplicación 1: Seminario TDA — Módulo 1 + Módulo 2 (Universidad del Pacífico)

Aplicación web interactiva desarrollada con **Streamlit**, **GUDHI**, **OSMnx**, **NetworkX**, **Folium** y **Plotly** para el cálculo y visualización pedagógica de **Complejos Simpliciales** y **Homología Persistente** en Lima Metropolitana y el territorio peruano.

> 📖 **Documentación Detallada**: Puedes consultar el manual completo técnico, pedagógico y de opciones en [DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md).

---

## 🎯 Objetivos de la Aplicación (Módulos 1 y 2)

- **Módulo 1: Complejos Simpliciales y Grafo Urbano**
  - Descarga y recorte circular de la red de calles mediante **OSMnx** con consolidación métrica de nodos (intersecciones a distancia menor de $x$ metros se funden).
  - Carga flexible de datasets en formato **CSV** (delimitadores `,` o `;`, coma decimal y detección heurística de nombres de columna de coordenadas: `lat`, `latitud`, `lon`, `longitud`, etc.).
  - Construcción de tres tipos de complejos simpliciales con parámetro métrico común $\alpha$:
    - **Alpha Complejo ($\alpha$-complex)**: subcomplejo óptimo de la triangulación de Delaunay acotado por celdas de Voronoi.
    - **Complejo Flag (Clique)**: basado en el grafo primario vial de OSM o la triangulación con aristas $\le \alpha$.
    - **Vietoris–Rips**: relaciones métricas por pares de puntos.
  - Cálculo de la **centralidad betweenness** (intermediación) sobre el 1-esqueleto del complejo, con opción de aproximación de Brandes por muestreo de $k$-fuentes para garantizar máxima fluidez.

- **Módulo 2: Filtraciones y Homología Persistente**
  - **Filtración multiescala** por dos variables:
    1. **Distancia física ($\varepsilon$)** en metros.
    2. **Centralidad betweenness** (*lower-star filtration*, en orden descendente o ascendente).
  - Inspección interactiva del complejo en cada nivel de filtración con localización de los **agujeros $H_1$ activos**.
  - **Homología persistente**:
    - **Diagramas de persistencia** y **Códigos de barras (barcodes)** interactivos con Plotly.
    - Curvas multiescala de números de Betti ($\beta_0, \beta_1, \beta_2$).
    - Tabla clasificatoria de ciclos (identificación de **señal topológica persistente** vs. **ruido local/manzanas**).
    - Entropía persistente y **Distancia de Bottleneck ($d_B$)** para análisis de estabilidad.

---

## 🚀 Ejecución Local

### 1. Requisitos previos
Tener Python 3.10+ instalado. Se recomienda un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# o venv\Scripts\activate en Windows
```

### 2. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 3. Lanzar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

---

## 🌐 Despliegue en Streamlit Cloud

1. Inicializa el repositorio Git en la carpeta del proyecto:
   ```bash
   git init
   git add .
   git commit -m "feat: Aplicación 1 TDA - Módulos 1 y 2 UP"
   ```
2. Sube el código a tu cuenta de **GitHub**.
3. Accede a [share.streamlit.io](https://share.streamlit.io), conecta tu repositorio de GitHub y selecciona:
   - **Main file path**: `app.py`
4. ¡Listo! Streamlit Cloud instalará automáticamente las librerías desde `requirements.txt`.

---

## 📁 Estructura del Proyecto

```
App1_mod1-2/
├── app.py                  # Punto de entrada principal y orquestación de Streamlit
├── requirements.txt        # Dependencias de Python
├── .streamlit/
│   └── config.toml         # Configuración del servidor y tema estético oscuro
├── tda/
│   ├── data.py             # Descarga OSMnx, consolidación y lector CSV robusto
│   ├── complexes.py        # Alpha, Flag y Vietoris-Rips con GUDHI
│   ├── centrality.py       # Betweenness (exacta y aproximación Brandes k-fuentes)
│   ├── homology.py         # Árboles simpliciales, persistencia, Betti y Bottleneck
│   ├── maps.py             # Mapas Folium con 6 basemaps, render 4:3 y canvas
│   ├── plots.py            # Diagramas de persistencia y barcodes con Plotly
│   ├── tabs.py             # Componentes de las Pestañas 1, 2 y 3
│   └── ui.py               # Sistema de diseño CSS, KPIs y tarjetas
├── data/
│   └── ejemplo_establecimientos_lima.csv  # Dataset sintético de ejemplo
└── scripts/
    └── generar_ejemplo.py  # Generador de datos sintéticos (estrategias del syllabus)
```
