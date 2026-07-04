# DataGastro V2 — Matriz de fuentes oficiales y anclas institucionales

> Etapa 2. Documento de diseño construido **solo con archivos locales existentes y
> documentación ya creada**. **No** se descargó nada nuevo, **no** se ejecutaron requests,
> **no** se integraron datos, **no** se creó padrón. Pipeline V1 y casas de pastas intactos.

## 1. Para qué sirve esta matriz

Antes de barrer "todos los gastronómicos" de CABA, hay que saber **qué nos puede anclar en lo
oficial** y **dónde lo oficial no alcanza**. Esta matriz cataloga las fuentes oficiales o
institucionales disponibles o candidatas, qué rubros cubre cada una y qué brechas quedan para
fuentes externas (Google/OSM) y revisión manual.

Configs asociados (versionables, sin datos sensibles):
- `config/v2/fuentes_oficiales_candidatas_v2.csv`
- `config/v2/cobertura_fuente_rubro_v2.csv`
- `config/v2/rubros_universo_gastronomico_v2.csv`

## 2. Fuentes oficiales / anclas disponibles (ya en el repo, V1)

| Código | Fuente | Naturaleza | Qué aporta | Volumen V1 (referencia) |
|---|---|---|---|---|
| F01 | Oferta y Establecimientos Gastronómicos (BA Data) | dataset abierto oficial | oferta registrada con **categoría** y **tipo de cocina**, nombre, dirección, barrio, comuna, coordenadas | ~2.823 registros |
| F02 | Habilitaciones Aprobadas AGC | registro administrativo oficial | habilitaciones por **descripción de rubro**, domicilio, comuna, superficie (2015–2025) | ~500k filas (44.169 gastronómicas inferidas) |
| F03 | Ferias y Mercados (BA Data) | dataset abierto + padrón | espacios reales de ferias/mercados + padrón de puestos | 259 espacios reales (30 ferias, 6 mercados, padrón ~4.352) |
| F04 | Eventos gastronómicos | relevamiento manual trazable | eventos/ediciones con fuente por fila | ~29 |
| F05 | Programas y políticas gastronómicas | catálogo manual trazable | contexto institucional, normativa, instrumentos | ~9 |

> Datos de volumen tomados de la documentación V1 (`docs/contratos_fuentes.md`,
> `docs/fuentes_y_trazabilidad.md`). **No se reabrieron ni regeneraron** esos archivos.

## 3. Fuentes oficiales / anclas candidatas (requieren descarga futura, NO en esta etapa)

| Código | Fuente | Estado | Rol esperado |
|---|---|---|---|
| F06 | Ente de Turismo / oferta gastronómica | candidata (descarga/convenio futuro) | curaduría institucional con **sesgo turístico** |
| F07 | BA Data — Bares y Cafés Notables | candidata (descarga futura) | **ancla oficial fuerte** de `bar_notable` y emblemáticos |
| F08 | BA Data — comercios/locales adicionales | candidata (identificar recurso) | cobertura por rubro donde exista |
| F09 | Distritos económicos / circuitos gastronómicos GCBA | candidata (documental) | **contexto territorial**, no padrón |
| F10 | Espacios culturales con gastronomía (Cultura) | candidata (si aplica) | bares/cafés/eventos asociados a cultura |
| I03 | Relevamientos internos (catálogo eventos candidato, eventos propios) | disponible local (gitignored, **sensible**) | validación/contexto, **no publicable** |

URLs: las directas reales de F01–F05 ya están registradas en `src/config.py` (V1, no se toca).
Para F06–F10 **no se inventan URLs**: quedan `pendiente` hasta relevarlas con su ficha de
fuente. I03 existe localmente en `outputs/analisis_interno/` y `outputs/inventario_drive/`
(carpetas internas, leídas solo como metadata, no modificadas).

## 4. Qué cubre cada fuente (por función del ecosistema)

- **Consumo en local** → F01 (categoría + cocina) y F02 (rubro administrativo) son el núcleo.
  F06 (turismo) y F07 (notables) agregan curaduría/memoria.
- **Producción (obradores/fábricas)** → solo F02 cuando el rubro de elaboración está declarado;
  cobertura **baja**. Es la mayor brecha oficial.
- **Venta especializada** → F02 parcial (panaderías sí; chocolaterías/queserías/charcuterías
  poco). Núcleo real será externo.
- **Ferias y mercados** → F03 es el ancla fuerte (separando espacios de puestos).
- **Eventos** → F04 (manual), enmarcado por F05 e I03; nunca universo completo.

## 5. Por qué AGC (F02) no alcanza sola

1. **Habilitación ≠ local activo.** F02 mide permisos aprobados, no actividad. Un registro
   puede corresponder a un local cerrado o a una habilitación nunca operada.
2. **Descripción de rubro angosta.** El rubro administrativo no distingue "cafetería de
   especialidad" de "cafetería", ni "tostador" o "quesería" como rubros propios.
3. **No geocodificada como puntos** en V1 (regla vigente): dificulta densidad fina sin trabajo
   adicional.
4. **Sesgo de registro:** rubros de nicho y producción quedan subrepresentados o mezclados.

Por eso F02 es **ancla de legitimidad**, no universo: necesita F01 (oferta), señales operativas
(Google/OSM) y revisión manual para acercarse al universo real.

## 6. Brechas oficiales (resumen)

| Brecha | Fuentes oficiales | Dónde se compensa |
|---|---|---|
| Cafeterías de especialidad | baja | Google + documental + revisión |
| Producción / obradores / fábricas | baja (solo F02 parcial) | F02 rubro elaboración + documental + revisión fuerte |
| Venta de nicho (queserías, charcuterías, chocolaterías, almacenes) | baja | Google + documental |
| Bodegones | baja en datasets, fuerte en F07/documental | F07 notables + prensa |
| Cervecerías | baja (rubro reciente) | Google + OSM |
| Empanadas como rubro propio | baja | Google + revisión |

## 7. Reglas de uso (heredadas de V1, vigentes en V2)

- **No mezclar** F01 (oferta) + F02 (habilitaciones) como un total de "establecimientos".
- **No interpretar** puestos F03 como ferias/mercados.
- **No mezclar** universos oficiales (F0x) con operativos (E0x) en un total único sin nota.
- Cada fila conserva su fuente; cada agregado declara qué universo cuenta.
- I03 (interno) es **sensible**: solo validación/contexto, nunca entregable público.

## 8. Conexión con la taxonomía V2

La matriz se conecta con `dim_rubro_gastronomico` (taxonomía V2) vía
`config/v2/cobertura_fuente_rubro_v2.csv`, que cruza cada `codigo_fuente` con cada
`subcategoria_v2`, su `cobertura` (alta/media/baja/nula/desconocida) y su `rol`
(`nucleo_oficial` / `ancla_institucional` / `complemento` / `validacion` / `solo_contexto`).
Así, al barrer el universo, cada rubro sabe de antemano qué fuente lo ancla y cuánto depende de
fuentes externas (ver `13_mapa_cobertura_por_rubro_v2.md`).
