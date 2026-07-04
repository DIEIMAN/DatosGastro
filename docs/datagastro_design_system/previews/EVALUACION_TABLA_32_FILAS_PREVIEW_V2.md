# Evaluacion de la tabla completa de 32 filas - Preview v2

Fecha: 2026-07-01. Documento interno. Evalua las hojas 3 a 5 de la preview v2 (tabla completa del
Borrador 3 simulada en A4). No es aprobacion de diseno productivo.

## 1. La tabla completa es legible?

**Si, con la variante densa.** La tabla completa usa 8pt (caption) con padding reducido
(1.8 x 2.5 mm), frente a los 9pt de la tabla ejecutiva. A ese tamano las 6 columnas entran en los
170 mm de ancho util y cada fila ocupa 1-2 lineas. La legibilidad es aceptable para un anexo de
trabajo; para un documento que jefatura vaya a leer en papel, 8pt esta en el limite inferior: no
conviene bajar mas ni sumar columnas.

## 2. Paginado: entra en A4?

**No entra en una pagina; requiere 3 hojas.** Con la densidad probada, el limite practico es de
11-13 filas de datos por hoja A4 (contando cinta de estado, titulo, intro/captions y filas
separadoras de grupo). El corte aplicado fue:

- Hoja 1: areas nucleo (6) + zonas relevantes (5) = 11 filas.
- Hoja 2: emergentes y candidatos a validar (9 filas, en el orden original intercalado).
- Hoja 3: anexo / casos secundarios (8) + en espera de evidencia (4) = 12 filas.

**Propuesta de corte por grupo (validada visualmente):** los cortes coinciden con los bloques
ejecutivos del Borrador 3, de modo que ninguna pagina corta un grupo por la mitad. Punto a
resolver: los candidatos a validar (Corrientes, Paternal) estan intercalados entre emergentes en
el orden original. Separarlos en su propia seccion reordenaria el universo; se resolvio con un
bloque unico "Emergentes y candidatos a validar" + columna Grupo por fila + nota de paginado. Es
la solucion mas fiel a la regla "mantener orden del Borrador 3".

## 3. Cuerpo o anexo?

**Anexo.** La tabla completa es material de trabajo: 32 filas con lectura prudente por fila piden
lectura lenta, no lectura ejecutiva. La recomendacion es la que ya practica la preview: en el
cuerpo, la tabla ejecutiva breve (6-8 casos representativos); en el anexo, la tabla completa en
3 hojas con cortes por grupo. Esto ademas reduce el riesgo de que la tabla completa se cite fuera
de contexto.

## 4. Partir por grupos?

**Si, con separadores de grupo dentro de una tabla continua** (filas separadoras con el nombre del
bloque), no como tablas independientes. Los separadores codifican estructura real del universo,
mantienen el encabezado unico y evitan que cada fragmento parezca un "top" propio. Repetir el
encabezado de columnas en cada hoja (como hace la preview) es necesario para lectura en papel.

## 5. Que columnas sobran para una version presentable

Del CSV de trabajo (14 columnas), para una version presentable **sobran en cualquier tabla
visible**:

- `grupo_base_fase5` (trazabilidad interna).
- `recomendacion_fase8_liviana` y `evidencia_fase8_liviana` (insumo de decision, no de lectura;
  ademas nombran medios/fuentes que requieren QA editorial antes de publicarse).
- `usar_capa_objetiva_en_cuerpo_si_no` y `usar_capa_objetiva_en_anexo_si_no` (columnas de control
  interno).
- `observacion_borrador_3` (texto repetido en las 32 filas; funciona mejor como nota unica al pie).
- `senal_objetiva_contexto` (descripcion larga repetida; queda cubierta por el nivel + la nota).

## 6. Que columnas deberian ir al anexo tecnico

La tabla del anexo quedaria con 6 columnas (las probadas en la preview): **caso, grupo, tipo
territorial, estado documental, senal de contexto (cualitativa), lectura prudente** — donde
"lectura prudente" fusiona `lectura_prudente_capa_objetiva` con `limitacion_territorial`, que por
separado son redundantes. Las columnas de recomendacion/evidencia de Fase 8 liviana, si se decide
mostrarlas, van en una tabla separada del anexo de decisiones (no mezcladas con la tabla
territorial), y solo despues del QA editorial de fuentes.

## 7. Hay riesgo de ranking?

**Bajo con el diseno probado; el punto sensible es la columna "Senal (contexto)".** Mitigaciones
aplicadas: la columna usa texto plano (alta/media/baja/no calculable) sin color, sin barras y sin
numeros; el orden es el del Borrador 3; la lectura prudente esta pegada en la columna contigua; el
caption de cada hoja repite "la senal es contexto, no ranking". Riesgo residual: un lector puede
recorrer la columna buscando las "altas". Si la revision humana lo considera demasiado sensible,
la alternativa conservadora es quitar la columna de la tabla y dejar la senal solo en las fichas
del anexo tecnico. Regla dura en cualquier caso: la columna nunca debe ser ordenable ni colorearse
por nivel.

## 8. El diseno aguanta el largo?

**Si.** La zebra manual por bloque, los separadores de grupo y los chips en variante tabla (dot de
1.6 mm) mantienen el ritmo visual en las 3 hojas sin saturar. Observaciones para la version
productiva:

- Los chips repetidos (8 "Media" seguidos en la hoja 3) son tolerables pero monotonos; una
  alternativa es chip solo en la primera aparicion por bloque y texto plano en el resto — a
  decidir en QA visual.
- El render PDF/DOCX real puede romper filas entre paginas: el template productivo debe fijar
  "no partir fila" y "repetir encabezado", que HTML simula pero no garantiza en otros formatos.
- Con nombres largos ("Federico Lacroze / Libertador a Cabildo", "Nuevo Bajo en Retiro /
  Esmeralda y Paraguay") la columna Caso necesita ~30 mm; no agregar columnas nuevas sin quitar
  otras.

## Conclusion

La tabla completa de 32 filas es usable como **anexo en 3 hojas A4 con cortes por grupo**, con la
tabla ejecutiva breve como unica tabla del cuerpo. La estructura probada (6 columnas, separadores
de grupo, chips en variante tabla, captions con advertencia) aguanta el largo y mantiene bajo el
riesgo de lectura de ranking. Queda a decision humana si la columna de senal permanece en la tabla
o se traslada a las fichas del anexo tecnico.
