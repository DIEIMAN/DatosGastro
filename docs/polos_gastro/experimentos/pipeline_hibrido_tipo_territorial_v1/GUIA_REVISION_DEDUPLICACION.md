# Guía de revisión de deduplicación

La carpeta interna contiene 200 pares estratificados. La clasificación automática es sólo una propuesta. Completar `decision_humana` con uno de estos valores:

- `DUPLICADO`: misma entidad real representada dos veces.
- `DISTINTO`: entidades diferentes.
- `AMBIGUO`: evidencia insuficiente.
- `COLOCALIZACION_VALIDA`: entidades distintas en la misma parcela, galería, mercado o dirección.

Revisar nombre original y normalizado, distancia, dirección/referencia, vecino más cercano y segundo vecino compatible. No cambiar umbrales hasta completar y auditar la muestra. No copiar nombres o referencias al paquete compartible.
