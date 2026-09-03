# Reproducción del preflight V4

```powershell
cd C:\proyectos\Gastronomia\DataGastro
.venv\Scripts\python.exe scripts\polos_gastro\expansion_candidatos_v4_preflight\build_preflight_expansion_candidatos_v4.py
```

## Determinismo

- Mismas capas de entrada ⇒ mismos IDs de celda y áreas (buffers fijos, grilla regular).
- No usa reloj ni random.
- Comparar `checksums.sha256` entre dos corridas.

## Dependencias

geopandas, pandas, shapely (venv del proyecto).

## No requiere

- API keys
- red (salvo que falten archivos locales)
