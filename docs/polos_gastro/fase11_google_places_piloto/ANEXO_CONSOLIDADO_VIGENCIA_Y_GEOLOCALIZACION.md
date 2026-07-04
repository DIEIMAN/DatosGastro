# Anexo consolidado — Vigencia y geolocalización auxiliar

DGDGAS — Dirección General de Desarrollo Gastronómico. Documento interno. Insumo para el Borrador 4.
Fecha: 2026-07-02. Respaldo técnico: documentos por tanda (ver sección final).

## 1. Alcance de la capa Google Places

- Google Places se usa como **señal auxiliar**, no como fuente de verdad.
- **No reemplaza** el universo semilla ni sus registros.
- **No valida por sí solo** la existencia ni el recorte de un polo.
- Sirve para **geolocalización preliminar**, **vigencia operativa** (indicio de cierre) y
  **detección de casos dudosos** (sucursales, nombres, duplicados).
- Los puntos **no revisados** por una persona **no** deben pasar directamente al mapa público.

## 2. Estado general de las corridas ejecutadas

- Corridas ejecutadas: **3** (Tanda 1, Tanda 2 y **corrida ampliada** en 9 bloques internos de 10).
- Consultas reales acumuladas: **106** (10 + 10 + 86). **Cobertura completa** de la tabla preparada
  de Fase 11.
- Errores de API: **0**. Problemas de seguridad: **0**. Fuera de CABA: **0**.
- Outputs separados por corrida: **interno / revisión visual / publicable**.
- Publicables **sanitizados** (sin place_id, rating, user_ratings_total, dirección exacta ni
  nota interna; lat/lon vacíos mientras no haya aceptación humana).

Distribución de los **106** registros (ver `consolidado_tandas_google_places.csv`):

| Estado consolidado | Casos |
|---|---|
| match_fuerte | 32 |
| match_razonable_revisar_sede | 27 |
| zona_sucursal_a_revisar | 25 |
| duplicado_probable | 11 |
| vigencia_no_confirmada | 8 |
| query_a_corregir | 3 |

Matches razonables o fuertes (mencionables con prudencia): **59**.

Cobertura por polo (razonables = fuerte + razonable):

| Polo | Total | Razonables |
|---|---|---|
| Palermo | 19 | 12 |
| Recoleta | 8 | 6 |
| Microcentro y Centro | 7 | 6 |
| Villa Crespo | 9 | 6 |
| Belgrano | 11 | 6 |
| Puerto Madero | 9 | 5 |
| Costanera Norte | 6 | 5 |
| San Telmo | 8 | 4 |
| Avenida Corrientes | 6 | 3 |
| Chacarita | 7 | 2 |
| Caballito | 5 | 2 |
| Avenida Caseros / Barracas | 5 | 2 |
| Abasto | 6 | 0 (todos duplican Av. Corrientes) |

## 3. Locales con match fuerte o razonable

### 3.1 Match fuerte (operativos, nombre y zona coherentes)

| Local | Polo/subzona | Resultado Google | Estado | Decisión | Observación |
|---|---|---|---|---|---|
| Don Julio | Palermo | Don Julio (restaurant) | OPERATIONAL | validar y mapear | parrilla emblemática |
| La Cabrera | Palermo | La Cabrera Buenos Aires (barbecue) | OPERATIONAL | validar y mapear | normalizar nombre |
| Gran Dabbang | Palermo | Gran Dabbang (restaurant) | OPERATIONAL | validar y mapear | nombre poco ambiguo |

### 3.2 Match razonable con revisión de sede/zona

| Local | Polo/subzona | Resultado Google | Estado | Observación |
|---|---|---|---|---|
| Niño Gordo | Palermo | Niño Gordo (restaurant) | OPERATIONAL | sede Palermo (Thames); ver duplicado LG028 |
| Mishiguene | Palermo | Mishiguene (fine dining) | OPERATIONAL | confirmar zona |
| La Mar | Palermo | La Mar (peruano) | OPERATIONAL | confirmar sede Palermo vs Belgrano |
| Cosi Mi Piace | Palermo | Cosi Mi Piace (italiano) | OPERATIONAL | confirmar zona |
| Campo Bravo | Las Cañitas | CAMPOBRAVO Las Cañitas | OPERATIONAL | variante de nombre; probable mismo local |

### 3.3 Cadenas con sede a confirmar

| Local | Subzona | Resultado Google | Observación |
|---|---|---|---|
| Café Registrado | Palermo | Café Registrado (coffee_shop) | cadena; confirmar sede Palermo |
| Novecento | Las Cañitas | Novecento Cañitas | cadena; sede Báez 199 |
| Kansas | Las Cañitas | Kansas (american) | cadena; Av. Libertador, borde Las Cañitas |
| SushiClub | Las Cañitas | SushiClub Las Cañitas | cadena; sede Báez 268 confirmada por dirección |

## 4. Locales con vigencia no confirmada

Google los devolvió con el **nombre correcto**, pero **cerrados** (8 en total, todas las corridas):

| Local | Polo/subzona | Estado Google |
|---|---|---|
| Osaka | Palermo | CLOSED_PERMANENTLY |
| Aldo's | Palermo | CLOSED_PERMANENTLY |
| Morelia | Las Cañitas | CLOSED_PERMANENTLY |
| La Reina Kunti | Av. Corrientes | CLOSED_PERMANENTLY |
| La Reina Kunti | Abasto (duplicado) | CLOSED_PERMANENTLY |
| Las Pizarras Bistro | Palermo | CLOSED_TEMPORARILY |
| Francisca del Fuego | Palermo | CLOSED_TEMPORARILY |
| Alo's Café | Belgrano | CLOSED_TEMPORARILY |

**Criterio recomendado**: conservar en la semilla como referencia del documento base, pero
**excluir del mapa público** y de menciones como "activo" hasta validación territorial o
confirmación institucional.

## 5. Locales con query a corregir, duplicados o hitos colectivos

### 5.1 Query a corregir / match dudoso (3)

- **Pa' Pastar** → Google devolvió **"Pastasole Argentina"** (nombre distinto, confianza baja).
  Posible cierre/renombramiento. No aceptar el sustituto: corregir query o marcar sin match.
- **Oporto** → match gastronómico ("Oporto Almacén"), pero dirección en **Colegiales**, no en
  Palermo Soho/Hollywood. Revisar zona/sucursal antes de mapear en el polo.
- **Chila** (Puerto Madero) → Google lo devolvió como `tourist_attraction`. Es alta cocina;
  probablemente categoría errónea de Google. Revisar antes de descartar.

### 5.2 Duplicados probables (11) — hallazgo relevante para Borrador 4

La corrida ampliada confirmó **objetivamente** solapamientos que la semilla ya sospechaba: varios
locales devolvieron **el mismo `place_id`** en dos polos distintos. En particular, **Abasto y
Avenida Corrientes comparten los mismos 6 locales** (Guerrín, Las Cuartetas, El Palacio de la
Pizza, Pertutti, La Reina Kunti, Moulin Bleu). Esto respalda tratar Abasto como subzona/anexo de
Corrientes, no como polo independiente.

Otros duplicados por sucursal/nombre compartido: La Fuerza (Villa Crespo = Chacarita), Sottovoce
(Puerto Madero = Recoleta), Hierbabuena (San Telmo = Caseros), Napoles (San Telmo = Caseros), Anafe
(Chacarita = Belgrano "original"), y Niño Gordo zona límite (LG028 = LG003 Palermo).

**Criterio**: no borrar; marcar como `duplicado_probable` y decidir a mano cuál registro se mapea.

### 5.3 Hitos colectivos / mercados (revisar)

Google devolvió categoría de mercado/patio para casos que **no** son un local individual: Mercado
de San Telmo, Patio de los Lecheros, El Mercado (Faena) y similares. Tratar como **hito colectivo**,
no como restaurante puntual.

## 6. Criterios de decisión para Borrador 4

| Categoría | Qué significa |
|---|---|
| mapeable tras revisión | operativo, nombre/zona coherentes; se habilita a mano |
| no mapeable hasta validar vigencia | cerrado (temp./perm.) según Google |
| zona/sucursal a revisar | sede o barrio no confirmado (cadenas, Oporto) |
| query a corregir | Google devolvió otro nombre (Pa' Pastar) |
| duplicado probable | misma dirección que otro registro (LG028 vs LG003) |
| conservar solo como referencia semilla | no se valida ni se mapea; queda en el universo base |

## 7. Recomendación editorial para el informe (DGDGAS)

- El cuerpo del informe **no** debe listar locales cerrados como activos.
- El mapa **no** debe mostrar locales cerrados ni dudosos.
- Las dudas van a **anexo** o a la sección de **decisiones humanas**, no al cuerpo.
- La semilla se **conserva sin borrar** registros.
- Narrativa **prudente**: "capa auxiliar", "requiere validación", "referencia preliminar";
  nunca presentar la geolocalización de Google como padrón oficial.

## 8. Próximo paso recomendado

La cobertura de Google Places sobre la semilla de Fase 11 **ya está completa** (106/106). No hace
falta más consulta de Places para el Borrador 4.

1. **Revisión humana** de los casos abiertos: 8 cerrados, 11 duplicados, 3 a corregir, hitos
   colectivos y los 25 de confianza baja (`zona_sucursal_a_revisar`).
2. Con los **59 razonables**, se puede armar un **mapa de revisión interno** (no público).
3. Preparar el **Borrador 4** integrando esta capa auxiliar y las decisiones humanas pendientes;
   resolver el tratamiento **Abasto = subzona de Av. Corrientes** con el respaldo objetivo de los
   duplicados.
4. Reforzar territorialmente los polos débiles (Abasto 0, Chacarita/Caballito/Caseros 2) por otras
   vías si se los quiere mantener como polos.

## Respaldo técnico (documentos por tanda, se conservan)

- `QA_REPILOTO_TANDA1_REAL_GOOGLE_PLACES.md`, `DECISION_POST_REPILOTO_TANDA1.md`.
- `QA_TANDA2_REAL_GOOGLE_PLACES.md`, `DECISION_POST_TANDA2.md`.
- `QA_FASE11_TANDAS_GOOGLE_PLACES.md`, `DECISIONES_HUMANAS_POST_TANDA1.md`.
- Tabla consolidada: `outputs/.../consolidado_tandas_google_places.csv`.
