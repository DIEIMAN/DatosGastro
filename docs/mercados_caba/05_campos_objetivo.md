# Mercados gastronómicos CABA — Campos objetivo

> Campos a relevar por **mercado gastronómico** candidato. Machine-readable:
> `outputs/mercados_caba/sanitized/campos_objetivo_mercados.csv`. Campo sin dato confiable →
> `pendiente`. **No inventar.**

## 1. Identificación y tipología
- `nombre` (oficial cuando exista) · `tipo_mercado_gastronomico` (taxonomía) ·
  `gestion_publica_privada_mixta`.

## 2. Territorio
- `barrio` (normalizado contra catálogo oficial CABA) · `comuna` (derivable del barrio) ·
  `direccion_o_zona` (dirección pública oficial o zona aproximada; sin precisión innecesaria).

## 3. Funcionamiento
- `horarios` · `dias_de_apertura` (distinguir permanente de temporal).

## 4. Oferta
- `oferta_gastronomica` (comida y bebida preparada — eje del informe) ·
  `oferta_alimentaria` (alimentos, productos frescos, bebidas, productores) ·
  `oferta_no_gastronomica_secundaria` (solo si es accesoria; si es central, revisar alcance) ·
  `cantidad_de_puestos_si_existe` (solo con dato confiable) ·
  `tipo_de_puestos` (gastronómicos / alimentarios / mixtos).

## 5. Público y perfil
- `publico_objetivo` (barrial / turístico / mixto) · `perfil_turistico` (alto/medio/bajo) ·
  `perfil_barrial` (alto/medio/bajo).

## 6. Composición, actividad y política pública
- `presencia_de_productores` (si/no/pendiente) · `presencia_de_locales_gastronomicos` ·
  `eventos_o_activaciones` (agregado interno, sin PII) ·
  `relacion_con_politicas_publicas` (circuitos/programas gastronómicos, p. ej. BA Capital
  Gastronómica) · `estado_aparente` (activo/cerrado/dudoso/pendiente).

## 7. Trazabilidad
- `fuentes` (códigos de fuente) · `nivel_de_confianza`
  (alto/medio/bajo/oficial_incompleto) ·
  `estado_revision` (candidato_local / revisar_foco_gastronomico / fuera_de_alcance / confirmado) ·
  `observaciones` (sin datos personales).

## 8. Datos prohibidos (nunca se relevan ni publican)
```text
telefono, celular, email, mail, referente, nombre de persona, CUIT, DNI,
links privados de Drive, place_id en entregables
```

## 9. Relación con el CSV de candidatos
`mercados_candidatos_iniciales.csv` usa una versión compacta de estos campos. La ficha completa
se arma en el relevamiento; los faltantes quedan `pendiente` hasta tener fuente. El campo
`estado_revision` marca explícitamente los candidatos cuyo foco gastronómico aún debe verificarse
y los que quedaron fuera de alcance.
