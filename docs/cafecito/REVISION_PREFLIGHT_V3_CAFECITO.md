# Revisión preflight V3 - Cafecito

## Resultado general

Aprobado con observaciones.

El preflight está bien armado y refleja de forma mayoritaria los datos reales disponibles en los CSV y documentos de apoyo. El punto que conviene reforzar antes de pedirle a Claude la V3 es el control metodológico y editorial: el documento ya identifica bien la red potencial de difusión, pero el prompt final debería ser más explícito para evitar que la V3 afirme más de lo que la fuente permite.

## 1. Discrepancias encontradas

No se detectaron discrepancias numéricas importantes con los archivos revisados.

Observación menor:
- El preflight usa la lógica de "marcas pendientes o no usadas" y "sedes no usadas" de forma correcta, pero conviene explicitar en el prompt a Claude que:
  - solo deben usarse en mapas las filas con `usar_en_mapa = si`;
  - `usar_en_mapa = no` y `usar_en_mapa = pendiente` no deben aparecer en el mapa público;
  - los casos pendientes deben mantenerse como pendientes, no como sedes confirmadas.

## 2. Números verificados de cafeterías

Validación realizada sobre [outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv](outputs/cafecito/cafeterias_sedes_caba_geocodificadas.csv).

### Totales
- Filas totales: 43
- `usar_en_mapa = si`: 39
- `usar_en_mapa = no`: 2
- `usar_en_mapa = pendiente`: 2

### Comunas con más sedes mapeables
- Comuna 14: 9
- Comuna 13: 7
- Comuna 1: 7
- Comuna 15: 4
- Comuna 6: 3
- Comuna 2: 3
- Comuna 4: 2
- Comuna 5: 2
- Comuna 12: 1
- Comuna 11: 1

### Barrios con más sedes mapeables
- Palermo: 9
- Belgrano: 5
- Caballito: 3
- Recoleta: 3
- San Nicolás: 3
- Puerto Madero: 2
- Barracas: 2
- Villa Crespo: 2
- Almagro: 2

### Sedes explícitamente no usadas
- Lobo Cafe / Pierina Dealessi 1130 / Puerto Madero / Comuna 1
- GOUT Gluten Free / Av. La Plata 24 / Almagro / Comuna 5

### Marcas o sedes pendientes
- Caoba Cafe BA
- Cura Te Alma

### Nota metodológica importante
- El archivo principal de sedes muestra 2 filas con `usar_en_mapa = pendiente`, pero los nombres de esos casos aparecen en [outputs/cafecito/cafeterias_marcas_pendientes.csv](outputs/cafecito/cafeterias_marcas_pendientes.csv). Ese archivo es útil para completar la lectura de pendientes, pero no debe interpretarse como evidencia de sede confirmada para el mapa público.

## 3. Revisión de [docs/cafecito/INSUMOS_V3_CAFECITO.md](docs/cafecito/INSUMOS_V3_CAFECITO.md)

### Lo que está bien
- Incluye los números correctos.
- Incluye los casos no usados.
- Incluye los casos pendientes.
- Incluye la advertencia metodológica de que la red de cafeterías es una red potencial de difusión, no una prueba de participación física.
- Incluye riesgos de la V2.
- Incluye contenidos que no deberían pasar al PDF público.

### Lo que falta reforzar antes de pedir la V3 a Claude
El documento es útil, pero conviene dejar más explícito en el prompt que Claude debe:
- no afirmar representatividad;
- no decir que todas las sedes mapeadas participaron físicamente;
- no mostrar público individual;
- no usar sedes con `usar_en_mapa != si`;
- no usar Lobo Cafe 1130 ni GOUT Av. La Plata 24 en mapas;
- dejar Caoba Cafe BA y Cura Te Alma como pendientes;
- aclarar que la red de sedes es una aproximación a una red potencial de difusión;
- no incluir rutas, archivos, QA técnico ni referencias internas en el PDF público.

## 4. Riesgos detectados para el PDF público

### Contenido técnico que aparece en documentación interna

| Archivo | Contenido técnico que aparece | Riesgo para el PDF público | Recomendación |
| --- | --- | --- | --- |
| [docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md](docs/cafecito/INFORME_CAFECITO_EXPLORATORIO.md) | Sección "Archivos V2" con rutas como `scripts/cafecito/generar_informe_datagastro_v2.py`, `outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf`, `Cafesito/final/INFORME_CAFECITO_DATAGASTRO_V2.pdf` y otros nombres de archivos. | Alto | Mantenerlo solo en documentación interna; no incorporarlo al PDF público. |
| [docs/cafecito/README_CAFECITO.md](docs/cafecito/README_CAFECITO.md) | Múltiples rutas, scripts, outputs y nombres de archivos generados. | Medio-alto | Mantenerlo como README técnico interno; no copiarlo al informe público. |
| [outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf](outputs/cafecito/INFORME_CAFECITO_DATAGASTRO_V2.pdf) | La extracción de texto disponible no mostró patrones técnicos como rutas, `scripts`, `outputs`, `QA`, `git`, `commit`, `push` ni `place_id`. | Bajo | No requiere ajuste por este punto en esta revisión. |

### Recomendación concreta
- Que el PDF público conserve solo el contenido institucional y analítico útil.
- Que todo lo técnico quede en documentación interna, README o anexos no públicos.

## 5. Recomendación sobre mapas vs rankings

### Conclusión
Para el PDF institucional, conviene priorizar:
1. mapa comunal del público;
2. mapa de sedes de cafeterías;
3. mapa combinado si la legibilidad lo permite;
4. lectura textual breve en vez de rankings redundantes.

### Razón
El ranking comunal del público es redundante con el mapa comunal y, en esta pieza, la red de sedes ya aporta una lectura territorial independiente. El ranking comunal/barrial de sedes puede quedar como apoyo interno o en una nota metodológica, pero no necesita ser un bloque central del PDF público.

## 6. Recomendaciones exactas para el prompt de Claude

El prompt debería insistir en:
- no afirmar representatividad;
- no decir que todas las sedes mapeadas participaron físicamente;
- no mostrar público individual;
- no usar sedes con `usar_en_mapa != si`;
- no usar Lobo Cafe 1130 ni GOUT Av. La Plata 24 en mapas;
- dejar Caoba Cafe BA y Cura Te Alma como pendientes;
- aclarar que la red de sedes es una aproximación a una red potencial de difusión;
- no meter archivos, rutas, QA técnico ni referencias internas en el PDF público.

## 7. Git y límites

Verificación realizada con `git status --short` y `git diff --cached --name-only`.

### Confirmación
- No hay cambios staged.
- No hubo commit en esta revisión.
- No hubo push en esta revisión.
- No se generó PDF nuevo.
- No se tocaron datos fuente.
- No se reescribió el informe.
- No se modificaron archivos existentes salvo la creación de este documento de revisión.
