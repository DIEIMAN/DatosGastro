# Diagnóstico — Por qué DBSCAN global dejó 47.3 % de ruido (tanda 1)

**Fecha:** 2026-07-07 · **Carácter:** documento interno del experimento auxiliar de clustering.
Los resultados citados son exploratorios; **no constituyen límites oficiales**.

## 1. El hecho

En la tanda 1, DBSCAN global (eps=400 m, min_samples=3) sobre 93 puntos válidos dejó
44 puntos (47.3 %) como ruido. La grilla ampliada de esta tanda (45 combinaciones,
`parametros_probados_dbscan_v2.csv`) confirma que no era una mala elección puntual:
**ninguna configuración con min_samples ≥ 3 y eps ≤ 500 baja del 43 % de ruido.**

## 2. Causas, por orden de peso

1. **Universo semilla ralo (causa principal).** 93 puntos repartidos en 13 polos dan ~7
   puntos por polo sobre ~200 km² de ciudad. DBSCAN detecta densidad; con esa densidad de
   muestreo, la mayoría de los puntos no tiene 2–3 vecinos a 150–400 m. No es un defecto del
   algoritmo: es la resolución del insumo. Los locales semilla fueron **seleccionados por
   criterio editorial, no como universo censal** — el muestreo no fue diseñado para densidad.
2. **Densidades heterogéneas entre zonas.** Palermo Soho concentra 13–14 puntos en pocas
   manzanas; Microcentro tiene 7 puntos desparramados en un área similar. Un único eps global
   no puede servir a ambos: el que funciona en Soho deja a Microcentro entero como ruido
   (7/7 en la tanda 1).
3. **Corredores lineales.** Avenida Corrientes y Caseros/Barracas son ejes, no manchas.
   La vecindad circular de DBSCAN corta un corredor en pedazos o lo manda a ruido.
4. **min_samples exigente en relación al insumo.** Con ~7 puntos por polo, exigir 4–6
   vecinos elimina casi toda estructura (95–100 % de ruido en la grilla). El piso útil es 3;
   con 2, los "clusters" son pares sueltos (evidencia débil, ver §5).
5. **Sedes mal geolocalizadas.** 10 puntos quedaron apartados de su zona editorial
   (sucursales o matches de sede dudosos de Fase 11). Aislados de su grupo real, engrosan el
   ruido o contaminan clusters ajenos.
6. **eps chico, solo en parte.** Subir eps reduce ruido, pero el remedio es peor pasado un
   umbral: con eps ≥ 800 m se fusionan zonas distantes (diámetros internos de 3.2–5 km;
   con eps=1000/ms=3 un cluster dominante absorbe 39 puntos ≈ Palermo + Villa Crespo +
   Chacarita encadenados).

## 3. Qué significa ese ruido

En este contexto, "ruido" = **punto sin acompañamiento local suficiente a la distancia
elegida**, no dato inválido ni local irrelevante. Un local semilla aislado puede ser
perfectamente representativo de su polo; simplemente el muestreo alrededor es escaso.

## 4. Por qué no invalida el experimento (pero sí limita esa salida)

- No lo invalida: los clusters que sí emergen son concentraciones reales del universo
  semilla (San Telmo, Villa Crespo, subnúcleos de Palermo), y el ruido mismo resultó
  informativo (delató sedes mal geocodificadas y corredores sin masa).
- Sí limita: una capa donde casi la mitad de los puntos queda sin asignar no sirve como
  representación de las zonas para revisión editorial — deja polos enteros sin polígono
  (Microcentro, Caballito, Chacarita en la tanda 1).

## 5. Qué se prueba en esta tanda (v2)

1. **Grilla ampliada** (eps hasta 1000 m, min_samples desde 2) con métricas de fusión
   (diámetro interno máximo) para elegir con evidencia y no solo por menor ruido:
   - min_samples=2 se descartó: fragmenta en pares/miniclusters (evidencia débil);
   - eps ≥ 800 se descartó: fusiona zonas distantes aunque el ruido baje a 10–22 %.
2. **Tres candidatas DBSCAN** en vez de una: estricta (500/4), equilibrada (400/3, la de
   la tanda 1, para comparabilidad) e inclusiva (650/4, ruido 29 % sin bandera de fusión).
3. **Poligonización asistida por polo/subzona** (estrategia B): usa las etiquetas
   editoriales existentes para agrupar, con depuración de sedes apartadas, hull prudente por
   grupo y atributos de confianza. Elimina por construcción el problema del ruido y garantiza
   un polígono por zona conocida — a cambio de no poder descubrir concentraciones nuevas.
