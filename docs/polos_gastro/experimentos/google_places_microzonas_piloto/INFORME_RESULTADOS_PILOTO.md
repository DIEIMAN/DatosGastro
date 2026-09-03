# Informe de resultados — piloto microzonas (Google Places + poligonización)

**Fecha:** 2026-07-09 · **Veredicto: PILOTO EJECUTADO** (379 consultas reales a Google
Places autorizadas por Diego, 0 errores + clustering y polígonos completos).
**EXPERIMENTAL — no oficial.**

## Qué se corrió

- **Contenedores:** 6 macrozonas de `macrozonas_editoriales_candidatas_v1` (Palermo
  Soho, Palermo Hollywood, Av. Corrientes, Microcentro y Centro, Belgrano, San Telmo).
- **Universo base:** 2.172 entidades F01+F02 aptas para clustering (del universo V1).
- **Enriquecimiento Places:** 379 consultas `searchNearby` en grilla acotada (0 errores,
  ≤ USD 13,27). De 3.511 puntos gastronómicos únicos devueltos: 626 quedaron fuera de
  la macrozona (descartados por contención estricta), 1.234 eran duplicados de F01+F02
  (15 m misma parcela, o 40 m + nombre compatible) y **1.651 entraron como puntos
  nuevos** — el universo piloto creció 76 %, a **3.823 puntos**.
- **Detección:** HDBSCAN por macrozona (parámetros del pipeline_microzonas_v1) + KDE de
  contraste. **Polígonos:** concave hull + buffer 35 m, recorte a macrozona, subdivisión
  KMeans si área > 18 ha o diámetro > 1.000 m (no corredor), descarte < 5 locales o
  < 1 local/ha.

## Resultado central: 78 microzonas chicas; la más grande mide 12,1 ha

Ningún polígono ocupa una macrozona entera (el problema del núcleo de 58 ha de la
validación anterior no reaparece). Descartes por gates: 0. Grandes no subdivisibles: 0.

| Macrozona | Puntos (F+P) | Places nuevos | Microzonas | Área máx. (ha) | % macrozona | % ruido |
|---|---|---|---|---|---|---|
| Av. Corrientes | 1.255 | +501* | 23 | 10,0 | 60,0 | 17,4 |
| Microcentro y Centro | 517 | +160* | 11 | 12,0 | 72,2 | 5,6 |
| Belgrano | 697 | +393 | 17 | 10,3 | 55,9 | 12,8 |
| Palermo Soho | 673 | +300* | 10 | 12,1 | 49,2 | 33,4 |
| Palermo Hollywood | 361 | +148* | 9 | 11,1 | 46,6 | 27,1 |
| San Telmo | 320 | +149 | 8 | 6,5 | 25,9 | 33,8 |

\* Los Places nuevos se registran por zona piloto (Corrientes+Microcentro = 661;
Soho+Hollywood = 448); el reparto por macrozona sale de la diferencia de puntos.

## Qué zonas mejoraron con Places

- **Belgrano** es la gran ganadora: +393 puntos sobre 304 (+129 %). El ruido bajó de
  3,3 % a 12,8 %… pero sobre un universo mucho mayor; en términos absolutos los núcleos
  se consolidaron y la subdivisión bajó de 15 piezas artificiales a 17 con estructura
  más real (5 clusters brutos en vez de 2).
- **San Telmo** (+87 %) y **Palermo** (+76 %): los núcleos existentes se densificaron y
  aparecieron mixtos (F01+F02 + Places en el mismo polígono), lo que valida que ambas
  fuentes ven la misma estructura territorial.
- **Corrientes/Microcentro** (+59 %): la zona con mayor cobertura registrada previa era
  la que menos margen tenía para crecer; aún así el máximo de área BAJÓ (16,6→10,0 ha en
  Corrientes) porque la densidad extra define mejor los núcleos.

## Los polígonos, ¿chicos o gigantes?

**Chicos.** Rango final: 0,9–12,1 ha, mediana ~4–6 ha según zona. Cobertura de macrozona
entre 25,9 % (San Telmo) y 72,2 % (Microcentro). El 72 % de Microcentro no es un cluster
gigante: son 11 piezas ≤ 12 ha en una macrozona que es casi toda densa — coherente con
que Microcentro ya se recortó descontando la franja de Corrientes.

## Limitaciones (leer antes de usar)

1. **Cortes de subdivisión KMeans = particiones geométricas, no fronteras reales** (8
   clusters subdivididos, sobre todo en Corrientes y Belgrano). Sirven para acotar
   tamaño; nombrar subzonas requiere revisión editorial.
2. **Places mide prominencia, no censo:** máx. 20 resultados por celda de 135 m — en
   corredores muy densos la celda se satura y lo devuelto es lo más prominente.
3. **Bug de sklearn 1.9:** Palermo Soho corrió con epsilon 0 (fallback documentado en
   `qa_clusters_piloto.json`); las otras 5 con epsilon 50 m normal.
4. **Fuentes separadas:** cada punto lleva su columna `fuente`; los conteos por fuente
   están en `qa_universo_piloto.json`. F01+F02 y Places NO se presentan como un mismo
   universo.
5. **No oficial:** no reemplaza mapas ni informes vigentes; los polígonos requieren
   revisión humana (DGDGAS).

## Qué falta para escalar

1. Revisión editorial de los cortes de subdivisión (Corrientes K01/K03, Belgrano).
2. Extender la grilla Places a las 8 macrozonas restantes (~500–700 consultas más,
   estimar con el mismo script en dry-run) una vez validado este piloto.
3. Resolver el bug de epsilon de sklearn (fijar versión o merge post-hoc a 50 m).
4. Decidir el rol institucional del dato Places (enriquecimiento experimental vs. capa
   estable con refresco periódico) — hoy es una foto del 2026-07-09.

## Archivos

- `outputs/.../google_places_microzonas_piloto/UNIVERSO_PILOTO_SANITIZADO.csv` (3.823 filas)
- `outputs/.../MICROCLUSTERS_PILOTO.geojson` · `POLIGONOS_MICROZONAS_PILOTO.geojson` (78)
- `outputs/.../mapas/mapa_piloto_*.png` (4 zonas, QA visual hecho)
- `outputs/.../qa_universo_piloto.json` · `qa_clusters_piloto.json`
- `outputs/.../places/plan_consultas_places.csv` · `places_sanitizado.csv` (sin place_id)
- `outputs/.../interno/` (place_id y campos técnicos; **gitignoreado, no publicable**)
