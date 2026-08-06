"""Junta el material bruto para el documento del método. Sin prosa: archivos y un índice.

QUÉ ES Y QUÉ NO
---------------
La redacción del documento extenso del método la toma Diego. Este script NO redacta: reúne en una
sola carpeta las tablas que hoy están repartidas entre `generado/`, `borrador_polos/` y las
corridas de `polos_gastro/`, y deja un índice que dice qué es cada archivo y de qué script salió.

El índice es una tabla, no un texto. Lo único que se agrega a los datos son las **fórmulas** de los
dos indicadores de parejidad, porque un CSV con una columna llamada `cobertura` no dice cómo se
calculó y eso es justamente lo que el documento tiene que poder explicar.

Los archivos se COPIAN, no se mueven ni se enlazan: el documento se va a escribir contra un estado
congelado, y que una corrida posterior le cambie una tabla abajo sería peor que duplicarla.

USO
---
  .venv/Scripts/python.exe scripts/barrido_ciudad/volcar_material_metodo.py
"""
from __future__ import annotations

import shutil
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
BARRIDO = ROOT / "outputs" / "BARRIDO_CIUDAD_2026-08"
GEN = BARRIDO / "generado"
POLOS = BARRIDO / "borrador_polos"
V3 = ROOT / "outputs" / "polos_gastro" / "corrida_territorial_v3"
TESTS = ROOT / "tests"
# Salida interna de la sonda de Places, ignorada por Git. De acá sale SÓLO el agregado por barrio
# —conteos, sin un solo punto ni identidad—, que es el nivel `agregado` de la tabla de licencias de
# R6: «sólo el conteo en una celda o zona, cuando el dato existe únicamente en una fuente no
# redistribuible». Los puntos y los crudos NO se copian y no salen de esa carpeta.
INTERNO = ROOT / "outputs" / "analisis_interno" / "places_sonda_barrios_2026-08"
DESTINO = BARRIDO / "material_metodo"

# (archivo origen, nombre destino, qué es, de qué script salió)
MATERIAL = [
    # --- curvas de sensibilidad
    (POLOS / "curva_continuidad_seis.csv", "curva_continuidad_seis_enteros.csv",
     "Barrido de continuidad de los 6 polos que `leaf` no partió, más los 4 controles positivos. "
     "Umbrales 40–300 m, componentes conexas y tamaños.",
     "polos_particion_anada_estructura.py"),
    (POLOS / "curva_continuidad_p065.csv", "curva_continuidad_p065.csv",
     "Barrido de P065. Incluye `pct_locales_en_esas_componentes`, la columna que distingue una "
     "partición de un estallido.", "polos_p065_union_y_clases.py"),
    (POLOS / "curvas_continuidad_polos_grandes.csv", "curva_continuidad_polos_grandes.csv",
     "Barrido de los 4 polos de 300+ locales buscando PARTES nombrables (regla de Belgrano). "
     "Grilla extendida a 20–300 m.", "polos_partes_nombrables.py"),
    (POLOS / "partes_nombrables_detalle.csv", "partes_nombrables_detalle.csv",
     "Las partes encontradas, aceptadas y al filo, con barrios y zona publicada encima.",
     "polos_partes_nombrables.py"),
    (POLOS / "partes_nombrables_resumen.csv", "partes_nombrables_resumen.csv",
     "Veredicto por polo grande: partes, umbral adoptado, aceptada o al filo.",
     "polos_partes_nombrables.py"),
    (POLOS / "justificacion_grilla_continuidad.csv", "justificacion_grilla_20_300m.csv",
     "Por qué la grilla baja a 20 m: distancia media al vecino observada contra la predicción de "
     "Poisson 1/(2·√λ), por polo grande. `piso_viejo_sobre_vecino` es la lectura operativa — "
     "cuando pasa de 2, el umbral más bajo de la grilla vieja ya conecta todo.",
     "justificar_grilla_continuidad.py"),
    (POLOS / "JUSTIFICACION_GRILLA_CONTINUIDAD.txt", "justificacion_grilla_20_300m.txt",
     "El argumento en texto: la distancia entre vecinos escala con 1/√densidad, así que un piso "
     "de 40 m es un umbral DISTINTO según la densidad del polo. Incluye un resultado no buscado: "
     "el orden por densidad nominal y por vecino observado NO coinciden, y el caso que los separa "
     "es P065 — control independiente de su encadenamiento.",
     "justificar_grilla_continuidad.py"),
    # --- P078: dónde caen los 123 que quedan afuera de las tres partes
    (POLOS / "p078_sueltos_ubicacion.csv", "p078_sueltos_ubicacion.csv",
     "Los 123 locales de P078 fuera de sus tres partes, uno por uno: parte más cercana y segunda, "
     "distancias, ángulo, si está entre dos partes y si cae adentro del envolvente conjunto. Es la "
     "prueba que REFUTÓ la lectura de que fueran los tramos sin oferta de R01.",
     "polos_p078_donde_caen_los_123.py"),
    (POLOS / "p078_sueltos_reparto.csv", "p078_sueltos_reparto.csv",
     "El reparto de esos 123 por parte más cercana, contra la cuota de locales de cada parte.",
     "polos_p078_donde_caen_los_123.py"),
    (POLOS / "P078_DONDE_CAEN_LOS_SUELTOS.txt", "p078_donde_caen_los_sueltos.txt",
     "La corrida completa, con la lectura declarada ANTES de correr y el veredicto NO CONFIRMA. "
     "Sirve como ejemplo de R1: la banda estaba escrita, el número cayó del lado que no se "
     "esperaba, y el veredicto lo eligió el número.",
     "polos_p078_donde_caen_los_123.py"),
    # --- P078: las tres pruebas de «cuándo dos polos son uno», corridas por primera vez
    (POLOS / "p078_curva_estabilidad.csv", "p078_curva_estabilidad.csv",
     "La curva de estabilidad de P078 cada 5 m, formato Belgrano. Es la que decidió: 3 partes sólo "
     "existen entre 40 y 60 m (20 m de ancho contra los 60 exigidos) y en la ventana ±40 m el "
     "conteo toma los valores 0, 1, 2 y 3. VEREDICTO: partición ARBITRARIA, P078 va entero.",
     "polos_p078_prueba_estabilidad.py"),
    (POLOS / "p078_vacios_entre_partes.csv", "p078_vacios_entre_partes.csv",
     "Los vacíos entre las tres partes, formato Recoleta, con las DOS distancias. Muestra por qué "
     "no son intercambiables: S1–S2 da 8,2 m entre envolventes y 60,5 m entre puntos. La de "
     "envolventes mide una arista tendida sobre un vacío, no continuidad.",
     "polos_p078_prueba_estabilidad.py"),
    (POLOS / "p078_prueba3_nombres.csv", "p078_prueba3_nombres.csv",
     "Prueba 3: calles dominantes y zona publicada por parte. S1 y S3 comparten Humboldt, Fitz Roy "
     "y Bonpland —el mismo lugar partido por Av. Niceto Vega— y no aparece ninguna calle de Soho: "
     "P078 es Palermo Hollywood, no Soho + Hollywood + Cañitas.",
     "polos_p078_prueba_estabilidad.py"),
    (POLOS / "saliente_p078_distancias.csv", "saliente_p078_distancias.csv",
     "Los tres bloques del saliente medidos contra TODOS los polos del borrador, con distancia "
     "entre envolventes y entre puntos. El polo externo más cercano a bloque_35 está a 315,7 m: el "
     "precedente Recoleta no aplica.",
     "polos_saliente_p078_de_quien_es.py"),
    # --- el registro de lo que no calificó
    (POLOS / "CANDIDATOS_BAJO_MINIMO.csv", "candidatos_bajo_minimo.csv",
     "Todos los conglomerados de 25–39 locales, por contigüidad a 55 m, con barrio, comuna, polo "
     "más cercano y zona publicada. Es el antídoto de «no se identificaron polos en X». LEER "
     "PRIMERO la sensibilidad: el conteo pasa de 1 a 14 a 18 entre 40, 55 y 70 m.",
     "polos_candidatos_bajo_minimo.py"),
    (POLOS / "candidatos_bajo_minimo_sensibilidad.csv", "candidatos_bajo_minimo_sensibilidad.csv",
     "La sensibilidad al umbral del registro anterior. Va junto y no aparte: el registro es lo que "
     "se ve a 55 m, no una propiedad del territorio.",
     "polos_candidatos_bajo_minimo.py"),
    (POLOS / "MATRIZ_DECISION_BORRADOR.csv", "matriz_decision_borrador.csv",
     "Las seis decisiones de esta tanda con sus números, INCLUIDA la excepción de P078 registrada "
     "como refutada. Una excepción medida y caída vale más que una que nunca se puso a prueba.",
     "registro a mano"),
    # --- foco menor: el atributo que registra una decisión humana
    (POLOS / "polos_foco_menor.csv", "polos_foco_menor.csv",
     "El foco secundario de P103 con su evidencia y el motivo por el que NO se publica como "
     "subzona. Ejemplo de un campo deliberadamente SIN umbral numérico: Belgrano (publicado, con "
     "partes) da 21,5 % y P103 da 15,2 %, así que la proporción no separa los casos.",
     "polos_foco_menor.py"),
    # --- uniones
    (POLOS / "union_100m_candidatas.csv", "union_100m_candidatas.csv",
     "Los 39 pares a menos de 100 m con su veredicto: continuidad, estabilidad, y motivo de "
     "rechazo. Incluye `evaluado_como`, que muestra la no-transitividad.",
     "polos_p065_union_y_clases.py"),
    # --- ablación
    (POLOS / "ablacion_por_grupo.csv", "ablacion_por_grupo.csv",
     "Ablación por grupo de independencia CON control aleatorio (5 sorteos, semilla fija). "
     "Columnas `colapsos_azar` y `polos_azar_mediana` son el control.",
     "borrador_polos_ciudad.py"),
    (POLOS / "sensibilidad_umbral.csv", "sensibilidad_grilla_hdbscan.csv",
     "Grilla 5×3 de min_cluster_size × min_samples, con la marca de colapso.",
     "borrador_polos_ciudad.py"),
    # --- clases y robustez
    (POLOS / "clases_densidad_ajuste.csv", "clases_jenks_gvf.csv",
     "Bondad de ajuste (GVF) de Fisher–Jenks para k = 2..6 y sus cortes.",
     "polos_atributos_clases.py"),
    (POLOS / "anada_contra_densidad.csv", "anada_contra_densidad.csv",
     "Por polo: densidad con todas las fuentes y sin el Relevamiento, clase en cada una, si "
     "cambió de clase, distancia al corte y añada.", "polos_particion_anada_estructura.py"),
    (POLOS / "anada_contra_densidad_resumen.json", "anada_contra_densidad_resumen.json",
     "eta², Kruskal–Wallis, Spearman y Rand ajustado de la prueba de añada.",
     "polos_particion_anada_estructura.py"),
    # --- partición
    (POLOS / "particion_encadenados.csv", "particion_encadenados.csv",
     "Los 10 polos candidatos a partir y qué pasó con cada uno.", "polos_atributos_clases.py"),
    (POLOS / "particion_sueltos_por_padre.csv", "particion_sueltos_por_padre.csv",
     "Dónde cayeron los 1.064 locales sueltos, por polo padre.",
     "polos_particion_anada_estructura.py"),
    (POLOS / "particion_bloques_de_sueltos.csv", "particion_bloques_de_sueltos.csv",
     "Los 6 grupos de sueltos que llegan a 40, con posición respecto de la cáscara y densidad.",
     "polos_particion_anada_estructura.py"),
    # --- cotejo y zonas
    (POLOS / "siete_zonas_explicacion.csv", "zonas_no_encontradas_explicacion.csv",
     "Las 22 zonas con su explicación asignada (E1/E2/E3) y la regla que la asignó.",
     "polos_atributos_clases.py"),
    (POLOS / "zonas_22_densidad.csv", "zonas_22_densidad.csv",
     "Las 22 publicadas medidas con la misma base: densidad por perímetro y por hull propio.",
     "polos_atributos_clases.py"),
    (POLOS / "cotejo_22_zonas_v3.csv", "cotejo_22_zonas_final.csv",
     "Cotejo final contra las 22, con familia del Atlas.", "polos_p065_union_y_clases.py"),
    (POLOS / "sensibilidad_piso_absoluto.csv", "sensibilidad_piso_absoluto.csv",
     "Piso absoluto a 2/4/6 loc/ha: polos y zonas publicadas que caerían con cada uno.",
     "polos_atributos_clases.py"),
    # --- lotes replicados y prueba catastral
    (GEN / "lotes_permisos_detectados.csv", "lotes_replicados_detectados.csv",
     "Detector de asientos replicados en el padrón: los lotes encontrados.",
     "detectar_lotes_permisos.py"),
    (GEN / "lotes_permisos_replicacion.csv", "lotes_replicados_replicacion.csv",
     "Detalle de la replicación por lote.", "detectar_lotes_permisos.py"),
    (GEN / "prueba_smp_lotes.csv", "prueba_catastral_smp.csv",
     "Prueba por partida catastral (SMP) del 22,6 % de asientos replicados.",
     "probar_smp_lotes.py"),
    (GEN / "mecanismo_smp.json", "prueba_catastral_mecanismo.json",
     "El mecanismo identificado detrás de la replicación.", "probar_smp_lotes.py"),
    (GEN / "discriminancia_smp.csv", "prueba_catastral_discriminancia.csv",
     "Discriminancia del SMP como clave.", "probar_smp_lotes.py"),
    # --- factores de captura
    (GEN / "factor_captura_22_zonas_dos_bases.csv", "factor_captura_dos_bases.csv",
     "Factores de captura contra las DOS bases, que es la comparación que corresponde.",
     "estimar_costo_places.py / capa_rus_por_zona.py"),
    (GEN / "factor_captura_22_zonas.csv", "factor_captura_una_base.csv",
     "Factores de captura contra una sola base. Se incluye para mostrar la diferencia.",
     "capa_rus_por_zona.py"),
    # --- parejidad
    (GEN / "parejidad_a_parcelas_comerciales.csv", "parejidad_a_por_barrio.csv",
     "Indicador A por barrio: cobertura, composición, aporte de las otras fuentes, añada.",
     "parejidad_cobertura.py"),
    (GEN / "parejidad_b_por_barrio.csv", "parejidad_b_por_barrio.csv",
     "Indicador B por barrio: locales cada mil habitantes (Censo 2022).",
     "parejidad_cobertura.py"),
    (GEN / "parejidad_b_por_comuna.csv", "parejidad_b_por_comuna.csv",
     "Indicador B por comuna, que es la unidad de referencia (el radio censal no se reparte).",
     "parejidad_cobertura.py"),
    # --- Places
    (BARRIDO / "places_criterio_destino" / "indicadores_por_barrio.csv",
     "places_criterio_indicadores.csv",
     "Los dos indicadores internos con los que se eligieron los barrios de la sonda.",
     "places_criterio_destino.py"),
    (BARRIDO / "places_criterio_destino" / "dry_run.json", "places_dry_run.json",
     "El dry-run que se usó para pedir autorización.", "places_criterio_destino.py"),
    (INTERNO / "places_resumen_nucleo_comparable.csv", "places_sonda_resultado_nucleo.csv",
     "EL RESULTADO DE LA SONDA, sobre el universo comparable (sólo anillo núcleo). 121 locales "
     "nuevos sobre los 1.128 de la base en esos 5 barrios = 10,7 %. DOS CALIFICACIONES QUE VAN "
     "PEGADAS AL NÚMERO: (1) es una COTA SUPERIOR, no un promedio — los 5 barrios se eligieron "
     "por ser los peores con criterio declarado; (2) no dice NADA sobre vigencia — Places "
     "descubre, no confirma. Y una tercera de alcance: los 5 son del oeste y el centro (comunas "
     "3, 10, 11, 15), así que el número NO se traslada al sur. Agregado por barrio solamente: "
     "ningún punto de Places sale de outputs/analisis_interno/.",
     "places_sonda_barrios_flacos.py"),
    # --- Belgrano, el precedente
    (V3 / "BELGRANO_SENSIBILIDAD_CONTINUIDAD_V3.csv", "belgrano_continuidad_precedente.csv",
     "El barrido de continuidad de Belgrano: el precedente del que sale toda la regla de partes. "
     "Umbrales 80-300 m sobre clusters candidatos (no sobre puntos sueltos: por eso los barridos "
     "de este paquete extienden la grilla hacia abajo).",
     "ejecutar_corrida_territorial_v3.py"),
    (V3 / "RECOLETA_VACIOS_CONTINUIDAD_V3.csv", "recoleta_vacios_continuidad.csv",
     "El otro precedente de continuidad: los vacios de Recoleta.",
     "ejecutar_corrida_territorial_v3.py"),
    # --- el test de regresión, que entra como material y no como código
    (TESTS / "test_normalizador_direcciones.py", "test_normalizador_direcciones.py",
     "El test de regresión del normalizador, incluido por sus CASOS NEGATIVOS. «Ciudad de la Paz» "
     "es una calle de Belgrano y cortar por «Ciudad» a secas la decapitaría; «Avellaneda» empieza "
     "con «Av» y no es una avenida abreviada. Los dos son de la familia del bug original («esq» "
     "matcheando adentro de «Esquiu»): son el mejor ejemplo de por qué un test de regresión sin "
     "casos negativos sólo demuestra que la corrección corrige.",
     "tests/test_normalizador_direcciones.py"),
]

# Las fórmulas van acá porque un CSV con una columna `cobertura` no dice cómo se calculó.
FORMULAS = [
    {"indicador": "A · razón pedida", "formula": "base_total ÷ parcelas comerciales del RUS",
     "columna": "base_sobre_comercial",
     "nota": "NO se puede leer sola: mezcla cobertura y composición. Por eso se reporta partida."},
    {"indicador": "A.1 · cobertura", "formula": "base_nucleo ÷ parcelas gastronómicas del RUS",
     "columna": "cobertura",
     "nota": "El factor que habla de la base. LÍMITE: el RUS está adentro de la base, así que no "
             "puede bajar de 1 y mide cuánto agregan las otras seis fuentes sobre ese piso."},
    {"indicador": "A.2 · composición",
     "formula": "parcelas gastronómicas del RUS ÷ parcelas comerciales del RUS × 1000",
     "columna": "rus_sobre_comercial",
     "nota": "NO es un defecto de la base: es el territorio. Palermo tiene más gastronomía por "
             "comercio que Villa Riachuelo y eso no es sesgo de medición."},
    {"indicador": "A.3 · aporte de las otras fuentes", "formula": "cobertura − 1",
     "columna": "aporte_otras_fuentes",
     "nota": "La cobertura sin el piso del propio RUS. Mediana 1,46."},
    {"indicador": "B · locales cada mil habitantes",
     "formula": "base_nucleo ÷ población en viviendas particulares × 1000",
     "columna": "locales_x_mil",
     "nota": "Población del Censo 2022, verificada contra dos archivos del INDEC. NO es un "
             "diagnóstico de cobertura: la gastronomía se ubica donde hay oficinas y turismo, no "
             "donde hay camas. La unidad de referencia es la COMUNA, porque el 20,5 % de la "
             "población vive en radios que tocan más de un barrio y el barrio exige repartir."},
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    DESTINO.mkdir(parents=True, exist_ok=True)

    filas, faltantes = [], []
    for origen, nombre, que_es, script in MATERIAL:
        if not origen.exists():
            faltantes.append((nombre, str(origen.relative_to(ROOT)), script))
            continue
        shutil.copy2(origen, DESTINO / nombre)
        filas.append({"archivo": nombre, "que_es": que_es, "script_de_origen": script,
                      "ruta_original": str(origen.relative_to(ROOT))})

    indice = pd.DataFrame(filas)
    indice.to_csv(DESTINO / "INDICE.csv", index=False, encoding="utf-8")
    pd.DataFrame(FORMULAS).to_csv(DESTINO / "formulas_parejidad.csv", index=False,
                                  encoding="utf-8")
    if faltantes:
        pd.DataFrame(faltantes, columns=["archivo", "ruta_esperada", "script"]).to_csv(
            DESTINO / "FALTANTES.csv", index=False, encoding="utf-8")

    print(f"material volcado en {DESTINO.relative_to(ROOT)}")
    print(f"  archivos copiados : {len(filas)}")
    print(f"  faltantes         : {len(faltantes)}")
    for nombre, ruta, script in faltantes:
        print(f"    {nombre} — falta {ruta} (lo produce {script})")
    print(f"  índice            : INDICE.csv")
    print(f"  fórmulas          : formulas_parejidad.csv ({len(FORMULAS)} indicadores)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
