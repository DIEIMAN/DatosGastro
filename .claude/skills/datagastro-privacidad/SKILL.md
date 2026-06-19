---
name: datagastro-privacidad
description: Manejo de datos personales y sensibles en DataGastro. Usar al perfilar, analizar o exportar cualquier dato interno con contactos, CUIT/DNI, teléfonos, facturación, ventas, transacciones, nombres de personas o participantes de eventos.
---

# Privacidad y datos sensibles

Contenido canónico: `docs/skills_claude/03_privacidad_datos_sensibles.md`.

Regla central: trabajar con **agregados, perfiles de columnas, conteos y diagnósticos**. **No
exportar filas individuales sensibles.**

- Nunca exportar: DNI, CUIT/CUIL, CBU, email, teléfono, nombres de personas, montos/ventas por
  comercio, comprobantes.
- Sí producir: perfiles de columnas (sin valores), conteos/agregados por comuna/barrio/rubro/mes,
  diagnósticos de calidad, muestras redactadas.
- Umbral mínimo de comercios/personas por celda. Salidas a `outputs/analisis_interno/` (ignorada
  por Git). Redactar por defecto cualquier valor que parezca sensible.
