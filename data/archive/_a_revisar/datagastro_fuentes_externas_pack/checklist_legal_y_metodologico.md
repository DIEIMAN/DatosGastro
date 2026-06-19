# Checklist legal y metodológico para nuevas fuentes DataGastro

Antes de integrar una fuente nueva, responder:

## 1. Acceso
- ¿La fuente es pública, API oficial, convenio, interna o scraping?
- ¿Hay términos de uso que permitan análisis y almacenamiento?
- ¿Hay costo o límite de consultas?

## 2. Privacidad
- ¿Incluye datos personales?
- ¿Incluye tarjetas, usuarios, teléfonos personales, domicilios de consumidores o repartidores?
- ¿Se puede agregar por comuna/barrio/mes?
- ¿Hay umbral mínimo por celda?

## 3. Universo
- ¿Qué representa la fuente?
  - oferta visible,
  - habilitación formal,
  - actividad real,
  - delivery,
  - pagos,
  - reservas,
  - movilidad,
  - reputación digital.
- ¿Qué NO representa?

## 4. Calidad
- ¿Tiene fecha de actualización?
- ¿Tiene identificador estable?
- ¿Tiene coordenadas o dirección normalizable por USIG?
- ¿Permite detectar activos/cerrados?
- ¿Se puede auditar la trazabilidad?

## 5. Integración
- ¿Se puede cruzar con DataGastro por nombre, dirección, coordenada o ID?
- ¿Se guardan datos raw?
- ¿Hay contrato de fuente en `source_contracts.py`?
- ¿Funciona con `--strict-real`?

Regla final: si una fuente requiere scraping de plataforma privada o contiene datos sensibles sin convenio, no entra al pipeline institucional.
