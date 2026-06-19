# Skill 03 — Privacidad y datos sensibles

Regla central: **trabajar con agregados, perfiles de columnas, conteos y diagnósticos.**
**No exportar filas individuales sensibles.**

## 1. Qué se considera sensible

| Categoría | Ejemplos | Tratamiento |
| --- | --- | --- |
| Identificadores de personas | DNI, CUIT, CUIL, CBU | **Nunca** exportar. Redactar en cualquier muestra. |
| Contacto | email, teléfono, celular, WhatsApp, dirección particular | **Nunca** exportar a nivel individual. |
| Nombres de personas | titulares, referentes, contactos | No exportar como fila; solo agregados. |
| Financiero individual | facturación, ventas, recaudación, montos, transacciones por comercio | Solo **agregado** con umbral mínimo de comercios por celda. |
| Comercios individuales | razón social + dirección + datos económicos juntos | Evitar la combinación reidentificable. |
| Participantes de eventos | inscriptos, feriantes, proveedores con sus datos | Conteos y categorías, no listados nominales. |
| Comprobantes / documentación | constancias AFIP/ARCA/AGIP, facturas | No procesar contenido individual ni exportarlo. |

## 2. Qué SÍ se puede producir

- **Perfiles de columnas**: nombre de columna, tipo inferido, % de nulos, valores únicos,
  riesgo de sensibilidad. Sin valores reales.
- **Conteos y agregados**: por comuna, barrio, rubro, mes, categoría, estado.
- **Diagnósticos de calidad**: duplicados detectados (por hash/clave, sin exponer el contenido),
  completitud, consistencia.
- **Muestras redactadas**: si hace falta ilustrar estructura, redactar CUIT/DNI/email/teléfono y
  cualquier cadena que parezca un valor sensible.

## 3. Reglas operativas

1. **Umbral mínimo por celda**: ninguna celda agregada debería representar a un único comercio o
   persona. Definir un mínimo (p. ej. ≥ 5) antes de publicar cruces finos.
2. **No persistir raw sensible en el repo**: los crudos internos van a `data/internal_raw/`
   (ignorado por Git) o se leen directo de Drive sin copiar el contenido sensible.
3. **Salidas internas a carpeta ignorada**: todo output con cualquier riesgo va a
   `outputs/analisis_interno/` (ignorada por Git, ver `.gitignore`).
4. **Redacción por defecto**: al inspeccionar archivos, asumir que pueden contener datos
   personales. Redactar antes de mostrar.
5. **Sin muestras con valores reales** en informes, resúmenes o commits.
6. **Separar lo publicable de lo no publicable**: cada análisis interno debe declarar qué se
   puede usar en un informe y qué no debe salir del área (ver skill 07).

## 4. Patrones de redacción recomendados

Reutilizar el enfoque ya usado en `outputs/analisis_interno/eventos_2026/_analizar_eventos_2026.py`:

- `(cuit|cuil|dni)[ _-]*\d+` → `\1 [redactado]`
- `\b\d{8,11}\b` → `[numero_redactado]`
- email → `[email_redactado]`
- Encabezados de planilla que parecen ser un valor (no un nombre de campo) → renombrar a
  `columna_N_redactada_posible_valor`.

## 5. Antes de exportar cualquier CSV interno, preguntarse

1. ¿Hay alguna columna que identifique a una persona o comercio individual? → agregar o quitar.
2. ¿Algún número podría ser DNI/CUIT/teléfono/monto individual? → redactar o agregar.
3. ¿El archivo va a una carpeta ignorada por Git? → verificar `.gitignore`.
4. ¿El informe que lo cita expone filas individuales? → reemplazar por agregados.

Si alguna respuesta es dudosa, **no se exporta** hasta resolverlo.
