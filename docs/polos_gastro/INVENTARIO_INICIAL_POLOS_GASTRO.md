# Inventario inicial PolosGastro

## Advertencia metodológica

Este inventario corresponde a una Fase 1. El PDF se trata como insumo semilla no validado, no como fuente oficial ni como verdad cerrada. La base resultante es candidata y requiere validación con fuentes complementarias antes de usarla como insumo de gestión, mapa o informe institucional.

## Archivo fuente detectado

- Archivo usado: `PolosGastro/Polos gastronómicos.pdf`
- Cantidad de páginas: 8
- Fecha de procesamiento local: 2026-06-29
- Extracción: lectura de texto con `pdftotext` y normalización controlada en `scripts/polos_gastro/inventariar_polos_gastro.py`.
- Copia de trabajo: no se realizó. El PDF original no fue movido ni modificado.

## PDFs considerados

| archivo | score | motivo | uso |
| --- | --- | --- | --- |
| PolosGastro/Polos gastronómicos.pdf | 12 | nombre contiene 'polo'; nombre contiene 'gastronom'; ubicado en PolosGastro | usado |
| docs/references/gastronomia_caba_v1.pdf | 4 | nombre contiene 'gastronom' | no usado |

## Polos detectados

| polo_id | polo | tipo_area | nivel | estado | página |
| --- | --- | --- | --- | --- | --- |
| PG001_PALERMO_SOHO_HOLLYWOOD_Y_LAS_CANITAS | Palermo (Soho, Hollywood y Las Cañitas) | barrio | consolidado | normalizado | 1; 2 |
| PG002_VILLA_CRESPO | Villa Crespo | barrio | consolidado | normalizado | 1; 3 |
| PG003_PUERTO_MADERO | Puerto Madero | barrio | consolidado | normalizado | 1; 3 |
| PG004_SAN_TELMO | San Telmo | barrio | consolidado | normalizado | 1; 4 |
| PG005_CHACARITA | Chacarita | barrio | relevante | normalizado | 1; 4 |
| PG006_BELGRANO_BARRIO_CHINO_BAJO_BELGRANO_BELGRA | Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R) | barrio | consolidado | ambiguo | 1; 5 |
| PG007_RECOLETA | Recoleta | barrio | consolidado | normalizado | 1; 5-6 |
| PG008_CABALLITO | Caballito | barrio | relevante | normalizado | 1; 6 |
| PG009_COSTANERA_NORTE | Costanera Norte | zona_costera | relevante | requiere_validacion | 1; 6 |
| PG010_AVENIDA_CASEROS_BARRACAS | Avenida Caseros (Barracas) | avenida | relevante | normalizado | 1; 7 |
| PG011_MICROCENTRO_CENTRO_RENOVADO | Microcentro / Centro Renovado | zona_central | relevante | normalizado | 1; 7 |
| PG012_AVENIDA_CORRIENTES | Avenida Corrientes | avenida | requiere_revision | ambiguo | 1 |
| PG013_ABASTO | Abasto | subpolo | requiere_revision | ambiguo | 1 |
| PG014_AVENIDA_BOEDO | Avenida Boedo | avenida | candidato | base_pdf | 1 |
| PG015_DEVOTO | Devoto | barrio | incipiente | base_pdf | 1 |
| PG016_CORREDOR_DOHO_DONADO_HOLMBERG | Corredor DoHo / Donado-Holmberg | corredor | incipiente | base_pdf | 1 |
| PG017_VILLA_URQUIZA | Villa Urquiza | barrio | candidato | base_pdf | 1 |
| PG018_NUEVO_BAJO_EN_RETIRO_ESMERALDA_Y_PARAGUAY | Nuevo Bajo en Retiro (Esmeralda y Paraguay) | zona_central | incipiente | base_pdf | 1 |
| PG019_AVENIDA_FEDERICO_LACROZE_DESDE_LIBERTADOR_ | Avenida Federico Lacroze desde Libertador hasta Cabildo | avenida | candidato | base_pdf | 1 |
| PG020_PARQUE_SAAVEDRA_AVENIDA_GARCIA_DEL_RIO | Parque Saavedra / Avenida García del Río | subpolo | candidato | base_pdf | 1 |
| PG021_CIRCUITO_GASTRONOMICO_DE_PATERNAL | Circuito gastronómico de Paternal | barrio | candidato | base_pdf | 1 |
| PG022_VILLA_PUEYRREDON_AVENIDA_SAN_MARTIN | Villa Pueyrredón / Avenida San Martín | barrio | candidato | base_pdf | 1 |
| PG023_ABASTO_AVENIDA_CORRIENTES | Abasto - Avenida Corrientes | corredor | relevante | ambiguo | 7-8 |

## Locales destacados detectados

El listado de locales destacados requiere validación. No se asume que los locales sigan abiertos, no se asume dirección y no se los trata como padrón oficial.

| polo/sección | locales mencionados | página |
| --- | --- | --- |
| Palermo (Soho, Hollywood y Las Cañitas) | Don Julio; La Cabrera; Niño Gordo; Gran Dabbang; Mishiguene; Osaka; La Mar; Aldo’s (Palermo); Cosi Mi Piace; Oporto; Las Pizarras Bistro; Pa’ Pastar; Café Registrado; Francisca del Fuego (Distrito Arcos); Campo Bravo; Novecento; Morelia; Kansas; SushiClub | 2 |
| Villa Crespo | 878 Bar; La Fuerza; Julia; Apu Nudo; La Crespo; Sarkis; Malcriada; Picarón; Niño Gordo (zona límite) | 3 |
| Puerto Madero | Cabaña Las Lilas; Sottovoce; Chila; Happening; El Mercado (Faena); Patagonia Sur; La Parolaccia Casa Tua; Le Grill; Red Resto & Lounge | 3 |
| San Telmo | El Preferido de San Telmo; Café San Juan; Hierbabuena; La Brigada; El Hornero; Napoles; Pulpería Quilapán; Mercado de San Telmo (puestos varios) | 4 |
| Chacarita | Anafe; Bar Chacabuco; La Fuerza (sucursal Chacarita); Cantina Urondo; Bar Roma; Niño Gordo Burger House; La Alacena Trattoria | 4 |
| Belgrano (Barrio Chino + Bajo Belgrano + Belgrano R) | Hong Kong Style; China Rose; Ichisou; Ramen Neko; Ichiban; BAO Kitchen; Tori Tori; Alo’s Café; La Mar (referencia de la zona); Casa China; Anafe (original) | 5 |
| Recoleta | La Pecora Nera; La Biela; Fervor; El Sanjuanino; Sottovoce Recoleta; Piegari; Roux; Aramburu | 5-6 |
| Caballito | Patio de los Lecheros; La Vaca Atada; La Casona del Nonno; Tierra de Nadie; Café de la Plaza | 6 |
| Costanera Norte | Rodizio; Gardiner; Tequila (bar); Puerto Cristal (sobre la zona); El Muelle; Lo de Jesús (sucursal Costanera) | 6 |
| Avenida Caseros (Barracas) | Hierbabuena (segunda sede); Napoles Caseros; Caseros 3039; La Popular; Café Registrado (sucursal) | 7 |
| Microcentro / Centro Renovado | Tanta; Los Galgos; La Puerto Rico; Santos Manjares; La Continental (histórica); La Embajada; El Foro | 7 |
| Abasto - Avenida Corrientes | Güerrín; Las Cuartetas; El Palacio de la Pizza; Pertutti; La Reina Kunti; Moulin Bleu | 7-8 |

## Ambigüedades iniciales

- Avenida Corrientes y Abasto aparecen separados en el listado inicial, pero la sección de locales los agrupa como Abasto - Av. Corrientes.
- Belgrano R aparece en el listado inicial, aunque la sección detallada solo desarrolla Barrio Chino y Bajo Belgrano.
- Palermo se presenta como polo amplio y Las Cañitas aparece como subpolo interno.
- La línea 'Incipientes Devoto' sugiere condición emergente, pero no define alcance ni evidencia complementaria.
- Varios casos son corredores o avenidas sin polígono: DoHo, Federico Lacroze, Avenida Boedo, Avenida Caseros y Avenida San Martín.
- Nuevo Bajo en Retiro se define por el entorno Esmeralda-Paraguay, no por un límite territorial formal.
- Costanera Norte no permite inferir comuna única sin una delimitación geográfica previa.

## Próximos pasos sugeridos

- Validar si el PDF tiene origen oficial, interno o documental y asignar una ficha de fuente.
- Contrastar los polos con barrios, comunas y cartografía oficial antes de delimitar polígonos.
- Separar polos consolidados, corredores, avenidas, subpolos y zonas turísticas con criterios explícitos.
- Validar locales destacados con fuentes complementarias antes de usarlos como evidencia territorial.
- Definir si en una fase posterior corresponde conectar esta base con habilitaciones, oferta registrada u otras capas de DataGastro, sin tocar el pipeline general hasta aprobación explícita.
