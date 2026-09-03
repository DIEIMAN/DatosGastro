# Inventario de referencias cartográficas existentes (Etapa Infra-1)

**Fecha:** 2026-07-08 · **Carácter:** experimental, de solo lectura. No se generó ningún
polígono nuevo en esta etapa — es exclusivamente el relevamiento pedido antes de construir
nada.

## Conclusión ejecutiva (para no enterrarla)

**No existe en el proyecto, ni en fuentes oficiales externas, ningún polígono real de
macrozona gastronómica.** Ni siquiera el informe oficial vigente (Fase 25) usa límites
reales: sus "geometrías editoriales" son elipses dibujadas a ojo (`center/width/height/
angle`), documentadas honestamente como "no límite oficial". Construir contornos
editoriales reales no es recuperar algo que ya existe y se perdió: **es trabajo nuevo**,
aunque hay insumos parciales reutilizables (calles de referencia por polo, callejero real,
límites administrativos) que evitan empezar de cero.

## 1. Capas geográficas reales disponibles (precisas, reutilizables tal cual)

| Capa | Ruta | Qué es | Precisión | Cobertura |
|---|---|---|---|---|
| Barrios CABA | `PolosGastro/cartografia/barrios_caba.geojson` (= `data/raw/geo_barrios.geojson`) | 48 barrios oficiales (BA Data) | Alta, oficial | Toda CABA |
| Comunas CABA | `PolosGastro/cartografia/comunas_caba.geojson` (= `data/raw/geo_comunas.geojson`) | 15 comunas oficiales (Ley 1777) | Alta, oficial | Toda CABA |
| **Callejero GCBA** | `outputs/polos_gastro/fase15_mapas_callejeros_v3/assets/callejero_gcba_2026_06_02.geojson` | 31.961 tramos de calle, con `nomoficial`, `tipo_c` (calle/avenida/…), `red_jerarq` (local/distribuidora/troncal), `barrio`, `comuna` | Alta, oficial (GOED/GCBA, atribución OSM ODbL) | Toda CABA |

**Estos tres son la base sólida.** Ninguno delimita polos gastronómicos (los barrios y
comunas son administrativos; el callejero es la trama vial), pero el callejero es
exactamente lo necesario para **construir** contornos reales: nombrar las calles que
delimitan un polo y trazar el polígono sobre sus geometrías reales, en vez de aproximar
con una elipse o un hull de puntos.

## 2. Capa editorial existente — hand-authored, no derivada de calles reales

`outputs/polos_gastro/fase16_mapas_editoriales_v4/tablas/subzonas_editoriales_geometrias.geojson`
(21 features) es la capa que ya usan los tableros de validación de esta sesión y los mapas
oficiales desde Fase 16 hasta Fase 25. Se construyó (`scripts/polos_gastro/
build_fase16_mapas_editoriales_v4.py`) con **coordenadas de centro + ancho + alto + ángulo
elegidos a mano** para dibujar elipses (`Ellipse` de matplotlib), apoyándose visualmente en
el callejero y el universo semilla, no calculando la geometría real de ninguna calle.
Fase 17 (`fase17_mapas_geometrias_editoriales`) reestiliza estas mismas 5 macrozonas
(círculos para puntos, no para contornos) sin agregar precisión geométrica.

**Cobertura: solo 5 de 12 macrozonas** (Palermo/Las Cañitas, Puerto Madero, San Telmo,
Corrientes/Abasto, Belgrano). Las otras 7 (Villa Crespo, Chacarita, Recoleta, Caballito,
Costanera Norte, Caseros/Barracas, Microcentro y Centro) no tienen ninguna geometría
editorial, ni siquiera aproximada.

Cada feature ya declara `"observacion": "Subzona de trabajo; no límite oficial."` — el
propio proyecto nunca las presentó como límites reales.

## 3. Fichas de polos (`docs/polos_gastro/fichas_polos/`, 34 fichas)

Cada ficha tiene una sección **"12. Delimitación territorial preliminar"** con texto libre.
Es el insumo más valioso encontrado porque en dos casos da calles reales concretas:

| Ficha | Delimitación textual | Utilidad para trazar polígono real |
|---|---|---|
| PG001A Palermo Soho | **Scalabrini Ortiz, Córdoba, Juan B. Justo y Santa Fe** | Alta — 4 calles nombradas, se puede armar el polígono con el callejero |
| PG001B Palermo Hollywood | **Juan B. Justo, Dorrego, Santa Fe y Córdoba** | Alta — ídem |
| PG001C Las Cañitas | "Báez y calles aledañas, en Palermo" | Media — 1 calle eje, falta perímetro |
| PG003 Puerto Madero | "Antiguos docks; Av. Alicia Moreau de Justo" | Media — 1 eje, falta el otro lado |
| PG010 Caseros/Barracas | "Barracas / eje Caseros" | Baja — solo el eje |
| PG006A/B/C Belgrano (Barrio Chino / Bajo Belgrano / Belgrano R) | Solo nombre de subzona | Baja |
| PG002, PG004, PG005, PG007, PG008, PG015 (Villa Crespo, San Telmo, Chacarita, Recoleta, Caballito, Devoto) | Solo "Barrio X" | Baja — remite al barrio administrativo completo, no al polo |
| PG009 Costanera Norte, PG012 Av. Corrientes, PG014 Av. Boedo | **"No definida"** | Nula |
| PG011 Microcentro y Centro | "sin delimitación fina" | Nula |
| PG013 Abasto, PG016–PG022, PGF2 (Colegiales, Flores, Floresta, Montserrat, Parque Patricios, Retiro) | Solo nombre de zona/corredor | Baja |

**Solo 2 de 34 fichas (Palermo Soho y Hollywood) tienen las 4 calles necesarias para trazar
un polígono real sin criterio editorial adicional.** El resto necesita una decisión humana
(qué tramo, qué ancho de manzanas) apoyada en el callejero, no solo lectura de la ficha.

Nota adicional: las 34 fichas exceden ampliamente las 12-13 macrozonas usadas en el
prototipo V1 (que solo tomó las agrupaciones del PDF semilla: Palermo, Villa Crespo, etc.).
PG014 en adelante son **polos emergentes documentados pero nunca incorporados a ningún
contenedor de clustering** — coincide con el 53 % de entidades que en la validación
quedaron "fuera de macrozona" (Etapa V1-3): varias de esas entidades probablemente
pertenecen a estos polos emergentes (Devoto, Villa Urquiza, Flores, etc.) que hoy no tienen
contenedor ni geometría de ningún tipo.

## 4. Documento semilla (`PolosGastro/Polos gastronómicos.pdf`, 8 páginas)

Es el PDF de origen de todo el proyecto PolosGastro (referenciado en las fichas como "PDF
semilla de Fase 1"). Contenido verificado: **listas de texto** — 22 nombres de polo (página
1) y "locales destacados" por polo (páginas 2-8). **Cero imágenes, cero mapas, cero
coordenadas** (`get_images()` devolvió 0 en las 8 páginas). No aporta nada geométrico más
allá de lo que ya está digerido en las fichas.

## 5. Universo semilla de Fase 13 (`locales_para_mapa_revision.csv`, 106 puntos)

Tiene columnas `polo` y `subzona` por **punto**, no por polígono. Es la fuente que el
prototipo V1 usó para derivar los contenedores actuales (hull convexo + buffer) — ya
identificado en la validación como el eslabón más débil del pipeline. No sustituye a un
contorno editorial: es evidencia puntual de qué locales pertenecen a qué polo, útil como
**capa de control** (todo contorno nuevo debería seguir conteniendo estos puntos), no como
fuente de la geometría.

## 6. Fuentes cartográficas oficiales externas

`docs/polos_gastro/cartografia/FUENTES_CARTOGRAFICAS_CABA.md` (relevado 2026-06-29) ya
confirma que **no existe un dataset oficial de "polos gastronómicos"** en Buenos Aires
Data, USIG ni IDECBA: los datasets oficiales georreferenciados son barrios, comunas y el
geocodificador de direcciones. Los "polos gastronómicos" son una categoría editorial de
DGDGAS, no una demarcación del GCBA — confirma que este trabajo de digitalización tiene
que hacerse puertas adentro, no se puede descargar.

## 7. Herramientas técnicas ya instaladas (relevantes para la Etapa Infra-3)

- **`@usig-gcba/mapa-interactivo` (npm, ya instalado, v1.2.8)**: wrapper de Leaflet con base
  cartográfica oficial GCBA. Sirve para **visualizar** (mapa interactivo con capas
  oficiales), no para **editar geometrías**: no expone herramientas de dibujo/edición de
  polígonos, solo marcadores y capas. Documentado en
  `docs/polos_gastro/cartografia/USIG_MAPA_INTERACTIVO_NOTAS_TECNICAS.md` y con un
  prototipo aislado en `scripts/polos_gastro/cartografia_experimentos/
  usig_mapa_interactivo_minimo/`.
- **`leaflet` (npm, ya instalado)**: base de lo anterior; sin el plugin de dibujo
  (`leaflet-draw` o `geoman`) no permite editar vértices — ninguno de los dos está
  instalado hoy.
- **`.venv` (GeoPandas + matplotlib + shapely)**: ya se usó en todo el prototipo V1 para
  construir y visualizar geometrías; sirve para validar/renderizar, no para edición manual
  interactiva de vértices.

## 8. Qué se puede reusar vs. qué hay que construir

| Insumo | Estado | Rol en la capa editorial nueva |
|---|---|---|
| Callejero GCBA | Real, completo | Base para trazar cada polígono sobre calles reales |
| Barrios/Comunas | Real, completo | Contexto y validación de cobertura |
| Fichas §12 (Palermo Soho/Hollywood) | Real, 2 de 34 | Único caso con polígono trazable directo por calles |
| Fichas §12 (resto) | Parcial o nulo | Punto de partida para decisión editorial, no polígono |
| `subzonas_editoriales_geometrias.geojson` (fase16) | Aproximado (elipses) | Referencia visual de "dónde", no geometría final; útil como capa de comparación al validar los polígonos nuevos |
| Semilla Fase 13 (106 puntos) | Real (puntual) | Capa de control: todo contorno nuevo debe contenerlos |
| PDF semilla | Solo texto | Ninguno (ya digerido en fichas) |
| USIG mapa-interactivo / Leaflet | Instalado, sin edición | Candidato a visor, no a editor, salvo que se sume un plugin de dibujo |

Con esto, la Etapa Infra-2 (diseño de la capa) y la Etapa Infra-3 (herramienta de edición)
parten de una base concreta en vez de una hoja en blanco.
