# Matriz de escalado inmediato — pipeline híbrido por tipo territorial

Estado: EXPERIMENTAL / NO OFICIAL. Fecha de corte: 2026-07-10.
Complementa `PLAN_ESCALADO_PIPELINE_HIBRIDO.md` del experimento v1: separa qué parte
del enfoque híbrido puede escalarse ya, qué requiere repetición y qué requiere decisión
humana. Métricas por zona: `metricas_estabilidad_desagregadas_v1.csv` y
`diagnostico_places_por_zona_corregido.csv` (verificadas).

"Escalar" significa correr el generador localmente y producir candidatos
experimentales; nunca publicar sin revisión humana ni tocar Fase 25/26.

## 1. Escalable ahora (patrones validados)

### 1.1 Núcleo compacto (estilo San Telmo)

Patrón: HDBSCAN estable (perturbaciones locales) ∩ consenso KDE multi-bandwidth →
concave hull; mezcla de fuentes y estabilidad de membresía por núcleo.

| Zona candidata | Evidencia a favor | Precauciones |
| --- | --- | --- |
| Palermo Soho | estabilidad local MEDIA (0,735); 44,6 % Places | epsilon cayó a fallback 0 en v1: correr grilla sin epsilon; sensibilidad global baja (0,309) → reportar eom vs. leaf |
| Recoleta | estabilidad local MEDIA (0,703); 47,3 % Places; confianza MEDIA | 29 celdas saturadas conocidas: los núcleos pueden estar subcapturados en densidad (no en forma); anotarlo en la salida |
| Microcentro (núcleos peatonales) | estabilidad local ALTA (0,958); 31,0 % Places (la más baja) | sensibilidad global ALTA (leaf/eom 0,187): la partición depende del método → publicar solo núcleos que coincidan entre eom y leaf; resolver DH-03 antes del mapa |

Gates obligatorios por zona antes de aceptar candidatos: ARI por bloques ≥ 0,55 con p10
reportado; % Places del núcleo ≤ % Places del universo + 10 pp; revisión visual sobre
callejero.

### 1.2 Corredor lineal (estilo Corrientes)

Patrón: eje vial local respaldado por puntos a 150 m + buffer variable por terciles +
perfil longitudinal.

| Zona candidata | Evidencia a favor | Precauciones |
| --- | --- | --- |
| Caseros/Barracas | eje real `CASEROS AV.` ya identificado como contenedor; estabilidad local ALTA (0,974) | **gate de fuentes fuerte**: 69,0 % Places, dependencia ALTA, confianza BAJA, universo chico (58 puntos: 18 F01/F02 + 40 Places). Solo publicar tramos donde F01/F02 respalde por sí solo; si no, tratar como señal, no corredor |
| Microcentro (eje posible) | ver 1.1 | evitar solape con Corrientes (DH-03) |

### 1.3 Señal exploratoria sin polígono (estilo Costanera)

Patrón: puntos + KDE + advertencia de fuente; sin polígono, sin marcadores como símbolo
principal.

- Aplicable de inmediato como **tratamiento por defecto** de cualquier zona o subzona
  cuya dependencia Places supere ~85–90 % o cuyo respaldo F01/F02 sea marginal
  (hoy: solo Costanera Norte está en ese extremo; Caseros/Barracas puede caer aquí si
  falla su gate).
- Precaución única: rotular siempre "oferta visible en plataforma externa; no
  delimitación" en la propia lámina.

### 1.4 Infraestructura transversal escalable ya

Automatizables sin decisión pendiente: detección multi-método, métricas de estabilidad
desagregadas (con p10 y mínimo, no solo medias), ablación de fuentes, perfiles
longitudinales, diagnóstico de bordes, QA de trazabilidad (conteo por membresía como
canónico). Los buffers siguen siendo orientativos (DH-12).

## 2. Requiere repetición antes de escalar

| Tipo | Zona piloto | Zonas en espera | Motivo |
| --- | --- | --- | --- |
| Red multinuclear | Belgrano (`ESPECIFICACION_REPETICION_BELGRANO.md`) | Palermo Hollywood (est. local BAJA 0,566), Villa Crespo (0,045), Chacarita (0,521), Caballito (leaf/eom 0,136) | robustez 0,39; ARI entre métodos 0,07; posible artefacto de contenedor |
| Frente gastronómico | Puerto Madero (`ESPECIFICACION_REPETICION_PUERTO_MADERO.md`) | (único caso del tipo) | cobertura 34,7 %; soporte incompleto confirmado por inventario de ejes |

Regla: ninguna zona del tipo multinuclear se corre antes de que la repetición de
Belgrano fije protocolo y criterios; el tipo frente no se replica hasta que Puerto
Madero tenga una opción elegida en DH-06.

## 3. Requiere decisión humana (no técnica)

- Nombres de núcleos y subtramos (DH-05; nunca automáticos).
- Jerarquías entre unidades (principal/secundario).
- Qué versión ocupa el mapa principal (DH-10).
- Relación con Fase 25 (DH-08): recomendación preliminar — complemento, Fase 25 como
  lectura general vigente.
- Tratamiento de puntos fuera de representación (DH-09): taxonomía de 6 categorías.
- Etiquetado humano de deduplicación (DH-11).
- Estatus de los anchos de buffer (DH-12).

## 4. No recomendado (cerrado salvo evidencia nueva)

1. **KMeans territorial** en cualquier variante (tiles, particiones, "k razonable").
2. **Macroenvolventes gigantes**: un hull por macrozona como "el polo".
3. **Polígono único para todos los tipos**: la tipología territorial (núcleo /
   corredor / multinuclear / frente / señal) es el hallazgo central del experimento;
   aplanarla lo desarma.
4. **Promoción de señales Places-only a polo firme** (Costanera y cualquier análogo):
   bloqueado por guardrail de fuentes.
5. **Cantidad de clusters como criterio de selección** de métodos, umbrales o
   parámetros (en v1 ningún umbral se eligió así; mantenerlo).

## 5. Secuencia sugerida (no vinculante)

1. Firmas rápidas: DH-02, DH-03, DH-04, DH-07, DH-08, DH-09, DH-12 (tienen
   recomendación con evidencia suficiente).
2. Corridas locales: repetición Belgrano + repetición Puerto Madero + soporte del eje
   Defensa (DH-01).
3. Escalado de patrones maduros: Palermo Soho, Recoleta, Microcentro (núcleos);
   Caseros/Barracas (corredor con gate).
4. Con todo lo anterior: DH-01, DH-05, DH-06 finales, DH-10/DH-11, y recién entonces
   plan de informe.
