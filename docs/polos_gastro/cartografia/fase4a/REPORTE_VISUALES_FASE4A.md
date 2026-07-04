# Reporte visual comparativo — Fase 4A

Fecha: 2026-06-29.

Cierre de la fase de rediseño visual y prototipo de mapa territorial. Los PNG nuevos están en
`outputs/polos_gastro/graficos/fase4a/`; los PNG anteriores **no se sobrescribieron**.

---

## 1. Qué se regeneró

Siete PNG nuevos (sufijo `_v2` / `_v1`) + la base `base_cartografica_visual_polos_gastro.csv`:

- `universo_polos_por_grupo_v2.png`
- `precision_delimitacion_polos_v2.png`
- `familias_territoriales_polos_v2.png`
- `mapa_conceptual_polos_gastro_resumido_v2.png`
- `mapa_conceptual_polos_gastro_completo_v2.png`
- `mapa_estatico_caba_polos_gastro_v1.png`
- `mapa_estatico_caba_polos_gastro_nucleo_v1.png`

## 2. Qué problemas anteriores se corrigieron

| Problema (auditoría previa) | Estado |
| --- | --- |
| Resumido y "_resumido" eran idénticos / alias confuso | Resuelto: resumido v2 propio, con criterio claro (núcleo+relevantes+candidatos). |
| Mapa conceptual completo con etiquetas solapadas | Resuelto: spread vertical por celda; sin encimado. |
| Caja "No mapeados" tapaba etiquetas | Resuelto: se eliminó la caja; los descartados no se listan sobre el gráfico. |
| `familias` con barras apiladas densas | Resuelto: barras agrupadas, comparables. |
| Faltaba mapa estático GeoPandas | Resuelto: mapa territorial real con barrios oficiales (+ versión núcleo). |
| Etiquetas encimadas por barrio compartido en el mapa estático | Resuelto: etiqueta combinada por barrio (Palermo, Villa Urquiza/DoHo, etc.). |

## 3. Qué mapa territorial se logró

Un **mapa estático real de CABA** (GeoPandas + barrios oficiales de Buenos Aires Data) que:
- pinta los 48 barrios en gris y **resalta los barrios asociados** a polos por grupo
  (núcleo / relevante / candidato);
- usa barrios como **referencia territorial**, con nota visible de que **no delimita** polos;
- tiene dos versiones: completa (núcleo+relevantes+candidatos) y núcleo (núcleo+relevantes).

No usa coordenadas Google, no inventa polígonos de polos, no geocodifica locales.

## 4. Qué visuales entran al informe

`apto_informe`:
- `universo_polos_por_grupo_v2.png`
- `precision_delimitacion_polos_v2.png`
- `familias_territoriales_polos_v2.png`
- `mapa_conceptual_polos_gastro_resumido_v2.png`
- `mapa_estatico_caba_polos_gastro_v1.png`
- `mapa_estatico_caba_polos_gastro_nucleo_v1.png`

## 5. Qué visuales quedan internos

`apto_con_ajustes` / interno:
- `mapa_conceptual_polos_gastro_completo_v2.png` — apto para **anexo** o revisión interna (más
  denso; el cuerpo del informe puede usar el resumido).

## 6. Qué visuales se descartan

**Ninguno.** Los PNG de la fase anterior (`graficos/*.png` sin sufijo) quedan como histórico,
no se borran; el informe usará los `fase4a/`.

## 7. Limitaciones metodológicas

- **Barrio asociado ≠ polo**: la base territorial es referencia, no delimitación.
- Varios polos comparten barrio (Palermo, San Nicolás): se etiquetan combinados.
- Precisión de delimitación: 3 alta / 11 media / 16 baja / 2 sin → no hay polígonos de polos.
- Subzonas (Barrio Chino, Microcentro, Costanera Norte) se aproximan al barrio contenedor.
- Los visuales **no** miden intensidad gastronómica ni cantidad de locales activos.

## 8. Decisión recomendada para el futuro informe

- **Cuerpo del informe**: usar `mapa_estatico_caba_polos_gastro_nucleo_v1.png` (territorial,
  limpio) + `mapa_conceptual_resumido_v2` + los 3 gráficos metodológicos v2.
- **Anexo**: `mapa_estatico_caba_polos_gastro_v1.png` (completo) y/o
  `mapa_conceptual_completo_v2` para mostrar todo el universo.
- Mantener siempre la **nota metodológica** y la **atribución Buenos Aires Data**.
- No avanzar a polígonos de polos ni a mapa "oficial".

> Ver el plan de armado en `docs/polos_gastro/PLAN_ENSAMBLADO_INFORME_POLOS_GASTRO.md`.
