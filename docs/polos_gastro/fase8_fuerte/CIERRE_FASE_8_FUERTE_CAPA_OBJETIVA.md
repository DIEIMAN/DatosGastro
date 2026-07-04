# Cierre Fase 8 fuerte - Capa objetiva de contexto

Fecha de consulta: 2026-07-01.

## Que se hizo

Se construyo una capa objetiva de contexto territorial para PolosGastro a partir de fuentes locales
abiertas/oficiales y salidas procesadas existentes. La fase produce insumos tecnicos para revision
humana futura o Borrador 3.

## Fuentes usadas

- F01 oferta y establecimientos gastronomicos: 2823 registros.
- F02 habilitaciones gastronomicas procesadas: 44169 registros.
- Dimension local de ubicacion para apoyo comunal.
- Tabla de polos Borrador 2, solo lectura.
- Universo consolidado Fase 5, solo lectura.

No hubo descargas nuevas.

## Tablas creadas

- `outputs/polos_gastro/fase8_fuerte/tablas/oferta_gastronomica_por_barrio_fase8_fuerte.csv`
  (47 barrios).
- `outputs/polos_gastro/fase8_fuerte/tablas/oferta_gastronomica_por_comuna_fase8_fuerte.csv`
  (15 comunas).
- `outputs/polos_gastro/fase8_fuerte/tablas/habilitaciones_gastronomicas_por_comuna_fase8_fuerte.csv`
  (16 comunas o categorias de comuna).
- `outputs/polos_gastro/fase8_fuerte/tablas/indice_senal_objetiva_por_barrio_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/indice_senal_objetiva_por_comuna_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/polos_vs_capa_objetiva_fase8_fuerte.csv`.
- `outputs/polos_gastro/fase8_fuerte/tablas/insumo_mapa_contexto_objetivo_fase8_fuerte.csv`.

## Principales hallazgos

- F01 permite una lectura barrial de oferta registrada.
- F02 permite una lectura comunal de habilitaciones gastronomicas historicas.
- La lectura barrial de F02 no es suficiente para esta fase.
- Los barrios con senal objetiva alta tienden a coincidir con areas ya relevantes en la lectura
  documental, pero eso no valida subpolos ni corredores.
- Casos como Corrientes, Abasto, Caseros, DoHo, Costanera Norte y Federico Lacroze requieren
  delimitacion territorial antes de cruzarse con datos cuantitativos finos.

## Limitaciones

- La capa no mide locales activos.
- La capa no mide densidad real.
- La capa no valida vigencia operativa.
- La capa no cierra delimitaciones oficiales.
- La capa no modifica clasificaciones.
- El indice es interno y relativo a fuentes disponibles.

## Que no se hizo

- No se modifico Borrador 2.
- No se modificaron tablas de Fase 7.
- No se modifico la validacion de Fase 8 liviana.
- No se tocaron datos fuente.
- No se uso Google Places.
- No se generaron PDF, DOCX, mapas, graficos ni dashboards.
- No se hizo commit, push ni staging.

## Como usar la capa

Usarla como contexto para Borrador 3, idealmente en anexo tecnico y con advertencias visibles.
No usarla como veredicto, ranking ni delimitacion oficial.

## Proximos pasos recomendados

- Revision humana del cruce `polos_vs_capa_objetiva_fase8_fuerte.csv`.
- Definir delimitaciones preliminares solo textuales para corredores prioritarios.
- Decidir que tablas pueden entrar al Borrador 3 y cuales deben quedar en anexo.
- Si se hacen mapas futuros, producir solo mapas de contexto, no poligonos oficiales.
