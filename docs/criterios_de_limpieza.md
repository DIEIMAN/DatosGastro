# Criterios de limpieza

1. Detectar encoding con chardet.
2. Reparar mojibake con ftfy.
3. Normalizar barrios al catálogo oficial.
4. Derivar comuna desde barrio cuando sea posible.
5. Normalizar direcciones con USIG.
6. Detectar duplicados por nombre normalizado + cuadra.
7. Marcar vigencia dudosa de F01 si no hay verificación posterior a 2020.
8. Separar No disponible, No encontrado en fuente pública y Dato inferido.
