---
name: datagastro-abrir-rubro
description: Abrir, retomar o auditar un estudio de rubro gastronómico (panaderías, casas de pastas, pizzerías, heladerías, parrillas, el que venga) sobre las fuentes locales F01/F02. Usar SIEMPRE antes de escribir un builder, un clasificador o una cifra por rubro, y al tocar scripts/<rubro>/ o outputs/<rubro>/.
---

# Abrir un estudio de rubro

Receta completa: `docs/estudios_de_rubro/COMO_ABRIR_UN_RUBRO_NUEVO.md`. Lector:
`docs/estudios_de_rubro/LECTOR_FUENTES_LOCALES.md`. Modelos que ya funcionan:
`scripts/panaderias/` (el más reciente) y `scripts/casas_pastas/`.

## Orden que no se altera

1. **Alcance escrito antes que código**: `docs/<rubro>/ALCANCE_Y_DEFINICION.md` con universos
   A (núcleo), B (frontera, se cuenta aparte) y C (fuera, etiquetado con el motivo). Manda el rubro
   habilitado, no el nombre de fantasía. Medir la zona gris (cuántas filas caen en rubros de
   frontera) y, si es grande, acordar la definición con Diego antes de codificar.
2. **Perfil de las fuentes**: `make perfil-f02` (o `.venv/Scripts/python.exe -m
   scripts.shared.fuentes_locales.f02`). Sale con 1 si algún archivo queda en cero filas o sin
   rubro; no se sigue hasta que dé 0.
3. **Clasificador aparte del builder**: `scripts/<rubro>/<rubro>_patterns.py` con `classify(...)`
   que devuelve `nivel`, `patron_detectado`, `confianza_categoria`, `motivo_categoria`, sobre
   texto normalizado con el módulo compartido.
4. **Lectura solo por el módulo compartido**: `from scripts.shared.fuentes_locales import
   iter_f01, iter_f02`. Nunca copiar un lector de otro estudio: F02 son ocho archivos con
   delimitador, codificación y columnas distintas, y un lector escrito contra uno devuelve cero
   para los demás sin fallar. Si falta algo, se agrega al módulo y se corren sus tests.
5. **Unidad de conteo = habilitación**: agrupar por `reg.clave_habilitacion` (`solicitud` +
   unidad funcional en los archivos viejos, `disposicion` en el de 2025). Nunca por partida (es el
   inmueble: el 51 % aloja más de una habilitación) ni por `id_registro`. El padrón «2025»
   republica trámites viejos: unir por partida + domicilio + año cuando hay exactamente un grupo
   de cada lado, y completar campos vacíos del representante con los del grupo.
6. **Correr sin pisar lo publicado**: `make rubro RUBRO=<rubro> OUT=outputs/_prueba/<rubro>`;
   comparar números; recién después sobre `outputs/<rubro>/`.
7. **Cierre**: `make test`; perfil sin archivos en cero; serie por año sin huecos en el medio (si
   los hay, es el lector); si sale PDF, `make pdf-check FILE=…` y mirar las páginas; `docs/<rubro>/
   ESTADO.md` con fecha de corte, cifras y unidad de conteo; handoff en `docs/revisiones/`.

## Lo que hay que decir del dato, siempre

- F02 son habilitaciones otorgadas, no locales activos ni stock (guardrail 5).
- Las filas 2015–2024 no traen nombre; titulares y CUIT no se leen (guardrail 7).
- El archivo «2025» no trae habilitaciones de 2025; el «2023» está subrepresentado en origen.
- Un local habilitado dos veces entra dos veces: publicar la cota (en panaderías, 6,8 %).

## Antes de cualquier número que se vaya a leer como conclusión

`agent_skills/shared/datagastro_metodo_experimental.md`: bandas escritas antes de correr, umbrales
que no se mueven, sensibilidad, y «no encontramos» no es «no existe».
