# Evaluacion de la preview - Polos Borrador 3 + Design System DGDGAS

Fecha: 2026-07-01. Documento interno de evaluacion visual y metodologica. Evalua el prototipo
`preview_polos_borrador3_design_system.html`. No es aprobacion de canonizacion ni de aplicacion
productiva.

## 1. El diseno mejora la legibilidad?

**Si.** Frente al Markdown plano del Borrador 3, la preview aporta: jerarquia tipografica clara
(display para portada, h1 de seccion, cuerpo 10.5pt con interlineado 1.5), eyebrows en mono que
anclan cada pagina a su rol (lectura ejecutiva / anexo tecnico), y cajas diferenciadas por funcion
(lectura, advertencia, nota) que hacen visibles los limites metodologicos sin interrumpir el texto.
La columna "lectura prudente" dentro de la tabla es el mayor avance: la advertencia viaja pegada al
dato, que era la regla mas dificil de sostener en Markdown.

## 2. Las tablas se ven institucionales?

**Si.** Header en azul institucional `brand.primary` con texto `on_brand_soft`, zebra tenue,
divisores suaves y caption en mono con fuente y fecha de corte dan un registro de documento de
gestion publica, no de dashboard. Riesgo menor: con 32 filas la zebra y los chips repetidos pueden
volverse monotonos; esta preview solo probo 8 filas.

## 3. Los chips ayudan o distraen?

**Ayudan, con una condicion cumplida y una pendiente.** La condicion cumplida: el texto de la
etiqueta es obligatorio y el color nunca es el unico significado, de modo que el chip funciona
tambien en fotocopia o impresion en grises. La pendiente: en una tabla de 32 filas, cinco o seis
chips distintos pueden competir con la columna de lectura prudente; conviene probar la version
"tabla" con dot mas chico (`chip.dot_small_size`) o chips solo con dot+texto sin fondo. Los colores
elegidos (verdes y azules desaturados, ambar para debil, gris para en espera) evitan la lectura
semaforica alarmista: no hay rojo en ningun estado de documentacion, lo cual es correcto.

## 4. Los disclaimers son suficientemente visibles?

**Si en esta preview; a vigilar en derivados.** Hay cuatro niveles: cinta superior en las tres
paginas, caja de alcance en portada con borde de validacion, caja "Alcance / advertencia" en la
pagina de capa objetiva y frase obligatoria al pie. Ninguno usa lenguaje alarmista y ninguno queda
escondido en pie de pagina. Punto a vigilar: la cinta usa caption 8pt; si se imprime en A4 real
sigue legible, pero no deberia achicarse mas.

## 5. La portada se siente DGDGAS?

**Si.** Marca publica DGDGAS con su desarrollo institucional completo, azul profundo, un solo
acento calido y ninguna estetica de startup o de IA. DataGastro no aparece en ninguna de las tres
paginas. El panel oscuro con filete de acento es sobrio y distintivo a la vez; es la unica apuesta
visual fuerte de la pieza y esta contenida en la portada.

## 6. Hay riesgo de que parezca informe final?

**Bajo, por diseno.** Precisamente porque el diseno institucional "viste" el contenido, el riesgo
existiria si se quitara la cinta de preview o la caja de alcance de portada. Mitigaciones ya
incluidas: cinta en las 3 paginas, subtitulo "Borrador interno de trabajo / referencia
metodologica", caja de alcance en portada y footer "Preview interna de diseno". Recomendacion:
cuando se aplique diseno a una copia real del Borrador 3, la marca de estado del documento
(borrador/preview) debe ser un componente obligatorio del template, no un agregado manual.

## 7. Hay riesgo de que la capa objetiva se lea como ranking?

**Bajo en esta preview.** Salvaguardas aplicadas: no se muestra ningun numero de indice; los
niveles aparecen solo en prosa ("senal alta", "senal media") dentro de frases con su limitacion;
los ejemplos estan en tarjetas de igual tamano y sin orden jerarquico; el chip de todos los casos
de contexto es el mismo (no hay chip "alto/medio/bajo"); y la caja de advertencia precede a los
ejemplos. Riesgo residual: si en el futuro se agregara una columna de nivel de senal a la tabla
ejecutiva, o un mapa coropletico, la lectura de ranking reapareceria. Regla sugerida: el nivel de
senal nunca entra como columna ordenable ni como escala de color de mapa en piezas ejecutivas.

## 8. Que habria que ajustar antes de aplicar al Borrador 3 real

1. **Completar `state_details`** para contexto, no_delimita, validacion, interno, alerta y anexo;
   en la preview dos chips usan derivaciones ad hoc.
2. **Probar la tabla completa (32 filas)** con corte de pagina A4 y evaluar chips en tamano tabla.
3. **Resolver tipografia:** decidir si el fallback (Arial/Calibri) es aceptable como definitivo o
   si se autoriza instalar Libre Franklin / Source Sans 3; la preview solo demuestra el fallback.
4. **Medir contraste AA** de on_brand_soft sobre brand.primary y de los textos de chip.
5. **Tokenizar la marca de estado del documento** (cinta borrador/preview/final) como componente
   obligatorio del template.
6. **Definir el patron de footer productivo** (el patron `DGDGAS - {proyecto} - {tipo}` funciono
   bien y puede adoptarse).
7. **Mantener el orden del Borrador 2 como invariante** en cualquier render: el template no debe
   permitir reordenar por senal.
8. **Recien despues**, aplicar sobre una copia controlada del Borrador 3 (nunca sobre los archivos
   de `docs/polos_gastro/fase9_borrador_3/`), con QA visual y de privacidad previo a cualquier
   PDF/DOCX.

## Conclusion

La preview cumple su objetivo: demuestra que el Design System mapeado sirve para piezas
institucionales DGDGAS prudentes y detecta ajustes concretos (estados incompletos, tabla larga,
tipografia, contraste) que conviene resolver antes de canonizar tokens o aplicar diseno al
Borrador 3 real. No habilita, por si misma, informe final, PDF, DOCX ni actualizacion de tokens
canonicos.
