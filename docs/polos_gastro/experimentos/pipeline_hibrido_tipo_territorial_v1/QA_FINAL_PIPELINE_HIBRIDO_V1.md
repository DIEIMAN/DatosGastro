# QA final pipeline híbrido v1

Estado: APTO PARA REVISIÓN INTERNA; experimental/no oficial.

- Auditoría corregida: clusters HDBSCAN y polígonos separados.
- Estabilidad: dimensiones desagregadas.
- Trazabilidad: IDs y fuentes preservados; sin doble conteo introducido.
- KMeans: no usado.
- Callejero: capa local de 31.961 tramos; sin nombres inventados.
- Hashes críticos: 27/27 sin cambios; cambiados=0.
- APIs/descargas: ninguna.
- Datos fuente/Fase25/Fase26/v1-v4.2: sin cambios.
- Librerías instaladas: ninguna. Se usó `.venv` existente (scikit-learn 1.9.0, networkx 3.6.1).
- Carpeta interna deduplicación: excluida por `.gitignore` local del experimento; no incluir en paquete compartible.
- Git: verificar al cierre; no se ejecutó add, commit, push ni staging.

Limitaciones: bootstrap por bloques usa submuestreo de 80% sin reemplazo; los buffers son orientativos; dependencia Places no desaparece por cambiar geometría; nombres y jerarquías requieren decisión humana.
