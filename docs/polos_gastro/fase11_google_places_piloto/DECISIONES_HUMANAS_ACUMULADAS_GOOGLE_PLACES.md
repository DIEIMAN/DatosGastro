# Decisiones humanas acumuladas — Google Places (PolosGastro)

DGDGAS — Dirección General de Gastronomía. Documento interno, en lenguaje simple. Reúne lo que hay
que decidir antes de armar el mapa. Fecha: 2026-07-02. No borra nada de la semilla.

## Locales cerrados (no mostrar como activos hasta validar)

- **Osaka** (Palermo) — cerrado permanente según Google.
- **Aldo's** (Palermo) — cerrado permanente según Google.
- **Morelia** (Las Cañitas) — cerrado permanente según Google.
- **Las Pizarras Bistro** (Palermo) — cerrado temporal según Google.
- **Francisca del Fuego** (Palermo) — cerrado temporal según Google.

**Decidir**: si se confirman como cerrados, quedan fuera del mapa y no se mencionan como activos;
se conservan en la semilla como referencia del documento base.

## Locales con zona o sucursal dudosa

- **Oporto** — Google lo ubica en **Colegiales**, no en Palermo Soho/Hollywood. ¿Es la referencia de
  Palermo u otra sede?
- **Cadenas** (confirmar que la sede devuelta es la esperada): **Café Registrado** (Palermo),
  **Novecento**, **Kansas**, **SushiClub** (Las Cañitas).
- **La Mar** — confirmar sede Palermo vs Belgrano.

**Decidir**: qué sede se toma para el mapa en cada caso.

## Duplicados probables

- **Niño Gordo "zona límite" (LG028)** devolvió la **misma dirección (Thames 1810)** que **Niño
  Gordo Palermo (LG003)**. Probablemente **no** hay una sede propia en Villa Crespo.

**Decidir**: tratar LG028 como duplicado de LG003 o confirmar sede independiente.

## Queries a corregir / match no confiable

- **Pa' Pastar** — Google devolvió **"Pastasole Argentina"** (otro nombre). No aceptar ese
  sustituto. Corregir la búsqueda o marcar como "sin match confiable".

**Decidir**: reintentar con otra query o dejar sin geolocalizar.

## Nombres a normalizar (menor)

- **La Cabrera** — Google devuelve "La Cabrera Buenos Aires"; usar "La Cabrera".
- **Campo Bravo** — Google devuelve "CAMPOBRAVO"; probablemente el mismo local.

## Actualización tras la corrida ampliada (86 locales restantes; total 106)

### Cerrados adicionales (sumar a los 5 previos → 8 en total)

- **La Reina Kunti** (Av. Corrientes / Abasto) — cerrado permanente.
- **Alo's Café** (Belgrano) — cerrado temporal.

### Duplicados confirmados por Google (mismo place_id en dos polos)

- **Abasto = Avenida Corrientes**: Guerrín, Las Cuartetas, El Palacio de la Pizza, Pertutti, La
  Reina Kunti, Moulin Bleu → los 6 locales de Abasto son los mismos de Corrientes.
  **Decidir**: tratar Abasto como subzona/anexo de Av. Corrientes, no como polo independiente.
- **La Fuerza** (Villa Crespo = Chacarita), **Sottovoce** (Puerto Madero = Recoleta),
  **Hierbabuena** y **Napoles** (San Telmo = Caseros), **Anafe** (Chacarita = Belgrano).
  **Decidir**: cuál sede se mapea en cada caso.

### Categoría dudosa

- **Chila** (Puerto Madero) → Google la marca como "atracción turística". Es alta cocina; revisar
  antes de descartar.

### Hitos colectivos (no son un local)

- Mercado de San Telmo, Patio de los Lecheros, El Mercado (Faena): tratar como hito colectivo.

## Qué hay que decidir antes del mapa

1. Confirmar cuáles de los **8 cerrados** quedan fuera.
2. Elegir la sede correcta de las cadenas, de Oporto/La Mar y de los **11 duplicados**.
3. Resolver **Abasto = Av. Corrientes** (subzona/anexo).
4. Definir qué hacer con Pa' Pastar y con Chila (categoría).
5. Revisar los **25 casos de confianza baja** (`zona_sucursal_a_revisar`).
6. Recién entonces marcar a mano los puntos aceptados para mapa.

> Regla: la semilla se conserva completa; Google Places es solo apoyo. Nada va al mapa público sin
> esta revisión humana.
