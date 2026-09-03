# HANDOFF · Ronda 21 · Los seis repartos aplicados y la fusión verificada · 2026-08-10

Continúa la ronda 20 (`outputs/BARRIDO_CIUDAD_2026-08/ronda_20/CIERRE_RONDA_20.md`).
Rama `mercados-gastronomicos-v2`. **Google Places: 0 requests.** Nada commiteado: el commit lo
hace Diego.

**El documento entero de esta tanda está en
`outputs/BARRIDO_CIUDAD_2026-08/ronda_21/CIERRE_RONDA_21.md`.** Esto es sólo el mapa para retomar.

---

## Lo que quedó hecho

| parte | qué | estado |
|---|---|---|
| A | los cinco repartos contenidos, con la unión recalculada | hecho · `repartos_cifras_finales.csv` |
| B | Chacagiales, la fusión de R09 + R19 + Z43 | hecho · **verifica**, atlas en 39 |
| C | los bordes de los cuatro sin borde propio | hecho · cierran 3 piezas de 9 |
| D | la capa de reconocimiento regenerada, 215 → 220 | hecho · las 2 correcciones a mano confirman |
| E | las calles de los 23 contornos, con alturas | hecho · 2.279 tramos |
| F | `.gitattributes` | escrito · **el `--renormalize` no corrió** |

### Las cifras nuevas del conjunto

    suma de los 41 por separado   12.105 → 11.403 locales
    unión de los 41               10.819 locales · 5.444,15 ha   (NO cambia, y eso valida el reparto)
    se cuentan de más              1.286 → 584 veces sobre 562 locales
    pares con solape                  25 → 20
    con la fusión, el atlas queda en 39 polos: 11.119 sumados, 10.819 en la unión,
    300 de más sobre 300 locales, 12 pares con solape

---

## Lo primero que hay que mirar al retomar

1. **Warnes.** El eje corre este-sudeste a oeste-noroeste, así que no tiene flanco «este»: la
   frase de la decisión nombra algo que no existe. El reparto medido le da 41,63 ha y 77 locales a
   **La Paternal** y 8,05 ha y 14 locales a **Villa Crespo**, igual a cinco radios distintos. La
   **variante espejo está medida y no adoptada** (R08 327,40 ha · 809 loc · R21 343,71 ha · 230
   loc): cambiarla cuesta una firma. Y Av. Warnes **no es el límite entre los dos barrios**: los
   dos comparten 127,9 m de borde y sólo 5 corren sobre Warnes.
2. **La cuenta del Microcentro cambia dos veces** —21 → 22 por la capa regenerada y 22 → 14 por
   los repartos—. Las dos son correctas y son de momentos distintos.
3. **El `git add --renormalize .` está pendiente** por un `.git/index.lock` de las 22:32 con
   procesos `git.exe` vivos. No se borró un lock ajeno a propósito.
4. **Siete archivos que git ve modificados tienen cambios de contenido reales**, no de fin de
   línea. Mirarlos antes de commitear.

---

## Lo que espera decisión de Diego

- **La orientación de A5 (Warnes)**: como se adoptó, o la variante espejo.
- **Los tres bordes que cierran en C** —el núcleo coreano de Retiro, el corredor Arroyo y el
  corredor de Crisólogo Larralde—: medidos y **no adoptados**.
- **La fusión Chacagiales**: verifica contra el mapa. Falta la firma que la publica y las tres
  páginas reescritas como sistema + subzonas, con el modelo de Palermo.
- **El borde de R21 La Paternal**, que mete 69 ha dentro del barrio Villa Crespo y 12 dentro de
  Caballito. No es de esta ronda, pero el reparto lo dejó a la vista.

## Lo que hay que escribir, y ya tiene el material

- **Los 23 perímetros** de la parte E. Cuatro páginas se escriben de corrido —La Boca · Caminito,
  Villa Santa Rita, Mataderos y Colegiales—; Av. Corrientes **no se escribe listando calles**
  porque su contorno es el de un corredor.
- **Las cuatro calles que le faltan a Villa Santa Rita** ya están medidas: Condarco, Av. Gaona,
  Joaquín V. González y Miranda, además de la Av. Álvarez Jonte que su página ya nombra.
- **Lo que falta nombrar** en las otras cinco piezas que no cierran, en `bordes_de_los_cuatro.csv`.

---

## Lo que sigue abierto de rondas anteriores y esta tanda no tocó

Sigue valiendo el punto 7 del cierre de la ronda 20: las contradicciones internas de páginas —las
dos superficies de Av. Montes de Oca, el «sin borde dibujado» de Barracas sobre Iriarte, las dos
piezas del perímetro escrito de Balvanera contra una sola dibujada— y el bloque «Dónde está» de La
Boca sobre Almirante Brown, que sigue citando el tramo de 340 metros. Son de redacción.

Y Mataderos sigue con borde transitorio, por lo de siempre: lo que lo cerraría es el perímetro de
ocupación de la Feria, que es un dato administrativo que este repositorio no tiene.
