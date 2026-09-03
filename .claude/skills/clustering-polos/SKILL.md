---
name: clustering-polos
description: >
  Clustering geoespacial de densidad con HDBSCAN / scikit-learn para generar
  candidatos de polos gastronómicos a partir de puntos. Usar para explorar
  agrupamientos por densidad. El clustering GENERA CANDIDATOS, no descubre
  polos: la decisión editorial y el relevamiento confirman (línea metodológica
  vigente del subproyecto Polos).
---

# HDBSCAN / scikit-learn — clustering de densidad

Instalado en `.venv-tools`. Ejecutar con `.venv-tools\Scripts\python.exe`.

## Uso básico

```python
import numpy as np
from sklearn.cluster import HDBSCAN  # también existe el paquete hdbscan clásico

# X: coordenadas proyectadas EN METROS (nunca lat/lon crudos)
# p.ej. GeoDataFrame.to_crs(epsg=5347) o similar métrico para CABA
labels = HDBSCAN(min_cluster_size=15, min_samples=5).fit_predict(X)
# label -1 = ruido (fuera de todo cluster)
```

## Reglas metodológicas (del propio proyecto — no re-litigar)

1. **Proyectar a CRS métrico antes de clusterizar**; distancias en grados
   distorsionan la densidad.
2. HDBSCAN es adaptativo: «mismos parámetros» NO es «misma vara» entre zonas de
   densidad distinta — declararlo como límite en cualquier comparación
   norte/sur (lección registrada del barrido de la Ciudad).
3. Los cortes de densidad tipo Jenks son óptimos, no naturales: la densidad es
   un atributo del polo, no un criterio de existencia.
4. Todo resultado que se vaya a leer como conclusión pasa por
   `agent_skills/shared/datagastro_metodo_experimental.md` antes de correrse.
5. Los candidatos van a borradores en `outputs/`; ningún cluster entra a un
   informe sin la cadena producción → auditoría independiente → decisión.
