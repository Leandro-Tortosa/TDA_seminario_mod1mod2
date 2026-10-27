# 📘 Documentación Técnica y Pedagógica · Aplicación 1 (TDA Módulos 1 y 2)
### Seminario: Análisis Topológico de Datos y Aplicaciones en Perú — Universidad del Pacífico (UP)

---

## 📑 Índice de Contenidos
1. [Introducción y Objetivos Pedagógicos](#1-introducción-y-objetivos-pedagógicos)
2. [Arquitectura del Sistema y Tecnologías](#2-arquitectura-del-sistema-y-tecnologías)
3. [Panel Lateral de Configuración (Detalle de Opciones)](#3-panel-lateral-de-configuración-detalle-de-opciones)
   - 3.1. Datos y Red Urbana
   - 3.2. Rendimiento y Centralidad Betweenness
   - 3.3. Configuración Cartográfica y Visual
   - 3.4. Tipología de Complejos Simpliciales
4. [Estructura y Funcionalidad por Pestañas](#4-estructura-y-funcionalidad-por-pestañas)
   - 4.1. Pestaña 1: Complejo Simplicial
   - 4.2. Pestaña 2: Filtraciones Multiescala
   - 4.3. Pestaña 3: Homología Persistente
5. [Estrategias de Optimización Computacional](#5-estrategias-de-optimización-computacional)
6. [Guía de Construcción, Ejecución y Despliegue](#6-guía-de-construcción-ejecución-y-despliegue)
   - 6.1. Ejecución en Entorno Local
   - 6.2. Publicación en GitHub y Despliegue en Streamlit Cloud
7. [Glosario de Conceptos Topológicos y Preguntas Frecuentes](#7-glosario-de-conceptos-topológicos-y-preguntas-frecuentes)

---

## 1. Introducción y Objetivos Pedagógicos

La **Aplicación 1** del seminario de TDA tiene como finalidad dotar al alumno de una herramienta interactiva, visual e intuitiva para experimentar de manera práctica los conceptos teóricos desarrollados en los **Módulos 1 y 2** del programa académico:

- **Módulo 1: Fundamentos de TDA y Geometría de Complejos Simpliciales**:
  - Pasar de datos espaciales y redes urbanas discretas a estructuras topológicas combinatorias ($k$-símplices).
  - Comprender las diferencias estructurales y computacionales entre el **Alpha Complejo ($\alpha$-complex)**, el **Complejo Flag (Clique)** y el **Complejo de Vietoris–Rips**.
  - Evaluar la importancia nodal y de tramos mediante la **centralidad de intermediación (*betweenness*)** en el 1-esqueleto del complejo.
- **Módulo 2: Homología Persistente, Análisis Multiescala y Estabilidad**:
  - Modelar familias anidadas de subcomplejos simpliciales mediante filtraciones continuas por **distancia métrica** ($\varepsilon$) y por **centralidad** (*lower-star filtration*).
  - Cuantificar las invariantes topológicas mediante los **números de Betti** ($\beta_0$ para componentes conexas, $\beta_1$ para lazos o ciclos, y $\beta_2$ para vacíos 3D) y la **Característica de Euler** ($\chi$).
  - Interpretar firmas topológicas completas con **diagramas de persistencia**, **códigos de barras (*barcodes*)** y curvas de Betti.
  - Distinguir con rigor matemático entre la **señal topológica persistente** (desiertos de cobertura, cerros, ríos, barreras viales) y el **ruido topológico local** (manzanas pequeñas o artefactos métricos).
  - Evaluar la estabilidad topológica mediante la **distancia de Bottleneck ($d_B$)**.

---

## 2. Arquitectura del Sistema y Tecnologías

La aplicación está construida sobre un ecosistema moderno en **Python 3.10+**, estructurada en módulos desacoplados para garantizar limpieza, facilidad de mantenimiento y reproducibilidad:

```
App1_mod1-2/
├── app.py                      # Punto de entrada y gestión de sesión en Streamlit
├── requirements.txt            # Declaración estricta de dependencias
├── .streamlit/
│   └── config.toml             # Configuración de rendimiento de Streamlit y tema visual
├── tda/
│   ├── data.py                 # Extracción OSMnx, recorte radial, consolidación y parser CSV
│   ├── complexes.py            # Construcción con GUDHI (Alpha, Flag, Vietoris-Rips)
│   ├── centrality.py           # Betweenness con NetworkX (exacta y aproximación Brandes)
│   ├── homology.py             # persistence(), betti_curve(), bottleneck() y entropía
│   ├── maps.py                 # Folium/Leaflet: 6 basemaps, canvas y render en formato 4:3
│   ├── plots.py                # Gráficos de persistencia interactivos con Plotly
│   ├── tabs.py                 # Lógica visual de las 3 pestañas principales
│   └── ui.py                   # Sistema de diseño CSS, tarjetas KPI y componentes HTML
├── data/
│   └── ejemplo_establecimientos_lima.csv  # Dataset sintético de prueba
└── scripts/
    └── generar_ejemplo.py      # Generador de datos sintéticos con vacíos topológicos
```

### Tecnologías Principales:
1. **Streamlit (v1.40+)**: Motor de interfaz web reactiva, gestión de estado de sesión (`st.session_state`) y caché de alto rendimiento (`@st.cache_resource`, `@st.cache_data`).
2. **GUDHI (v3.9+)**: Librería del INRIA para computación topológica de vanguardia (`AlphaComplex`, `SimplexTree`, homología persistente y pares de persistencia).
3. **OSMnx (v2.0+)**: Descarga, modelado, recorte geográfico y simplificación de redes viales desde OpenStreetMap.
4. **NetworkX (v3.2+)**: Cálculo de centralidad de intermediación de caminos mínimos y análisis de grafos.
5. **Folium & Branca**: Visualización cartográfica interactiva georreferenciada basada en Leaflet.js.
6. **Plotly (v5.20+)**: Visualización vectorial de diagramas de persistencia, códigos de barras y curvas de Betti con *hover* interactivo y soporte WebGL.
7. **PyProj**: Proyección conforme UTM (EPSG:32718 para Lima) para cálculos de distancia euclídea precisos en metros reales.

---

## 3. Panel Lateral de Configuración (Detalle de Opciones)

El panel lateral izquierdo agrupa todos los controles de entrada y modelado en cuatro secciones numeradas:

### 3.1. Datos y Red Urbana
- **Selector de Fuente de Datos**:
  - `Red urbana (OpenStreetMap)`: Descarga automática de la malla vial real de cualquier parte de Lima o del mundo.
  - `Dataset CSV propio`: Permite al estudiante subir su propio archivo de datos espaciales.
  - `Dataset de ejemplo (sintético)`: Conjunto de datos preparado que simula 312 establecimientos de salud en Lima Centro, con un núcleo denso en el Cercado y dos anillos deliberados en La Victoria y Breña que rodean sendos «desiertos de cobertura sanitaria» (agujeros $\beta_1$).
- **Ubicación de Referencia (Presets en Lima)**:
  - *Plaza Mayor · Cercado de Lima* (`-12.04637, -77.03019`)
  - *Universidad del Pacífico · Jesús María* (`-12.08430, -77.04970`)
  - *Parque Kennedy · Miraflores* (`-12.12110, -77.02970`)
  - *Centro financiero · San Isidro* (`-12.09500, -77.02700`)
  - *Gamarra · La Victoria* (`-12.06800, -77.01350`)
  - *Plaza de Armas · Barranco* (`-12.14900, -77.02150`)
  - *Personalizado*: Habilita la entrada libre de cualquier latitud y longitud.
- **Radio en metros ($r$)**: Deslizador de 300 m a 5.000 m (por defecto 600 m). Define el círculo exacto de descarga urbana alrededor del punto de origen.
- **Tipo de red OSM**:
  - `drive`: Calles transitables para automóviles (predeterminado).
  - `drive_service`: Incluye vías secundarias y de servicio.
  - `walk`: Red peatonal integral (incluye aceras, senderos y escalinatas).
  - `bike`: Red ciclable y ciclovías.
  - `all_public`: Todas las vías de acceso público.
- **Consolidación de Nodos en metros**: Deslizador de 0 a 50 m (por defecto 10 m). Todas las intersecciones intermedias, rotondas o cruces complejos situados a menor distancia se funden en un único nodo primario, eliminando micro-aristas espurias.
- **Lector Flexible de CSV**:
  - Admite separación por comas (`,`) o punto y coma (`;`).
  - Reconoce números decimales tanto con punto (`-77.03`) como con coma (`-77,03`).
  - Reconocimiento heurístico de columnas insensibles a mayúsculas y tildes (`lat`, `latitud`, `latitude`, `coordy`, `lon`, `longitud`, `longitude`, `coordx`, etc.).

### 3.2. Rendimiento y Centralidad Betweenness
- **Aproximación por Muestreo ($k$-fuentes)**: Casilla de verificación activa por defecto. En lugar de calcular los caminos mínimos entre todas las parejas de nodos del grafo ($O(V \cdot E)$), ejecuta el algoritmo de aproximación de Brandes muestreando $k$ nodos origen aleatorios representativos.
- **Número de Nodos Fuente ($k$)**: Deslizador de 10 a 200 (por defecto 50). Permite un compromiso idóneo entre precisión estadística y velocidad instantánea en redes con miles de elementos.

### 3.3. Configuración Cartográfica y Visual
- **6 Mapas Base Optimizados**:
  1. *Esri claro*: Fondo gris tenue que atenúa el ruido visual urbano y destaca la coloración topológica.
  2. *Esri oscuro*: Fondo nocturno de alto contraste, ideal para contrastar paletas brillantes.
  3. *CartoDB Positron*: Estilo cartográfico claro, moderno y minimalista con rotulación sutil.
  4. *CartoDB Dark Matter*: Fondo oscuro elegante y sobrio.
  5. *Lienzo en blanco (Blank Canvas)*: Fondo blanco puro (`#ffffff`) sin cartografía base callejera, concebido para exportar figuras limpias para informes y artículos científicos.
  6. *Esri topográfico*: Cartografía con relieve físico sombreado y curvas de nivel, útil para relacionar la conectividad con accidentes geográficos (ríos, cerros).
- **Paletas de Color Continuas**: `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `turbo`.
- **Modo de Escala**: *Cuantiles* (reparte equitativamente los tonos cromáticos independientemente de colas pesadas) o *Lineal*.
- **Tamaño de los Vértices**: Deslizador de 1.0 a 8.0 px para adaptar la legibilidad según el radio geográfico.

### 3.4. Tipología de Complejos Simpliciales
- **Alpha complejo ($\alpha$-complex)** *(Predeterminado)*:
  - Construido intersectando las bolas de radio $\alpha/2$ con las celdas de Voronoi de los puntos.
  - Al ser subcomplejo estricto de la **Triangulación de Delaunay**, el número de triángulos en el plano está rigurosamente acotado a un máximo de $2n - 5$.
  - Preserva el **mismo tipo de homotopía** que la unión continua de bolas (Teorema del Nervio), sin sufrir explosión combinatoria.
- **Complejo Flag (Clique)**:
  - En redes urbanas, se apoya en el **grafo primario vial de OSM** (aristas viales reales con su longitud física).
  - Rellena automáticamente como 2-símplices aquellos triángulos cerrados formados por 3 calles conectadas. Evidencia la "degeneración por grado nodal" de las redes viales ortogonales.
- **Complejo de Vietoris–Rips**:
  - Forma una arista entre cualquier pareja de puntos cuya distancia sea $\le \alpha$, y rellena todas las camarillas (*cliques*).
  - Muy ilustrativo para distancias pequeñas, pero protegido mediante corte de seguridad para evitar explosión combinatoria cuando $\alpha$ es elevado.
- **Parámetro $\alpha$ en metros**: Distancia física máxima entre vértices de un símplex.

---

## 4. Estructura y Funcionalidad por Pestañas

### 4.1. Pestaña 1: Complejo Simplicial
Ofrece una vista panorámica integral del complejo simplicial a escala completa:
1. **Mapa Interactivo en Gran Tamaño (Relación 4:3)**:
   - Cuadro de capas compacto en la esquina superior derecha que permite encender/apagar de forma independiente: *Área de estudio*, *Grafo primario vial*, *0-símplices (vértices)*, *1-símplices (aristas)* y *2-símplices (triángulos)*.
   - Coloreado coherente de aristas y caras según la **centralidad betweenness** promedio de sus vértices.
   - **Escala cromática flotante** en la esquina inferior derecha con gradiente continuo y valores clave en números tabulares.
   - Puntero interactivo (*tooltip*): muestra el ID del vértice, su betweenness y el nombre de la calle o establecimiento.
2. **Panel de Indicadores KPI**:
   - Conteo de 0-símplices, 1-símplices y 2-símplices.
   - **Característica de Euler**: $\chi = V - E + F$.
   - **Números de Betti** en la escala $\alpha$: $\beta_0$ (componentes conexas) y $\beta_1$ (ciclos o túneles independientes). Verificación de la identidad $\chi = \beta_0 - \beta_1 + \beta_2$.
   - Grado medio del grafo y porcentaje de nodos en la **componente gigante**.
   - Valor máximo y media de la centralidad de intermediación.
3. **Distribución y Nodos Críticos**:
   - Histograma interactivo de la distribución de *betweenness* en escala logarítmica.
   - Tabla interactiva con el **Top 10 de vértices más influyentes**, con su grado nodal y coordenadas geográficas.

---

### 4.2. Pestaña 2: Filtraciones Multiescala
Permite estudiar la evolución y el nacimiento/muerte de la forma topológica a medida que varía la escala:
1. **Selector de Variable de Filtración**:
   - `📏 Distancia (m)`: Filtración métrica clásica $K_\varepsilon \subseteq K_\alpha$. A $\varepsilon = 0$ los vértices están desconectados; a medida que $\varepsilon$ se expande, se unen aristas y se rellenan caras.
   - `⭐ Betweenness (más centrales primero)`: Filtración *lower-star* descendente. Permite observar cómo el "esqueleto" arterial de la ciudad se forma primero y cómo se integran paulatinamente las vías locales.
   - `🔻 Betweenness (menos centrales primero)`: Filtración *lower-star* ascendente.
2. **Controles Dinámicos**:
   - Deslizador de umbral de filtración ($\varepsilon$ o nivel $t \in [0, 1]$).
   - Selector de coloreado de los elementos: por *Valor de filtración propio* o por *Centralidad Betweenness*.
   - Casilla de verificación para **mostrar los agujeros $H_1$ vivos**: dibuja con línea discontinua roja la arista que genera el ciclo y rellena el triángulo donde morirá el vacío.
3. **Mapa del Subcomplejo Filtrado**:
   - Incluye una "capa fantasma" semitransparente con el complejo completo $K_\alpha$ de fondo, permitiendo al alumno ver con exactitud qué porcentaje de la red se ha consolidado en el umbral actual.
4. **Curvas de Betti**:
   - Gráfico continuo de $\beta_0(\varepsilon)$ y $\beta_1(\varepsilon)$ con un marcador vertical interactivo que sigue el deslizador del alumno.

---

### 4.3. Pestaña 3: Homología Persistente
Condensa la firma algebraica multiescala y el diagnóstico urbano:
1. **Gráficos Topológicos Esenciales**:
   - **Diagrama de Persistencia**: Gráfico cartesiano de puntos $(b_i, d_i)$ correspondientes a las clases de $H_0$ (celeste), $H_1$ (naranja) y $H_2$ (violeta). Los puntos que no mueren antes del límite se proyectan en la línea superior punteada $\infty$.
   - **Código de Barras (*Persistence Barcode*)**: Visualización horizontal de los intervalos de vida $[b_i, d_i)$ ordenados por persistencia decreciente.
2. **Métricas de Complejidad y Entropía**:
   - Número total de clases formadas en cada dimensión.
   - **Máxima persistencia en $H_1$**: identifica la escala del mayor vacío cerrado de la red.
   - **Entropía Persistente** ($E = -\sum p_i \log p_i$): cuantifica la dispersión y uniformidad en la duración de los ciclos.
3. **Tabla Diagnóstica: Señal Topológica vs. Ruido**:
   - Clasificación automatizada de cada ciclo $H_1$:
     - **Señal Topológica Persistente**: ciclos de larga duración que representan verdaderos vacíos urbanos (cerros, ríos, barreras físicas o desiertos de atención sanitaria).
     - **Ruido Topológico**: ciclos efímeros cercanos a la diagonal $y=x$, provocados por pequeñas manzanas residenciales o ligeras desviaciones métricas.
4. **Módulo de Estabilidad y Distancia de Bottleneck ($d_B$)**:
   - Cálculo numérico de la distancia de Bottleneck entre la filtración por distancia física y la filtración por centralidad betweenness, ilustrando el Teorema de Estabilidad de Cohen-Steiner et al.

---

## 5. Estrategias de Optimización Computacional

Para posibilitar que la aplicación responda con fluidez en entornos de recursos compartidos (como **Streamlit Cloud**) ante redes con miles de calles y nodos, se han incorporado técnicas avanzadas de optimización:

1. **Caché en Cascada con `@st.cache_resource` y `@st.cache_data`**:
   - Las cuatro etapas más pesadas (Descarga OSM, Construcción del Complejo, Betweenness y Simplex Tree de GUDHI) están cacheadas independientemente con claves hash invariantes. Mover el deslizador de la Pestaña 2 no recalcula el complejo ni la betweenness.
2. **Agrupamiento Geométrico Vectorial (*Color-Binning*)**:
   - En lugar de inyectar 10.000 polígonos individuales en el HTML del mapa Leaflet (lo que colapsaría el navegador), las aristas y triángulos se clasifican en **32 cubetas de color** y se empaquetan en geometrías compuestas `MultiLineString` y `MultiPolygon`. Esto reduce el tamaño del HTML en un **95%** (de más de 20 MB a menos de 400 KB).
3. **Renderizado Directo en `<canvas>`**:
   - Folium está configurado con `prefer_canvas=True`, descargando el trabajo de rasterización en la aceleración por hardware de la GPU del navegador del alumno.
4. **Protección Anti-Explosión Combinatoria**:
   - Para el complejo de Vietoris–Rips, se computa una cota superior del número de triángulos a partir de la distribución de grados de los vértices ($\sum \binom{d_i}{2} / 3$). Si supera los 350.000 triángulos, se detiene la expansión y se advierte al usuario, impidiendo caídas por falta de memoria (OOM).

---

## 6. Guía de Construcción, Ejecución y Despliegue

### 6.1. Ejecución en Entorno Local

#### Paso 1: Clonar o situarse en el directorio del proyecto
```bash
cd /Users/leandro/antigravity/Seminario_UP/App1_mod1-2
```

#### Paso 2: Crear y activar un entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate    # En macOS/Linux
# o bien: venv\Scripts\activate en Windows
```

#### Paso 3: Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Paso 4: Iniciar la aplicación web
```bash
streamlit run app.py
```
El servidor local se abrirá en `http://localhost:8501`.

---

### 6.2. Publicación en GitHub y Despliegue en Streamlit Cloud

Para poner la aplicación a disposición de todos los alumnos del seminario a través de una URL pública gratuita:

#### Paso 1: Inicializar el repositorio Git local
En la carpeta raíz del proyecto:
```bash
git init
git add .
git commit -m "feat: Aplicación 1 TDA (Módulos 1 y 2 UP)"
```

#### Paso 2: Crear el repositorio en GitHub
1. Abre tu navegador y accede a [GitHub](https://github.com/new).
2. Crea un nuevo repositorio (por ejemplo, `TDA-Lima-App1`).
3. Conecta el repositorio local con GitHub y sube los cambios:
```bash
git remote add origin https://github.com/Leandro-Tortosa/TDA_seminario_mod1mod2.git
git branch -M main
git push -u origin main
```

#### Paso 3: Desplegar en Streamlit Community Cloud
1. Entra en [share.streamlit.io](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en el botón azul **"New app"**.
3. Selecciona tu repositorio recién creado:
   - **Repository**: `Leandro-Tortosa/TDA_seminario_mod1mod2`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Haz clic en **"Deploy!"**.
5. Streamlit Cloud leerá automáticamente el archivo `requirements.txt`, instalará `gudhi`, `osmnx`, `folium` y demás librerías en un contenedor Linux y en un par de minutos generará una URL pública y compartible (por ejemplo: `https://tda-lima-app1.streamlit.app`).

---

## 7. Glosario de Conceptos Topológicos y Preguntas Frecuentes

### ¿Por qué el Alpha Complejo es superior en datos espaciales 2D?
En $d=2$, el complejo de Vietoris–Rips genera conexiones espurias redundantes y su número de símplices crece como $O(2^n)$. El Alpha Complejo utiliza el diagrama de Voronoi como "andamio", garantizando que los triángulos se restrinjan a la triangulación de Delaunay ($O(n)$ caras) con preservación exacta de la forma homotópica.

### ¿Qué representa un punto en $H_1$ muy alejado de la diagonal?
Significa que el ciclo o lazo nació a una distancia pequeña ($b_i$) y se mantuvo abierto sin ser cubierto por triángulos hasta una escala métrica muy grande ($d_i$). En el análisis urbano de Lima, esto identifica inequívocamente:
- **Barreras naturales**: el cauce del Río Rímac o el Cerro San Cristóbal.
- **Barreras de infraestructura**: la franja portuaria del Callao o autopistas sin pasos peatonales.
- **Desiertos de servicio**: manzanas pobladas que quedan fuera del alcance caminable de postas o farmacias.

### ¿Cómo interpretar la Característica de Euler ($\chi$)?
La relación $\chi = V - E + F = \beta_0 - \beta_1 + \beta_2$ es una de las joyas de la topología algebraica. Permite al alumno verificar la coherencia combinatoria global de la red: cada componente aislada suma $+1$ a $\chi$, cada arista que forma un ciclo independiente resta $-1$, y cada cara que rellena un ciclo suma $+1$.
