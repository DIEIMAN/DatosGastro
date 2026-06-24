# Mercados gastronómicos CABA — Relevamiento de candidatos v0

> Primera base candidata de **mercados gastronómicos** de CABA con fuentes públicas verificables.
> Relevamiento candidato, **no censo ni padrón oficial**. Fecha de corte: **2026-06-23**.
> No se usó Google Places API ni API keys. No se expusieron datos personales. No se inventaron
> datos: lo no confirmado quedó `pendiente`.

## 1. Metodología de búsqueda

1. **Ancla oficial.** Se partió del listado oficial **"Mercados y Patios Gastronómicos"** de
   Turismo BA / GCBA, que define el universo institucional de espacios con eje gastronómico.
2. **Verificación por candidato.** Para cada nombre (los del pedido + los del listado oficial) se
   buscaron fuentes públicas y se registró URL, organismo/medio y fecha de consulta en
   `fuentes_mercados_urls_v0.csv`.
3. **Jerarquía de fuentes.** Prioridad: GCBA/Turismo BA (C1) → sitio oficial del mercado (C2) →
   prensa con autoría multifuente (C3) → auxiliares (C4). Sin fuente → `pendiente`, no se
   completó de memoria.
4. **Filtro de alcance gastronómico** (criterios de `00_vision_y_objetivo.md`) aplicado antes de
   clasificar: en alcance, dudoso, o fuera de alcance.
5. **Privacidad.** Solo datos institucionales y agregados; sin teléfonos, mails, referentes,
   CUIT, place_id ni links privados.

La búsqueda web pública se usó como **localizador**; la fuente final quedó registrada con URL,
nombre y fecha. No hubo scraping de plataformas privadas (Maps, Rappi, etc.) ni llamadas pagas.

## 2. Fuentes usadas

- **Oficiales (C1):** Turismo BA — "Mercados y patios gastronómicos"; GCBA Desarrollo Económico /
  Descubrir BA (fichas por mercado); GCBA noticias (BA Market, Sabe la Tierra).
- **Sitios oficiales del mercado (C2):** mercadosantelmo.com.ar, mercadosoho.com.ar,
  buenosairesmarket.com, sabelatierra.org.
- **Prensa multifuente (C3):** La Nación, El Cronista (Carruajes, Mercat Caballito).
- **Auxiliar (C4):** Wikipedia (datos a confirmar, p. ej. cantidad de puestos del Progreso).
- **Internas (contexto, sin PII):** señales DGDGAS de V2 (`outputs/v2/sanitized/`) sobre
  "ferias_mercados" y eventos; no aportan nombres nuevos de mercados, solo contexto de
  activaciones.

URLs completas en `outputs/mercados_caba/sanitized/fuentes_mercados_urls_v0.csv`.

## 3. Criterios de inclusión / exclusión (aplicados)

- **Incluir** si la gastronomía/los alimentos/los productores son el eje central (food hall,
  mercado de productores, mercado histórico con oferta alimentaria, patio gastronómico, feria
  gastronómica).
- **Excluir** (`fuera_de_alcance_no_gastronomico`) si el eje es antigüedades, ropa, diseño,
  shopping/outlet, supermercado o mayorista sin experiencia gastronómica.
- **Dudoso** (`dudoso_pendiente_revision`) si el peso gastronómico no está claro o si es una zona
  y no un mercado único.

## 4. Tabla de candidatos en alcance (16)

| id | nombre | tipo | gestión | barrio | confianza | estado |
|---|---|---|---|---|---|---|
| MG-0001 | Mercado de San Telmo | identidad histórica gastronómica | mixta | San Telmo | C1 | activo |
| MG-0002 | Mercado de Belgrano | identidad histórica gastronómica | mixta | Belgrano | C1 | activo |
| MG-0003 | Mercado del Progreso | barrial alimentario | privada | Caballito | C1 | activo |
| MG-0004 | Mercat Villa Crespo | food hall | privada | Villa Crespo | C1 | activo |
| MG-0005 | Mercado Soho | food hall | privada | Palermo | C1 | activo |
| MG-0006 | Patio de los Lecheros | espacio tipo mercado gastronómico | pública | Caballito | C1 | activo |
| MG-0007 | Mercado de los Carruajes | food hall | mixta | Retiro | C1 | **cerrado (abr-2025)** |
| MG-0008 | Mercado Bonpland | mercado de productores | mixta | Palermo | C1 | activo |
| MG-0009 | El Galpón | mercado de productores | privada | Chacarita | C1 | activo |
| MG-0010 | Smart Plaza Patio Parque Patricios | espacio tipo mercado gastronómico | pública | Parque Patricios | C1 | activo |
| MG-0011 | Patio Costanera Norte | espacio tipo mercado gastronómico | mixta | Costanera Norte | C1 | activo |
| MG-0012 | Patio Gastronómico Rodrigo Bueno | espacio tipo mercado gastronómico | pública | Puerto Madero | C1 | activo |
| MG-0013 | Mercado San Nicolás | identidad histórica gastronómica | mixta | San Nicolás | C1 | activo |
| MG-0014 | Mercat Caballito | food hall / orgánico | privada | Caballito | C3 | activo |
| MG-0015 | Buenos Aires Market | feria gastronómica (itinerante) | privada | itinerante | C2 | activo |
| MG-0016 | Sabe la Tierra | mercado de productores (itinerante) | privada | itinerante | C2 | activo |

Detalle completo (oferta, horarios, fuentes, observaciones) en
`mercados_gastronomicos_candidatos_v0.csv` y en las fichas de `fichas_v0/`.

## 5. Candidatos dudosos (`dudoso_pendiente_revision`)

- **Barrio Chino (Belgrano)** — distrito comercial con oferta gastronómica y comercios orientales;
  no es un mercado único. Revisar si se trata como unidad o como zona.
- **Los Arcos del Rosedal / "Patio de los Arcos" (Palermo)** — polo gastronómico bajo viaducto;
  hay que desambiguarlo de **Distrito Arcos** (outlet, fuera de alcance) y definir si es un
  mercado/patio o un conjunto de restaurantes independientes.
- **CAM y Mercado Comunitario Primera Junta (5)** — heredados del relevamiento inicial; son
  mercados de abasto alimentario marcados `revisar_foco_gastronomico` (falta confirmar oferta de
  comida/gastronómica).
- **Mercado M1 (Chacarita)** — nombre ambiguo; confirmar naturaleza y eje.

Todos en `mercados_pendientes_revision_v0.csv`.

## 6. Candidatos fuera de alcance (`fuera_de_alcance_no_gastronomico`)

- **Mercado de las Pulgas (Chacarita)** — eje antigüedades/usados.
- **Distrito Arcos (Palermo)** — premium outlet; gastronomía accesoria.

En `mercados_fuera_alcance_v0.csv`. No se fuerza inclusión: solo entrarían con evidencia de oferta
gastronómica central.

## 7. Qué NO hizo esta etapa

No se ejecutó Google Places ni OSM/Overpass; no se usaron API keys; no se descargaron crudos
versionables; no se completaron horarios/oferta sin fuente. Los vacíos quedan en
`12_brechas_y_pendientes_v0.md`.
