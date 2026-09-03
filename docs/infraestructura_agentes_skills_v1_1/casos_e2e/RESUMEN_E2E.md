# Resumen E2E V1.1

Fecha: 2026-07-11

Salidas: `outputs/infraestructura_agentes_skills_v1_1/casos_e2e/`

```json
[
  {
    "caso": 1,
    "ok": true,
    "dir": "outputs\\infraestructura_agentes_skills_v1_1\\casos_e2e\\caso1_investigador_documental"
  },
  {
    "caso": 2,
    "ok": true,
    "intact": true,
    "map_ok": true
  },
  {
    "caso": 3,
    "ok": true,
    "dir": "outputs\\infraestructura_agentes_skills_v1_1\\casos_e2e\\caso3_integrador"
  },
  {
    "caso": 4,
    "ok": true
  },
  {
    "caso": 5,
    "ok": true,
    "results": {
      "caso_correcto": {
        "returncode": 0,
        "stdout": "[OK] C:\\proyectos\\Gastronomia\\DataGastro\\outputs\\infraestructura_agentes_skills_v1_1\\casos_e2e\\caso5_kpis\\doc_ok.md: 2 KPIs presentes",
        "stderr": ""
      },
      "valor_discrepante": {
        "returncode": 1,
        "stdout": "[FALLA] C:\\proyectos\\Gastronomia\\DataGastro\\outputs\\infraestructura_agentes_skills_v1_1\\casos_e2e\\caso5_kpis\\doc_bad.md:\n   falta '99' (features_presentacion_pm)",
        "stderr": ""
      },
      "universo_lock": {
        "returncode": 0,
        "stdout": "[OK] C:\\proyectos\\Gastronomia\\DataGastro\\outputs\\infraestructura_agentes_skills_v1_1\\casos_e2e\\caso5_kpis\\doc_universo.md: 1 KPIs presentes",
        "stderr": ""
      },
      "nota_no_verificable": {
        "comentario": "validate_kpis solo comprueba presencia de strings del lock; la no verificabilidad se documenta cualitativamente",
        "documento": "doc_no_verificable.md"
      }
    }
  }
]
```
