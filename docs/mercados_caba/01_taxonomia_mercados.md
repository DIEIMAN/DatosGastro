# Mercados gastronómicos CABA — Taxonomía

> Tipología de **mercados gastronómicos** y espacios tipo mercado con eje gastronómico. Fuente de
> verdad machine-readable: `outputs/mercados_caba/sanitized/taxonomia_mercados.csv`.

## 1. Principio

Todas las categorías exigen que la **gastronomía, los alimentos o las bebidas sean el eje
principal** del espacio. Un espacio puede ser **mixto** o combinar funciones: **no se excluye
automáticamente**; se clasifica en la categoría gastronómica dominante y, si el peso de lo
gastronómico es ambiguo, se marca `dudoso_pendiente_revision` con justificación. Si la gastronomía
es accesoria o inexistente, se marca `fuera_de_alcance_no_gastronomico`.

## 2. Categorías

| tipo_mercado_gastronomico | qué es | señal distintiva | gestión típica |
|---|---|---|---|
| `mercado_gastronomico_publico` | gestión estatal/municipal con eje gastronómico/alimentario | titularidad GCBA + oferta gastronómica/alimentaria central | pública |
| `mercado_gastronomico_privado` | gestión privada con varios puestos de comida | operador privado con múltiples puestos gastronómicos | privada |
| `mercado_gastronomico_mixto` | gestión compartida con eje gastronómico | inmueble público con explotación gastronómica privada | mixta |
| `food_hall` | patio gastronómico curado | gastronomía curada como atractivo principal | privada |
| `mercado_de_productores` | venta directa de productores de alimentos | productores de alimentos/bebidas con venta directa | pública/mixta |
| `feria_gastronomica` | feria con eje gastronómico/alimentario | puestos de comida/alimentos como componente central | pública/mixta |
| `mercado_barrial_alimentario` | mercado de barrio con oferta alimentaria significativa | abasto barrial con peso alimentario/gastronómico | pública/mixta |
| `mercado_turistico_gastronomico` | mercado con perfil turístico ligado a su gastronomía | relevancia turística asociada a la oferta gastronómica | pública/privada |
| `mercado_con_identidad_historica_gastronomica` | mercado tradicional con oferta alimentaria vigente | trayectoria documentada + oferta gastronómica/alimentaria | pública/mixta |
| `espacio_tipo_mercado_gastronomico` | formato mercado con varios operadores gastronómicos | varios operadores, estética de mercado, eje gastronómico | privada |
| `dudoso_pendiente_revision` | foco gastronómico no confirmado | señales insuficientes/contradictorias sobre el eje | pendiente |
| `fuera_de_alcance_no_gastronomico` | espacio sin eje gastronómico/alimentario | categoría principal no alimentaria (pulgas, ropa, shopping…) | cualquiera |

## 3. Eje transversal: gestión

`publica` / `privada` / `mixta` / `pendiente`. Es un atributo aparte de la tipología: un
`mercado_de_productores` puede ser público (feria GCBA) o mixto, y un `food_hall` suele ser
privado.

## 4. Riesgos de clasificación (qué NO confundir)

- **Food hall ≠ patio de comidas de shopping** ni restaurante individual.
- **Mercado de productores ≠ feria de manualidades/antigüedades/pulgas** (aunque compartan el
  CSV F03): solo entra si el foco es alimentario.
- **Mercado barrial alimentario ≠** mercado de abasto puro **sin** componente gastronómico/de
  comida → si es solo abastecimiento mayorista, revisar alcance.
- **Mercado gastronómico público ≠ supermercado** ni mercado mayorista sin experiencia
  gastronómica.
- **Espacio "tipo mercado" ≠** un solo restaurante temático.

Ante duda sobre el peso gastronómico → `dudoso_pendiente_revision`. Si la gastronomía es claramente
accesoria → `fuera_de_alcance_no_gastronomico`. Nunca exclusión silenciosa.

## 5. Criterios de validación

Cada tipo tiene su criterio (columna `criterio_de_validacion` del CSV): registro oficial GCBA +
evidencia de oferta gastronómica/alimentaria, documentación de concesión, catálogo de ferias con
foco alimentario, sitio oficial del mercado con múltiples puestos gastronómicos, o relevamiento
territorial. La tipología tentativa se confirma recién con ≥1 fuente acorde **que acredite el eje
gastronómico**.
