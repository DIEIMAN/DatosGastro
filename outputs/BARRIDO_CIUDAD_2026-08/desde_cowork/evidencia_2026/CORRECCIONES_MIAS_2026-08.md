# Correcciones a material que ya cargué

*7 de agosto de 2026*

Tres cosas que escribí mal y quedan corregidas acá. Las dejo escritas porque el error ya está en archivos que el repositorio leyó.

---

## 1 · Bulevar Caseros no llega a Montes de Oca

En `diccionario_nombres_uso_corriente.csv` puse la extensión del Bulevar Caseros como **"Defensa a Av. Montes de Oca"**.

**Ninguna fuente sostiene eso.** Las dos fuentes que describen el bulevar como polo gastronómico —La Nación, 12 de enero de 2017, y El Cronista, 3 de noviembre de 2021— coinciden en que es **una sola cuadra, sobre Av. Caseros entre Defensa y Bolívar**, con la calle convertida en boulevard en 2007 y desembocando en el Parque Lezama. El Cronista lo ubica "a pocos metros de Parque Lezama", entre San Telmo y Barracas.

**Extensión correcta: Av. Caseros entre Defensa y Bolívar. Una o dos cuadras, máximo hasta Perú.**

De Bolívar a Montes de Oca hay más de diez cuadras que ninguna fuente describe.

Y una salvedad que hay que sumar a la ficha: **las dos únicas fuentes zonales son de 2017 y de 2021**. Cinco rutas de búsqueda no dieron una sola nota de prensa nacional sobre el Bulevar Caseros posterior a 2021. La vía E de R11 abre, pero abre **débil por antigüedad**, y conviene que la matriz lo registre así.

---

## 2 · El Distrito de Diseño no sirve como anclaje de nombre

En `PERIMETROS_NORMATIVOS.md` listé la Ley 4761 (Distrito de Diseño) entre los perímetros normativos que anclan el nombre de un polo.

**No corresponde. La Ley 4761 no incluye la gastronomía entre las actividades promovidas.** Es un distrito de promoción de diseño, no gastronómico. Que haya oferta gastronómica dentro de su perímetro no lo convierte en anclaje normativo para un polo gastronómico: el nombre "Distrito de Diseño" no tiene, en su norma, un gancho con nuestro objeto.

Queda fuera de la lista de anclajes. El polo puede seguir llamándose así por uso corriente —que es otro nivel del diccionario, y legítimo—, pero **no como nombre normativo**.

---

## 3 · La escala de niveles de la vía E no estaba escrita, y hacía falta

Los cuatro frentes de investigación de esta ronda usaron escalas de niveles ligeramente distintas para `via_E`, porque la escala no estaba fijada en ningún documento del proyecto. Uno puso a Time Out en e1; otro en e4. Eso no cambió ningún veredicto —los umbrales se aplicaron sobre el conteo de grupos independientes, no sobre el nivel— pero es una inconsistencia que hay que cerrar antes de consolidar la matriz.

**Escala adoptada, que queda fijada acá:**

| nivel | qué es | ejemplos |
|---|---|---|
| e1 | Guía gastronómica internacional con criterio editorial | Michelin Argentina, The World's 50 Best, Latin America's 50 Best, Gault&Millau Argentina |
| e2 | Prensa nacional o extranjera de circulación general que trata **a la zona** | La Nación, Clarín, Infobae, Perfil, Página/12, Ámbito, El Cronista, NYT, Guardian, Condé Nast, El País |
| e3 | Ranking o lista de terceros con método declarado | Time Out cuando publica ranking con método, listas comparativas con criterio publicado |
| e4 | Guía de turismo comercial | Lonely Planet, Time Out guía de barrio, Fodor's, Rough Guides |
| e5 | Food tour vendido comercialmente | GetYourGuide, Civitatis, Context Travel, Parrilla Tour, Culinary Backstreets |

**Time Out queda en e3 cuando publica un ranking con método declarado y en e4 cuando publica una guía de barrio.** No es e1: no es una guía gastronómica con criterio editorial de selección al modo de Michelin.

**Umbral:** abre con ≥2 grupos independientes de nivel e1–e4, o con 1 solo de nivel e1. Un solo e5 no abre.

**Y la regla que más veces hizo falta:** si un local de la zona tiene estrella o recomendación Michelin pero la zona no es tratada como destino, eso es **vía B**, no vía E. Michelin distingue restaurantes, no barrios.
