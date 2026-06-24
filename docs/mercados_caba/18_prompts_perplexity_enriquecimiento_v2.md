# Mercados gastronómicos CABA — Prompts de Perplexity / búsqueda documental (V2)

> Perplexity (o búsqueda asistida) se usa **solo para localizar fuentes**, no como fuente final.
> Toda afirmación debe quedar respaldada por una **URL verificable** (título, medio, fecha). Sin
> URL comprobable, **no entra**. Los resultados se vuelcan a
> `outputs/mercados_caba/sanitized/fuentes_documentales_mercados_v2.csv`. **No** se copian
> teléfonos, emails, referentes ni datos personales.

## Reglas de uso

1. El resultado es una **lista de fuentes**, no un dato definitivo.
2. Priorizar oficiales (GCBA, Turismo BA, BA Capital Gastronómica) y sitios propios del mercado.
3. Verificar cada URL antes de usarla; descartar blogs sin fuente original.
4. No incorporar candidatos nuevos automáticamente: marcarlos `posible_omitido_pendiente_revision`.

## Prompts (10)

### 1. Mercados gastronómicos activos en CABA
```text
Listá fuentes oficiales y verificables (GCBA, Turismo BA) sobre los mercados gastronómicos
actualmente activos en la Ciudad de Buenos Aires. Para cada uno citá título, medio y URL. No
incluyas mercados de pulgas/antigüedades ni shoppings.
```

### 2. Food halls en CABA
```text
Buscá fuentes sobre food halls / patios gastronómicos curados en CABA (ej. Mercat, Mercado Soho,
Mercat Caballito). Indicá dirección, oferta y horarios con su URL y fecha. Solo fuentes con autoría.
```

### 3. Mercados de productores en CABA
```text
Localizá fuentes oficiales sobre mercados de productores y economía social en CABA (ej. Bonpland,
El Galpón, ferias de productores). Días, horarios y gestión, con URL verificable.
```

### 4. Patios gastronómicos públicos de GCBA
```text
Buscá fuentes oficiales (buenosaires.gob.ar, Turismo BA, BA Capital Gastronómica) sobre patios
gastronómicos gestionados o impulsados por GCBA (Lecheros, Smart Plaza Parque Patricios, Costanera
Norte, Rodrigo Bueno). Dirección, días y horarios con URL.
```

### 5. Mercados históricos con oferta gastronómica
```text
Localizá fuentes sobre mercados históricos de CABA con oferta gastronómica (San Telmo, Belgrano,
Progreso, San Nicolás). Historia, gestión y oferta actual, citando URL oficial o prensa con fecha.
```

### 6. Estado / cierre del Mercado de los Carruajes
```text
Buscá fuentes que confirmen el estado actual del Mercado de los Carruajes (Retiro): ¿sigue
cerrado? ¿se reconvirtió? Citá medio, fecha y URL.
```

### 7. Gestión / concesión de mercados gastronómicos
```text
Localizá normativa o fuentes oficiales sobre el régimen de gestión/concesión de los mercados
gastronómicos municipales de CABA (mercados públicos, patios GCBA). URL del Boletín Oficial o GCBA.
```

### 8. Cantidad de puestos y oferta por mercado
```text
Buscá fuentes que indiquen cantidad de puestos/locales y tipo de oferta de cada mercado
gastronómico de CABA. Solo datos con fuente citada (sitio oficial o prensa con fecha).
```

### 9. Horarios oficiales
```text
Para cada mercado gastronómico activo de CABA, localizá la fuente oficial de horarios (sitio
propio o GCBA/Turismo BA). Señalá divergencias entre fuentes (ej. Mercado de San Telmo).
```

### 10. Posibles omitidos
```text
Buscá menciones recientes y verificables de mercados gastronómicos, food halls o ferias
gastronómicas en CABA que NO estén en esta lista: San Telmo, Belgrano, Progreso, Mercat Villa
Crespo, Soho, Lecheros, Bonpland, El Galpón, Smart Plaza Parque Patricios, Costanera Norte, Rodrigo
Bueno, San Nicolás, Mercat Caballito, Buenos Aires Market, Sabe la Tierra. Citá URL y fecha; marcá
cada hallazgo como posible omitido a revisar.
```

## Volcado de resultados

Cada fuente verificada se registra en `fuentes_documentales_mercados_v2.csv` con: id, mercado,
tipo de fuente, título, medio/organismo, URL, fecha de publicación (si existe), fecha de consulta,
afirmación sostenida, campo que respalda, nivel de confianza, observación. **Sin URL verificable,
no entra.**
