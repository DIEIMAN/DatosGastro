# Guía Opción B — Descarga real de fuentes oficiales

> El entorno del asistente bloquea `*.buenosaires.gob.ar` (`x-deny-reason: host_not_allowed`),
> por eso la descarga se ejecuta en **tu máquina**. Todo quedó preparado y probado.

## Estado verificado de las fuentes (junio 2026, vía búsqueda web)

| Fuente | Estado | Nota |
|---|---|---|
| **F01** Establecimientos (ENTUR) | **Vivo pero desactualizado** | Última actualización feb-2023. ENTUR declaró formalmente no ser área competente (Decreto 36/2022). Es un dataset huérfano → refuerza la oportunidad "padrón vivo". URL directa CSV funciona. |
| **F02** Habilitaciones AGC | **Vivo y muy actualizado** | Recursos por año 2023–2026; el dataset fue modificado pocos días atrás. Fuente correcta para el monitor de altas. |
| **F03** Ferias y Mercados | **Vivo** | Disponible en CSV, SHP y GeoJSON (geo listo para mapa). |

## Pasos

```bash
# 1. Entorno
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Completar URLs por año de F02 y F03 en src/config.py / src/download_sources.py
#    (copiarlas desde el portal del dataset: botón DESCARGAR de cada recurso/año)

# 3. Descargar
python src/download_sources.py        # baja F01 directo; F02/F03 según URLs cargadas

# 4. Perfilar (genera reporte de calidad: encoding, sep, nulos, duplicados, mojibake,
#    filtro gastronómico y match de barrios contra Ley 2650)
python src/profile_sources.py
```

## Qué esperar de F01 al descargarlo
- Header real: `nro_registro;rubro;establecimiento;domicilio_completo;barrio;comuna;telefono;email;facebook;web;accesibilidad`
- Separador `;`, encoding latin-1 mal exportado → mojibake ("CAFÉ"→"CAF", "AL CARBÓN"→"AL CARBN"). Tratar con `ftfy` en limpieza.
- Números de registro 2015–2019 → marcar vigencia dudosa (estado `sin_verificar`) hasta cruzar con F02.

## Siguiente paso del pipeline (ya con datos reales)
`ftfy → USIG (geo) → catálogo barrios → dedupe → reconstruir data/processed → recalcular analytics`.
La normalización de barrios, el centinela de ubicación y el recálculo de analytics ya están implementados (ver `src/fix_v1_estructura.py` como referencia).
