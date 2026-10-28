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
- **Mapas Base Optimizados (100% Abiertos y Gratuitos, sin necesidad de API Key)**:
  1. *Esri topográfico* (Predeterminado): Cartografía con relieve orográfico sombreado y curvas de nivel, idóneo para contrastar la red urbana con barreras físicas.
  2. *OpenStreetMap estándar*: Mapa callejero universal y gratuito de OpenStreetMap.
  3. *OpenStreetMap Humanitario (HOT)*: Estilo cartográfico claro de alta legibilidad urbana.
  4. *OpenTopoMap (Topográfico libre)*: Mapa topográfico abierto con curvas de nivel e hidrografía.
  5. *Esri claro (Gris neutro)*: Fondo gris claro que atenúa el ruido urbano y resalta el complejo simplicial coloreado.
  6. *Lienzo en blanco (Blank Canvas)*: Fondo blanco puro (`#ffffff`) sin mapa callejero de fondo, concebido para exportar figuras limpias para artículos e informes.
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

Mientras que la Pestaña 1 muestra una «fotografía fija» del complejo simplicial en su escala máxima $\alpha$, la **Pestaña 2** permite reproducir la «película» completa de su construcción: una **filtración simplicial**, es decir, una familia anidada de subcomplejos
$$\emptyset \subseteq K_{t_0} \subseteq K_{t_1} \subseteq \dots \subseteq K_{\text{máx}} = K_\alpha$$
donde cada símplex $\sigma \in K_\alpha$ posee un instante o umbral de entrada $f(\sigma)$ y el subcomplejo activo en el umbral $t$ es $K_t = \{\sigma \in K_\alpha : f(\sigma) \le t\}$.

---

#### 4.2.1. Variables de Filtración Disponibles

El control **«Variable de filtración»** define la regla matemática $f(\sigma)$ que gobierna el orden en que nacen los vértices, aristas y triángulos:

1. **`📏 Distancia (m)` — Filtración métrica geométrica ($K_\varepsilon \subseteq K_\alpha$)**:
   - **Vértices (0-símplices)**: Todos tienen valor de filtración $f(v) = 0\,\text{m}$. Por tanto, **todos los nodos existen en el mapa desde $\varepsilon = 0$** como puntos aislados ($\beta_0 = V$).
   - **Aristas (1-símplices)**: Entran cuando el umbral $\varepsilon$ alcanza su escala métrica $f(e)$:
     - En **Vietoris–Rips** y **Flag (clique)**: $f(e)$ es la longitud física de la arista en metros.
     - En **Alpha complejo**: $f(e) = 2\sqrt{\alpha_e^2}$ es el diámetro (en metros) de la menor bola vacía o restringida a las celdas de Voronoi en la que se cortan las regiones de sus extremos.
   - **Triángulos (2-símplices)**: Entran cuando $\varepsilon$ alcanza $f(\tau)$:
     - En **Vietoris–Rips** y **Flag**: $f(\tau) = \max_{e \subset \tau} f(e)$ (la longitud de su lado más largo, instante en que se cierra la 3-camarilla).
     - En **Alpha complejo**: $f(\tau) = 2R_\tau$, donde $R_\tau$ es el radio circunscrito de Delaunay/Voronoi del triángulo (siempre $\ge$ que sus tres aristas).
   - **Lectura urbana**: Al deslizar $\varepsilon$ desde $0$ hasta $\alpha$, se observa cómo los puntos cercanos se agrupan primero en pequeños racimos locales, cómo disminuye el número de componentes conexas ($\beta_0 \downarrow$) hasta formar la componente gigante, y cómo emergen y se sellan los vacíos urbanos ($\beta_1$).

2. **`⭐ Betweenness (más centrales primero)` — Filtración *lower-star* descendente ($t \in [0, 1]$)**:
   - Sea $\tilde{c}(v) = \frac{\text{BC}(v)}{\max_u \text{BC}(u)} \in [0, 1]$ la centralidad de intermediación normalizada de cada vértice.
   - A cada vértice se le asigna el valor de entrada $f(v) = 1 - \tilde{c}(v) \in [0, 1]$, y a cada arista o triángulo se le asigna el máximo de sus vértices (**regla de la estrella inferior o *lower-star***):
     $$f(\sigma) = \max_{v \in \sigma} f(v)$$
   - Esto garantiza que una calle o triángulo entra en el subcomplejo $K_t$ **en el instante exacto en que todos sus vértices han superado el umbral de centralidad** $\tilde{c}(v) \ge 1 - t$.
   - **Lectura urbana**: En $t$ cercano a $0$ solo aparecen las intersecciones más estratégicas de toda la ciudad; al avanzar $t$, se dibuja primero la **columna vertebral o esqueleto arterial** de grandes avenidas y puentes de flujo, y solo al final ($t \to 1$) se rellenan las calles residenciales y fondos de saco.

3. **`🔻 Betweenness (menos centrales primero)` — Filtración *lower-star* ascendente ($t \in [0, 1]$)**:
   - Invierte el orden anterior asignando $f(v) = \tilde{c}(v)$ y $f(\sigma) = \max_{v \in \sigma} \tilde{c}(v)$.
   - **Lectura urbana**: Nacen primero las zonas periféricas, tranquilas o de baja intermediación ($\tilde{c}(v) \le t$), mientras que los grandes corredores arteriales quedan ausentes al principio, dejando **grandes vacíos o trincheras topológicas** allí donde discurren las avenidas principales hasta que $t$ se aproxima a $1$.

---

#### 4.2.2. ¿Cómo se interpreta la representación en el Mapa de la Pestaña 2?

Para que el alumno nunca pierda la referencia espacial ni el contexto de qué parte de la ciudad falta por activarse, el mapa de la Pestaña 2 superpone **tres niveles visuales claramente diferenciados** (controlables desde el cuadro de capas de la esquina superior derecha):

1. **Fondo de referencia o «Capa Fantasma» (`Complejo completo K_α`)**:
   - Representa el estado final completo $K_\alpha$ (el mismo complejo íntegro de la Pestaña 1), pero dibujado de forma atenuada:
     - **Aristas de $K_\alpha$**: Líneas **discontinuas gris-azuladas** finas (`dashArray: 4, 4`).
     - **Triángulos de $K_\alpha$**: Polígonos con un **relleno azul traslúcido muy suave** (opacidad del $22\,\%$).
   - **¿Cómo leerlo?**: Todo lo que se vea únicamente como línea punteada gris o sombra azulada tenue es estructura que **todavía NO ha nacido** en el umbral actual $t$ (su valor de filtración supera a $t$, es decir, $f(\sigma) > t$). Sirve como «molde» o «plantilla» del complejo final.

2. **Primer plano activo (`0-símplices`, `1-símplices` y `2-símplices` del subcomplejo $K_t$)**:
   - Sobre la plantilla fantasma se dibujan con **trazo continuo sólido y colores intensos** (según la paleta activa: `viridis`, `plasma`, etc.) únicamente los elementos que **ya han nacido en el umbral actual** ($f(\sigma) \le t$):
     - **Vértices activos ($f(v) \le t$)**: Círculos coloreados con borde definido e información interactiva al pasar el ratón (*tooltip*).
     - **Aristas activas ($f(e) \le t$)**: Segmentos continuos de grosor medio ($2\,\text{px}$) que tapan la línea discontinua gris de la capa fantasma a medida que se consolidan.
     - **Triángulos activos ($f(\tau) \le t$)**: Caras rellenas con el color correspondiente de la escala (opacidad $38\,\%$), que indican zonas donde el tejido espacial ya es continuo y bidimensionalmente compacto (sin agujeros internos entre esos tres nodos).

3. **Capa superpuesta de Topología de Dimensión 1 (`Agujeros H₁ vivos`)**:
   - En color **rojo brillante** se destacan los ciclos o vacíos unidimensionales que están abiertos en el instante exacto $t$ seleccionado (detallados en el apartado siguiente).

---

#### 4.2.3. ¿Qué significa la representación de $H_1$ (Agujeros Vivos) y cómo se interpreta en el mapa?

En Homología Persistente, el primer grupo de homología $H_1(K_t)$ captura los **ciclos independientes de aristas (lazos cerrados) cuyo interior todavía no está pavimentado por triángulos (2-símplices)**.

Cada clase homológica en $H_1$ posee un intervalo de vida $[b, d)$ calculado de forma exacta mediante reducción matricial sobre $\mathbb{Z}/2\mathbb{Z}$ en GUDHI:
- **Instante de nacimiento ($b$, *birth*)**: Valor del umbral en el que entra la **última arista** que cierra el camino circular por primera vez.
- **Instante de muerte ($d$, *death*)**: Valor del umbral posterior en el que entra el **último triángulo** que termina de tapar o rellenar el interior del lazo. Si incluso en el complejo máximo $K_\alpha$ el agujero sigue sin rellenarse por completo, el ciclo nunca muere dentro del rango estudiado y se dice que es una **clase esencial ($d = \infty$)**.
- **Persistencia ($p = d - b$)**: Duración o resistencia del vacío a lo largo de las escalas.

##### ¿Cuándo está «vivo» un agujero $H_1$?
Un agujero $H_1$ está **vivo en el umbral actual $t$** del deslizador si y solo si **ya ha nacido pero todavía no ha muerto**:
$$b \le t < d$$
La cantidad total de agujeros vivos en ese umbral $t$ coincide exactamente con el **primer número de Betti $\beta_1(t)$** mostrado en las tarjetas KPI y en la curva de Betti inferior.

##### ¿Qué significan los 3 elementos gráficos rojos que dibuja el mapa para cada agujero $H_1$ vivo?
Cuando la casilla **«Mostrar agujeros $H_1$ vivos en el umbral»** está activa, el mapa representa hasta los 20 agujeros vivos de mayor persistencia mediante tres elementos geométricos complementarios:

| Elemento visual en el mapa | Significado matemático (pares de persistencia) | ¿Cómo interpretarlo sobre la ciudad o los datos? |
| :--- | :--- | :--- |
| **1. Línea discontinua roja gruesa** (*Arista creadora / generador de nacimiento*) | Es el 1-símplex crítico $e_{\text{birth}}$ con $f(e_{\text{birth}}) = b$ que, al añadirse en el umbral $b$, cerró el circuito creando la clase de homología en $H_1$. | Muestra el **«puente» o eslabón que terminó de rodear el vacío**. Si esa única conexión se eliminara en el instante $b$, el anillo dejaría de estar cerrado. |
| **2. Triángulo sombreado en rojo translúcido** (*Triángulo matador / símplex de muerte*) | Es el 2-símplex crítico $\tau_{\text{death}}$ con $f(\tau_{\text{death}}) = d > t$ emparejado con $e_{\text{birth}}$ en el algoritmo de persistencia. Cuando el deslizador llegue en el futuro a $t = d$, este triángulo entrará y sellará definitivamente el ciclo. | **¡Atención pedagógica clave!**: En el umbral actual $t < d$, este triángulo **aún NO pertenece al complejo activo**; se dibuja en rojo para **localizar el corazón geométrico del vacío** (el último rincón del agujero que tardará más en cubrirse). *Nota*: Si el agujero no muere antes de $\alpha$ ($d = \infty$), no existe triángulo matador y solo se muestra la arista discontinua roja. |
| **3. Círculo rojo con borde blanco** (*Marcador de persistencia y consulta*) | Se ubica en el baricentro del triángulo matador (o en el punto medio de la arista creadora si $d = \infty$). Su **radio es proporcional a la persistencia $(d - b)$** del ciclo. | **Tamaño del círculo = importancia del vacío**: Un círculo rojo grande señala una **señal topológica estructural** (un gran parque, un cerro, el cauce de un río o un desierto de cobertura sanitaria); un círculo pequeño señala ruido local (una manzana pequeña). |

> **💡 Interacción con el ratón (*Tooltip* de $H_1$)**: Al situar el cursor sobre cualquiera de los tres elementos rojos (la arista discontinua, el triángulo rojo o el círculo central), se despliega una etiqueta emergente con:
> - **`H₁ #k`**: Posición en el ranking de los agujeros vivos más persistentes (`#1` es el vacío más importante presente en ese umbral).
> - **`nacimiento`**: Escala exacta $b$ en la que se cerró el ciclo.
> - **`muerte`**: Escala futura $d$ en la que se tapará el agujero (o `∞ (no se rellena)` si sobrevive hasta el final).
> - **`persistencia`**: Vida total $d - b$ del agujero.

---

#### 4.2.4. ¿Qué diferencia hay entre colorear por «Valor de filtración» o por «Centralidad betweenness»?

Es fundamental distinguir entre **qué filtra la presencia de los elementos** y **qué determina su color**:
- **¿Qué elementos se ven en el mapa?**: Lo decide exclusivamente la **Variable de filtración** junto con el **deslizador de umbral** ($f(\sigma) \le t$).
- **¿De qué color se pintan esos elementos activos?**: Lo decide el selector **«Colorear por»**, que permite alternar entre dos lecturas analíticas distintas sobre el mismo subcomplejo activo:

##### Opción 1: Colorear por `Valor de filtración` (Perspectiva cronológica o «edad de nacimiento»)
Asigna a cada símplex activo el color correspondiente al **umbral exacto en el que nació**, manteniendo la barra de colores fija en el rango completo $[0, \alpha]$ (o $[0, 1]$) para que el color de cada elemento sea constante al mover el deslizador:
- **En la filtración por `📏 Distancia`**:
  - Las **aristas activas** se colorean según su escala de entrada $f(e)$ en metros, y los **triángulos activos** según la escala $f(\tau)$ en metros a la que se rellenan.
  - Dado que en esta filtración todos los vértices tienen $f(v) = 0$, para evitar que todos los puntos tengan un único color uniforme irrelevante, cada **vértice** se colorea según su **distancia de primera conexión** ($\min_{e \ni v} f(e)$, es decir, los metros necesarios para que ese nodo deje de estar aislado y se conecte a su vecino más próximo; si un vértice permanece totalmente aislado en $K_\alpha$, toma el valor $\alpha$).
  - **¿Qué permite descubrir?**: Funciona como un **mapa de calor cronológico de densidades y alcances**. Los tonos del extremo inferior de la paleta (p. ej. violeta/azul en `viridis`) revelan los núcleos hiperdensos donde los nodos y manzanas se compactan a distancias muy cortas, mientras que los tonos del extremo superior (verde/amarillo) resaltan los enlaces largos de unión interdistrital y las caras que acaban de cerrarse cerca del umbral actual $\varepsilon$.
- **En las filtraciones por `⭐ / 🔻 Betweenness`**:
  - Colorea vértices, aristas y triángulos según su nivel de entrada $f(\sigma) \in [0, 1]$ en la filtración *lower-star*, mostrando como «anillos de crecimiento» qué elementos entraron en las etapas iniciales ($t \approx 0$) y cuáles acaban de incorporarse en la frontera del umbral actual.

##### Opción 2: Colorear por `Centralidad betweenness` (Perspectiva funcional o «jerarquía de flujo»)
Independientemente de cuándo nació cada elemento en la filtración, pinta todos los elementos activos según su **importancia de intermediación (*betweenness*) en el grafo global $K_\alpha$**:
- Los **vértices activos** muestran su centralidad $\text{BC}(v)$.
- Las **aristas y triángulos activos** muestran el **promedio de la centralidad *betweenness*** de los vértices que los componen.
- **¿Qué permite descubrir?**: Su mayor potencia pedagógica aparece cuando se combina con la **filtración por `📏 Distancia`**. De este modo se cruzan **dos dimensiones independientes en un único mapa**:
  1. **La geometría multiescala** (controlada por el deslizador $\varepsilon$, que muestra qué conexiones físicas existen a menos de $\varepsilon$ metros y qué agujeros $H_1$ están abiertos).
  2. **La jerarquía funcional de transporte/red** (mostrada por el color, que distingue qué tramos dentro de ese subcomplejo $\varepsilon$ son grandes corredores arteriales o puentes críticos de flujo frente a calles locales secundarias).

##### Tabla resumen comparativa

| Criterio | Colorear por «Valor de filtración» | Colorear por «Centralidad betweenness» |
| :--- | :--- | :--- |
| **Pregunta a la que responde** | *«¿A qué escala o en qué momento nació cada conexión y cada cara?»* | *«¿Qué importancia estratégica o de flujo tiene cada nodo y tramo activo en la red?»* |
| **Color de las aristas y triángulos** | Su propio umbral de aparición $f(e)$ o $f(\tau)$ en la filtración. | El promedio de la centralidad *betweenness* de sus vértices. |
| **Color de los vértices** | En distancia: escala $\varepsilon$ de su primera arista incidente ($\min_{e \ni v} f(e)$). En betweenness: su nivel de entrada $f(v)$. | Su valor de centralidad de intermediación $\text{BC}(v)$ en el 1-esqueleto. |
| **Uso recomendado** | Entender el crecimiento multiescala, identificar zonas densas (nacen pronto) frente a zonas dispersas (se conectan tarde). | Cruzar la escala métrica $\varepsilon$ con la jerarquía vial para ver qué arterias principales vertebran los componentes y rodean los agujeros $H_1$. |

---

#### 4.2.5. Indicadores KPI del Umbral y Curvas de Betti Sincronizadas

Debajo del mapa de la Pestaña 2 se actualizan en tiempo real dos bloques cuantitativos sincronizados con el deslizador:
1. **Banda de 8 Indicadores KPI en el umbral $t$**:
   - **Vértices activos, Aristas y Triángulos**: Conteo actual en $K_t$ comparado con el total disponible en $K_\alpha$.
   - **$\beta_0(t)$ (Componentes conexas)**: Número de islas o racimos desconectados entre sí en el umbral $t$.
   - **$\beta_1(t)$ (Agujeros vivos)**: Número exacto de ciclos independientes abiertos en el umbral $t$ (coincide con los agujeros $H_1$ vivos del mapa).
   - **$\chi(t) = V_t - E_t + F_t$**: Característica de Euler instantánea del subcomplejo $K_t$.
   - **Componente gigante (%)**: Porcentaje de los vértices activos que ya han quedado unidos dentro de la mayor componente conexa (permite detectar el **umbral crítico de percolación** de la red urbana).
   - **Grado medio**: Número medio de conexiones por vértice activo en el 1-esqueleto actual.
2. **Gráfico de Curvas de Betti ($\beta_0$ y $\beta_1$)**:
   - Traza la evolución continua de $\beta_0(t)$ (azul) y $\beta_1(t)$ (naranja) a lo largo de todo el dominio $[0, \alpha]$ o $[0, 1]$.
   - Incorpora una **línea vertical discontinua interactiva** que señala la posición exacta del deslizador del alumno, facilitando relacionar los picos y valles de las curvas con los cambios estructurales observados en el mapa.

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
5. **Auto-encuadre Reactivo en Pestañas Ocultas (`_AutoFitBounds` con `ResizeObserver`)**:
   - En Streamlit, las pestañas inactivas (`st.tabs`) se montan inicialmente en el DOM con `display: none` (dimensiones `0x0` píxeles), lo que provocaba que el método estándar `fitBounds()` de Leaflet calculara un zoom de nivel `0` (escala mundial) en la Pestaña 2. Mediante un observador `ResizeObserver` integrado en `MapBuilder`, el mapa detecta el instante exacto en que la pestaña pasa a ser visible y recalcula automáticamente `invalidateSize()` + `fitBounds()`, centrando y ajustando el zoom sobre el grafo sin intervención manual.

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
2. Crea un nuevo repositorio (por ejemplo, `TDA_seminario_mod1mod2`).
3. Conecta el repositorio local con GitHub y sube los cambios:
```bash
git remote add origin https://github.com/TU_USUARIO/TDA-Lima-App1.git
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

### ¿Por qué en los agujeros $H_1$ vivos de la Pestaña 2 se dibuja un triángulo rojo si el agujero aún está abierto?
Porque en homología persistente cada ciclo $H_1$ que muere en un umbral futuro $d > t$ está emparejado algebraicamente con un **único 2-símplex crítico** (el *triángulo matador* $\tau_{\text{death}}$). En el umbral actual $t$, ese triángulo **todavía no ha entrado en el subcomplejo activo** (por eso el agujero sigue vivo), pero se proyecta en rojo translúcido sobre el mapa para mostrarle al usuario **dónde está el epicentro del vacío** y cuál será la pieza exacta que terminará de sellarlo cuando el deslizador alcance $t = d$. Si el agujero es tan grande que ni siquiera en $K_\alpha$ llega a taparse ($d = \infty$), no existe triángulo matador y solo se dibuja en rojo discontinuo la *arista creadora* ($e_{\text{birth}}$).

### ¿Cuándo conviene colorear por «Valor de filtración» y cuándo por «Centralidad betweenness» en la Pestaña 2?
- Usa **«Valor de filtración»** cuando quieras responder a la pregunta *«¿qué partes de la red nacieron primero y cuáles acaban de formarse?»* (cronología multiescala y densidad local).
- Usa **«Centralidad betweenness»** cuando quieras cruzar la escala geométrica del deslizador con la **importancia funcional vial**, distinguiendo qué tramos del subcomplejo activo son arterias principales de flujo frente a calles locales.
