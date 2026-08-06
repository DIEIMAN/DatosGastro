# Reconciliación de la capa de hitos · qué de lo mío sirve y qué está duplicado

**6 de agosto de 2026** · Escrito después de leer `outputs/polos_gastro/REFERENTES_2026/`, que no
había mirado antes de armar `hitos_documentales_caba.csv`. **Buena parte de ese archivo es trabajo
duplicado y peor hecho.** Esto dice qué se descarta y qué sirve.

---

## Lo que ya existía, y está mejor

`REFERENTES_2026/` tiene **169 referentes geocodificados con USIG y asignados a las envolventes**,
con matriz final, conteos por referencia, cobertura de geocodificación, casos ambiguos, casos
fuera del Atlas y una propuesta de integración escrita.

| capa | REFERENTES_2026 | mi CSV | veredicto |
|---|---:|---:|---|
| **Bares Notables** | **84**, GCBA, 84/84 geocodificados | 90, del Boletín Oficial | **gana REFERENTES_2026** |
| **Restaurantes Icónicos GCBA** | **16**, 16/16 geocodificados | **0 — no lo tenía** | gana REFERENTES_2026 |
| **MICHELIN** | **58**, 57/58 geocodificados, **con Estrella Verde** | 58, sin geocodificar, sin Estrella Verde | **gana REFERENTES_2026** |
| Mercados y patios | 11, **sólo 2 con dirección** | 10, **8 con dirección** | se complementan |
| 50 Best | **0 — decisión explícita de no mostrar** | **16, del sitio oficial, con posición y fecha** | aporta lo mío |
| Pizzerías emblemáticas | 0 | 20 | aporta lo mío |
| Heladerías históricas | 0 | 5, confianza baja | aporta lo mío, con reservas |

Y el encuadre conceptual ya estaba escrito, mejor de lo que lo escribí yo: **«dos geografías
distintas»** —el Atlas mide concentración de oferta actual, los catálogos miden patrimonio y
distinciones vigentes, y no tienen por qué coincidir—. Eso es exactamente lo que yo formulé como
«la densidad de hitos mide dónde miran las guías». **Se usa la formulación que ya existe.**

## Lo que sí aporta mi capa · y son dos pendientes que estaban declarados

La propuesta de integración de REFERENTES_2026 deja dos cosas explícitamente abiertas. Las dos se
cierran con lo que traje:

**1 · «50 Best: no mostrar hasta reconstruir el catálogo primario completo y fechado.»**

Está reconstruido. **16 filas del sitio oficial de The World's 50 Best**, con posición y edición:

- Latin America's 50 Best Restaurants **2025**: 8 en el 1–50 (Don Julio 3, Niño Gordo 21, El
  Preferido 24, El Mercado 27, Aramburu 35, Trescha 36, Crizia 40, Julia 50) y 3 en el 51–100
  (Ness 64, Mishiguene 69, Gran Dabbang 70).
- The World's 50 Best Restaurants 2025: Don Julio, Nº 10.
- The World's 50 Best Bars 2025: Tres Monos 10, CoChinChina 26, Victor Audio Bar 87, Florería
  Atlántico 90.

**Y una exclusión que hay que conservar:** *Alo's* figura en la lista como «Buenos Aires» y está
en **Boulogne, San Isidro**. No es CABA. Es el mismo tipo de trampa que Kobito en Michelin
—listado bajo Buenos Aires, ubicado en San Isidro—.

**2 · «Mercados y patios: mantener sólo en la matriz documental hasta completar domicilios
exactos.»**

La cobertura era **2 de 11**. Traigo dirección para ocho: Mercado de San Telmo (Bolívar 954),
Mercado Belgrano (Av. Juramento 2527), Mercado Bonpland (Bonpland 1660), Mercado del Progreso
(Av. Rivadavia 5430), Patio de los Lecheros (Av. Tte. Gral. Donato Álvarez 175), Patio Costanera
Norte (Av. Costanera Rafael Obligado 7010), Patio Rodrigo Bueno (Av. España 2230) y Yiyo el
Zeneize (Av. Eva Perón 4402). Siguen sin dirección **Mercado San Nicolás** y **Smart Plaza Parque
Patricios**.

Con eso la cobertura puede pasar de 2/11 a ~9/11 y los mercados dejan de estar excluidos de los
conteos.

**3 · Dos categorías nuevas.** Pizzerías Emblemáticas Porteñas (APYCE + Ministerio de Desarrollo
Económico del GCBA, 20 entre las ediciones 2025 y 2026) y heladerías históricas de AFADHYA (5).
Las 20 pizzerías **no tienen dirección**: hay nombre y barrio, y hay que geocodificar por
nombre+barrio o descartarlas. AFADHYA es una cámara privada, no el GCBA — confianza baja, y las
pondría sólo si alguien las quiere.

## Y una discrepancia que conviene resolver

**Hay tres conteos distintos de Bares Notables y ninguno coincide:**

| fuente | filas |
|---|---:|
| `REFERENTES_2026` · catálogo GCBA | **84** |
| `dataset_bares_notables` · Wikidata (CC0) | **95** |
| mi lectura del catálogo consolidado del Boletín Oficial | **90** |

Wikidata declara ser un listado no exhaustivo, así que 95 > 84 es raro y probablemente incluya
altas o bajas que el catálogo del bloque GCBA no tiene. Los 90 míos incluyen 2 altas de agosto de
2026 que sólo tienen respaldo de prensa.

**No es un detalle de conteo: es la clase de divergencia silenciosa que este proyecto ya cazó tres
veces.** Vale una corrida corta que cruce las tres listas por nombre normalizado + dirección y
devuelva quién tiene qué, sin decidir todavía cuál manda.

---

## En una línea

De las 199 filas de `hitos_documentales_caba.csv`, **sirven 51**: 16 de 50 Best, 20 pizzerías, 5
heladerías y 10 de mercados —de las cuales 8 aportan la dirección que faltaba—. Las otras 148
—bares notables y Michelin— están mejor resueltas en `REFERENTES_2026/` y **se descartan**.

Tendría que haber leído el repositorio antes de salir a buscar. Es la misma regla que ya está
escrita: **antes de gastar, mirar el disco.**
