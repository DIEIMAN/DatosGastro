# QA make_valid — R08 y R12

Gate fijado antes de correr: geometría final válida/no vacía; mismo conteo point-in-polygon; delta de área ≤10 m² y ≤0.001 %.

| polo_id | valido_antes | explicacion_antes | valido_despues | explicacion_despues | area_m2_antes | area_m2_despues | delta_area_m2 | delta_area_pct | perimetro_m_antes | perimetro_m_despues | delta_perimetro_m | partes_antes | partes_despues | locales_antes | locales_despues | gate_no_cambio_material |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R08 | SI | Valid Geometry | SI | Valid Geometry | 2938286.594034 | 2938286.594034 | 0.0 | 0.0 | 14562.234511 | 14562.234511 | 0.0 | 6 | 6 | 746 | 746 | PASS |
| R12 | NO | Self-intersection[5648629.20585559 6170049.33255717] | SI | Valid Geometry | 1537172.697631 | 1537172.697631 | 8e-09 | 0.0 | 13653.885129 | 13605.472125 | -48.413004 | 6 | 6 | 875 | 875 | PASS |

R08 ya resulta válida con la versión local de GEOS y `make_valid` es identidad. R12 corrige la autointersección puntual: el área y los 875 puntos se preservan; la disminución de perímetro corresponde a la eliminación de segmentos duplicados en el cruce.
