# Cafecito - análisis exploratorio

Este paquete documenta el análisis exploratorio del formulario Cafecito BA en tu barrio.

## Datos fuente

- `Cafesito/Formulario Cafecito (Respuestas).xlsx`
- `Cafesito/Formulario cafecito.pdf`
- `Cafesito/InfoCafecito`
- `Cafesito/Graficos  del form.docx`

El XLSX original se usa solo en modo lectura y no debe modificarse.

## Script

- `scripts/cafecito/analizar_cafecito.py`

Para regenerar los outputs:

```powershell
python scripts/cafecito/analizar_cafecito.py
```

## Outputs

- Tablas y resúmenes: `outputs/cafecito/`
- Gráficos: `outputs/cafecito/graficos/`
- Informe Markdown: `docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md`
- Documento Word con gráficos: `outputs/cafecito/INFORME_CAFECITO_GRAFICOS.docx`

## Privacidad

No publicar correos, marcas temporales, barrios/localidades libres, teléfonos ni identificadores personales. Los outputs públicos trabajan con agregados y omiten datos personales directos.

La muestra es exploratoria y no representativa del público total del evento.

## Versión DataGastro

Para regenerar la versión visual/narrativa DataGastro:

```powershell
python scripts/cafecito/generar_informe_datagastro.py
```

Outputs principales:

- Gráficos DataGastro: `outputs/cafecito/graficos_datagastro/`
- PDF institucional: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO.pdf`
- Copia final: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO.pdf`
- Markdown textual completo: `docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md`
- DOCX resumido con gráficos: `outputs/cafecito/INFORME_CAFECITO_GRAFICOS.docx`

## Mejora analítica territorial e interpretativa

Para regenerar la capa analítica previa a una nueva maquetación PDF:

```powershell
python scripts/cafecito/mejorar_analitica_cafecito.py
```

Outputs nuevos:

- Diagnóstico de mejoras: `docs/cafecito/DIAGNOSTICO_MEJORAS_INFORME_CAFECITO.md`
- Conclusiones por categoría: `docs/cafecito/conclusiones_por_categoria_cafecito.md`
- Resumen territorial agregado: `outputs/cafecito/resumen_territorial_agregado.csv`
- Ranking comunal: `outputs/cafecito/ranking_comunal_cafecito.csv`
- Cruces interpretativos: `outputs/cafecito/cruces_interpretativos_cafecito.md`
- Gráfico ranking comunal: `outputs/cafecito/graficos_datagastro/ranking_comunal_cafecito.png`
- Mapa comunal: `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png` (generado)

## Versión DataGastro V2

Para regenerar la versión final visual V2:

```powershell
python scripts/cafecito/generar_informe_datagastro_v2.py
```

Salidas V2:

- PDF institucional V2: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf`
- Copia final V2: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V2.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v2.py`

La V2 usa la mejora analítica territorial e interpretativa:

- `docs/cafecito/conclusiones_por_categoria_cafecito.md`
- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/resumen_territorial_agregado.csv`
- `outputs/cafecito/cruces_interpretativos_cafecito.md`
- `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png`
- `outputs/cafecito/graficos_datagastro/ranking_comunal_cafecito.png`

La versión anterior se conserva y no se sobrescribe.

## Versión DataGastro V3 (final)

Para regenerar la versión final institucional V3:

```powershell
python scripts/cafecito/generar_informe_datagastro_v3.py
```

Salidas V3:

- PDF institucional V3: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V3.pdf`
- Copia final V3: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V3.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v3.py`

Insumos territoriales y de red de cafeterías que usa la V3:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`
- `outputs/cafecito/graficos_datagastro/mapa_comunal_cafecito.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_v3.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_cafecito.png`

Notas:

- La V3 mapea sedes solo cuando `usar_en_mapa = si`. Lobo Cafe (Pierina Dealessi 1130) y GOUT Gluten Free (Av. La Plata 24) quedan fuera del mapa; Caoba Cafe BA y Cura Te Alma quedan pendientes.
- El PDF público no incluye rutas, nombres de archivos, scripts, hashes, identificadores de servicios externos ni referencias a versiones internas.
- Las versiones anteriores se conservan y no se sobrescriben.

QA técnico de la V3:

```powershell
# Verificar que el PDF no contenga contenido técnico interno
python - <<'PY'
import re, zlib
data = open(r"outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V3.pdf","rb").read()
texto = b""
for m in re.finditer(rb"stream
?
(.*?)
?
endstream", data, re.S):
    try: texto += zlib.decompress(m.group(1))
    except Exception: pass
prohibidos = [b".py", b".csv", b"outputs/", b"scripts/", b"docs/", b"place_id", b"SHA256", b"git", b"pdfinfo"]
print([p for p in prohibidos if p in texto] or "sin patrones tecnicos")
PY
```

## Versión DataGastro V4 (final)

Para regenerar la versión final institucional V4:

```powershell
python scripts/cafecito/generar_informe_datagastro_v4.py
```

Salidas V4:

- PDF institucional V4: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V4.pdf`
- Copia final V4: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V4.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v4.py`

Insumos territoriales y de red de cafeterías:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la V4 (no sobrescriben los de la V3):

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_v4.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_v4.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_v4.png`

Cambios respecto de la V3:

- Mapas más grandes con mejor contraste, escala de color y leyendas claras.
- Mapa de sedes diferencia las 4 marcas con más sedes; resto en gris.
- Terminología prudente: "sedes mapeables", "red potencial de difusión", "cafeterías vinculadas".
- TACC estandarizado en mayúsculas.
- Género: categoría minoritaria visible (No binario).
- Cruce de contacto: incluye "No está seguro/a" y fila Total.
- Títulos y subtítulos de gráficos separados con padding.

Notas:

- Mapea sedes solo cuando `usar_en_mapa = si`. Lobo Cafe (Pierina Dealessi 1130) y GOUT Gluten Free (Av. La Plata 24) quedan fuera; Caoba Cafe BA y Cura Te Alma pendientes.
- El PDF público no incluye rutas, archivos, scripts, hashes ni referencias a versiones internas.
- Las versiones anteriores se conservan y no se sobrescriben.

QA técnico de la V4:

```powershell
python -c "import re,zlib;d=open(r'outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V4.pdf','rb').read();t=b'';[t:=t+zlib.decompress(m.group(1)) for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream',d,re.S) if 1];p=[x for x in [b'.py',b'.csv',b'outputs/',b'scripts/',b'docs/',b'place_id',b'SHA256',b'git',b'pdfinfo',b'QA',b'V1',b'V2',b'V3',b'V4'] if x in t];print(p or 'sin patrones tecnicos')"
```

## Versión DataGastro V5 (final)

Para regenerar la versión final institucional V5:

```powershell
python scripts/cafecito/generar_informe_datagastro_v5.py
```

Salidas V5:

- PDF institucional V5: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V5.pdf`
- Copia final V5: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V5.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v5.py`

Insumos territoriales y de red de cafeterías:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la V5 (no sobrescriben los de V3 ni V4):

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_v5.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_v5.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_v5.png`

Cambios respecto de la V4 (solo layout):

- Mapas PNG sin títulos internos: los títulos se muestran solo en la página del PDF.
- Nota de género movida a la caja metodológica (evita texto cortado).
- Título "Intereses futuros" acortado para evitar truncamiento.
- Numeración de página: "Pág. X" en lugar de "0X".

Notas:

- Mapea sedes solo cuando `usar_en_mapa = si`.
- El PDF público no incluye rutas, archivos, scripts, hashes ni referencias a versiones internas.
- Las versiones anteriores se conservan y no se sobrescriben.

## Versión DataGastro V6 (final)

Para regenerar la versión final institucional V6:

```powershell
python scripts/cafecito/generar_informe_datagastro_v6.py
```

Salidas V6:

- PDF institucional V6: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V6.pdf`
- Copia final V6: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V6.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v6.py`

Insumos territoriales y de red de cafeterías:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la V6 (no sobrescriben los de V3, V4 ni V5):

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_v6.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_v6.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_v6.png`

Cambios respecto de la V5 (micro-correcciones):

- Terminología más prudente para la red de cafeterías: "Sedes públicas conocidas en CABA de marcas/cafeterías vinculadas al evento."
- Ajuste del color de la categoría minoritaria de género en el gráfico (gris) para ser menos llamativa.
- Mantiene layout V5 en páginas 5, 6 y 7, para no alterar la estructura.

## Versión DataGastro V6_1 (final)

Para regenerar la versión final institucional V6_1:

```powershell
python scripts/cafecito/generar_informe_datagastro_v6_1.py
```

Salidas V6_1:

- PDF institucional V6_1: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V6_1.pdf`
- Copia final V6_1: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V6_1.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_v6_1.py`

Insumos territoriales y de red de cafeterías:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la V6_1 (no sobrescriben los de V3, V4 ni V5 ni V6):

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_v6_1.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_v6_1.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_v6_1.png`

Cambios respecto de la V6 (micro-correcciones):

- Cambio de kicker de página y portada de "DATAGASTRO" a "DataGastro" por microcorrección de marca.
- Terminología más prudente para la red de cafeterías: "Sedes públicas conocidas en CABA de marcas/cafeterías vinculadas al evento."
- Ajuste del color de la categoría minoritaria de género en el gráfico (gris) para ser menos llamativa.
- Mantiene layout V5 en páginas 5, 6 y 7, para no alterar la estructura.

## Version DataGastro FINAL

Para regenerar la version final institucional:

```powershell
python scripts/cafecito/generar_informe_datagastro_final.py
```

Salidas FINAL:

- PDF institucional FINAL: `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf`
- Copia final FINAL: `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_FINAL.pdf`
- Script generador: `scripts/cafecito/generar_informe_datagastro_final.py`

Insumos territoriales y de red de cafeterias:

- `outputs/cafecito/ranking_comunal_cafecito.csv`
- `outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_comuna.csv`
- `outputs/cafecito/resumen_sedes_cafeterias_por_barrio.csv`

Mapas generados por la version FINAL:

- `outputs/cafecito/graficos_datagastro/mapa_comunal_publico_final.png`
- `outputs/cafecito/graficos_datagastro/mapa_sedes_cafeterias_final.png`
- `outputs/cafecito/graficos_datagastro/mapa_cafeterias_y_publico_final.png`

Cambios respecto de V6_1:

- Mantiene marca DataGastro, numeracion `Pág. X` y terminologia prudente.
- Remaqueta paginas 5, 6 y 7 para que los mapas ocupen el ancho superior y las cajas de lectura queden abajo.
- Conserva 12 paginas y no modifica datos fuente ni narrativa general.
