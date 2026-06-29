# Regenerar informe final V4_1 de mercados gastronómicos CABA

V4_1 es una corrección formal quirúrgica de V4:

- mantiene 14 páginas y el mismo orden;
- no cambia datos, conteos, universo ni estados;
- corrige tildes, nombres y microcopy institucional;
- reemplaza el separador técnico Madrid -> CABA por una frase institucional;
- genera un pack V4_1 separado para comparar con V4.

## Comandos

```powershell
python src\mercados_caba\build_pdf_final_v4_1_from_v3.py
python src\mercados_caba\validate_mercados_final_v4_1.py
```