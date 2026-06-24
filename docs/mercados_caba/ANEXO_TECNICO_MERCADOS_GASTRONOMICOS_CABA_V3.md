# Mercados gastronómicos de CABA — Anexo técnico (V3)

> Respaldo metodológico interno del informe final V3. No es el documento principal para enviar.
> Fecha: 2026-06-24.

## 1. Fuentes usadas

- **Oficiales (C1):** Buenos Aires Ciudad / GCBA (Descubrir BA, Desarrollo Económico, sección
  Mercados, BA Capital Gastronómica), Turismo BA, Argentina.gob.ar (economía social), Boletín
  Oficial CABA (régimen de concesiones).
- **Sitios oficiales del mercado (C2):** mercadosantelmo.com.ar, mercadodelprogreso.com,
  mercadosoho.com.ar, elgalpon.org.ar, buenosairesmarket.com, sabelatierra.org,
  gourmandfoodhall.com.
- **Prensa multifuente (C3):** La Nación, El Cronista, Infobae, Radio Hache, El Trece/Cucinare,
  Info Gastronómica, entre otros (apoyo, no fuente única).

## 2. Google Places

Validación de los activos y descubrimiento de posibles omitidos mediante Google Places API en
**modo seguro** (key solo desde entorno/.env, nunca impresa; crudos y staging en interno
gitignored; outputs sanitizados **sin** place_id, teléfono ni dirección individual). Aportó el
estado operativo (`businessStatus`) y señales de actividad (reseñas). En esta etapa **no** se
hicieron nuevas requests.

## 3. Fuentes internas (DGDGAS)

Inventario de 119 archivos internos leídos **solo en metadata** (sin contactos, teléfonos, emails,
CUIT ni links privados). Corroboraron Belgrano, Bonpland, San Nicolás y Progreso. Material crudo en
carpeta gitignored; no se versiona.

## 4. Perplexity / documental

Dos tandas: V2.1 (con `url_no_visible_en_export`) y V2.3 (19 fuentes con URLs visibles, 16
completas y 3 truncadas marcadas `url_truncada_requiere_verificacion`). Reforzaron fuentes y
contradicciones; **no** modifican el conteo por sí mismas.

## 5. Por qué se excluyeron Soho, Mercat Caballito y El Galpón

- **Mercado Soho:** Google `CLOSED_PERMANENTLY`; sin evidencia reciente suficiente (perfil por
  Turismo BA, pero dirección/horario solo por prensa, sin sitio oficial vigente recuperado).
- **Mercat Caballito:** Google `CLOSED_PERMANENTLY`; la fuente oficial es solo una mención de
  evento, sin ficha propia con dirección/horario.
- **El Galpón:** match de Google inconsistente (devolvió un teatro/`event_venue` homónimo) y
  situación no clara.

Criterio: una señal de cierre en una sola fuente no alcanza para afirmar cierre, pero sí para
**dejar de contarlos como activos** hasta validar. Son **casos en revisión**, reversibles.

## 6. Cómo se integró Gourmand Food Hall

Validado contra **5 criterios** (identidad propia de food hall, operación verificable, +10
propuestas, multifuente, no es patio de comidas común). Sostenido por **sitio oficial**, **prensa**
y **Google `OPERATIONAL`** con alta cantidad de reseñas. Se incorporó como `food_hall` privado
activo (MG-0017), pasando el conteo de 12 a **13**. Ver `validacion_gourmand_food_hall_v2_4.csv`.

## 7. Limitaciones

- Relevamiento documental; **no** valida actividad en terreno. Ningún caso alcanza confianza alta
  por verificación territorial.
- Sesgo de cobertura hacia mercados emblemáticos/turísticos.
- Horarios autodeclarados y a veces divergentes (San Telmo, Progreso).
- Coordenadas del mapa **aproximadas por barrio** (lectura territorial, no geolocalización exacta).

## 8. Pendientes de validación

- Estado operativo en terreno de los 3 casos en revisión.
- Horarios definitivos de San Telmo y de los itinerantes (por sede).
- Recuperación de las 3 URLs truncadas del documental.
- Revisión de posibles omitidos prioritarios (Feria del Productor FAUBA, Mercado Punto Verde,
  Mercado Fusión).

## 9. Trazabilidad de archivos

Activos: `mercados_gastronomicos_activos_v3.csv` · No activos: `mercados_gastronomicos_no_activos_v3.csv`
· Resumen: `resumen_relevamiento_mercados_v3.csv` · Indicadores:
`indicadores_mercados_gastronomicos_v3.csv` · Horarios: `horarios_mercados_gastronomicos_v3.csv` ·
Públicos: `publicos_objetivo_mercados_v3.csv` · Oportunidades:
`oportunidades_politica_publica_mercados_v3.csv`. Documentos de respaldo V2.2/V2.3/V2.4 y validador
en `src/mercados_caba/validate_mercados_setup.py`.
