# Lectura previa · ronda 15

Estado: **EXPERIMENTAL / NO OFICIAL**. Esta nota se fija antes de ejecutar el reparto.

## Universo y geometrías

- Locales: `base/local.csv`, filtro `anillo == 'nucleo' AND apto_geometria == True`.
- Z50 Av. Montes de Oca: P066 de `borrador_polos/polos_publicables.geojson`, la misma
  geometría usada por `ronda_14/montes_de_oca_seis_vias.csv`.
- Z51 Iriarte–California–Vieytes: P008 de la misma capa.
- Z54 Av. Sáenz: P024 de la misma capa.
- R11 y Z40: `geometria_r7/zonas_r7.geojson`.

Las geometrías P son soportes analíticos; no se adoptan como límites institucionales.

## Lectura fijada antes de correr

Para cada par se medirán área de intersección, superficie perdida y registros compartidos en
los dos sentidos. No se usará `covers()` ni otro predicado de contención.

- **Recomendar fusión:** superficie de la zona nueva perdida fuera del candidato ≤ 1 m² y cero
  registros del universo ERR-10 de la zona nueva fuera del candidato.
- **Recomendar mantener separada:** intersección ≤ 0,01 m² y cero registros compartidos.
- **Reparto parcial:** cualquier resultado intermedio. Se informan los números y decide Diego.

El conteo vigente permanece en 41 polos admitidos. Las recomendaciones sólo informarán el
conteo contrafáctico si Diego las firma; no modificarán el criterio ni el documento por sí solas.

## Z55

La afirmación de la feria de Av. Mariano Acosta sólo abrirá la vía C si aparece en una fuente
pública trazable —registro oficial, norma o permiso publicado—. Una mención sin URL ni
procedencia no alcanza. La ausencia en un padrón se redactará como “no se encontró”, nunca como
prueba de inexistencia.
