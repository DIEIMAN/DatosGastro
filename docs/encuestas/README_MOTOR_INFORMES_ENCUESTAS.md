# Motor reusable de informes de encuestas

Herramienta experimental y paralela para futuros informes DataGastro basados en
formularios, encuestas o planillas de respuestas.

No reemplaza informes vigentes. En particular, no modifica ni sobrescribe el
informe actual de Cafecito Belgrano Tanda 5.

## Carpetas

- `scripts/encuestas/`: motor reusable.
- `config/encuestas/`: configuraciones y fixtures de prueba.
- `docs/encuestas/`: documentacion operativa.
- `outputs/encuestas/`: salidas generadas por el motor.

## Caso de prueba incluido

El caso `cafecito_belgrano_template_test` usa un CSV sintetico, sin datos
personales reales, para validar estructura y estilo del template.

Regenerar:

```powershell
python scripts/encuestas/generar_informe_encuesta.py --config config/encuestas/cafecito_belgrano_template_test.json
```

Salida esperada:

```text
outputs/encuestas/cafecito_belgrano_template_test/
```

## Guardrails

- El motor solo escribe bajo `outputs/encuestas/`.
- No toca `scripts/cafecito/`, `docs/cafecito/`, `outputs/cafecito/` ni `Cafesito/`.
- No modifica fuentes originales; calcula hash antes y despues.
- Excluye columnas sensibles o no publicables segun config.
- No publica respuestas abiertas textuales.
- Genera QA de privacidad en el output.

## Como adaptar a otro evento

1. Copiar el JSON de prueba dentro de `config/encuestas/`.
2. Cambiar `project_slug`, titulos, fuente, fecha de corte y `output_dir`.
3. Revisar cada pregunta: columna, tipo, publicabilidad y objetivo.
4. Marcar como `public: false` cualquier dato personal, contacto, timestamp,
   barrio/localidad fina o texto libre riesgoso.
5. Ejecutar el script.
6. Revisar `QA_PRIVACIDAD_TEMPLATE_TEST.md`, tablas, graficos y PDF.

## Tipos de pregunta

- `single`: pregunta cerrada de seleccion unica.
- `multi`: pregunta cerrada de multiple respuesta.
- `open`: texto libre; solo se reporta conteo no vacio.
- `sensitive`: dato excluido de salidas publicas.

Para multi-respuesta, si una opcion contiene coma interna, declararla en
`canonical_options_with_commas` para no partirla por error.
