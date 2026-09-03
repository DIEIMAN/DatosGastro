# QA final repeticiones híbridas v2

Estado: **EXPERIMENTAL / NO OFICIAL**.

## Controles

- Sin API: **OK**.
- Sin Google Places: **OK** (no se realizaron llamadas; solo se leyó el universo local sanitizado ya almacenado).
- Sin descargas: **OK**.
- Sin datos fuente modificados: **OK**.
- Sin cambios en Fase 25, Fase 26, v1–v4.2 y prototipos híbridos v1: **OK** (333 archivos protegidos comparados; 0 cambios).
- Sin KMeans: **OK**.
- Privacidad: **OK** (0 hallazgos automáticos).
- PNG no blancos: **OK** (6 mapas).
- ZIP: se valida después de su creación.

## Git

El script no ejecuta `git add`, commit, push ni staging. La verificación final del estado Git se realiza fuera del script para distinguir cambios preexistentes.

## Límites

La ausencia de patrones automáticos no reemplaza revisión humana. Las geometrías son experimentales y los buffers son convenciones cartográficas orientativas.
