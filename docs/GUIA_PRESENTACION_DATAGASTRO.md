# Guía rápida de presentación — DataGastro

## Pieza recomendada para una primera reunión

Usar la notebook:

```bash
jupyter notebook notebooks/05_informe_ejecutivo_datagastro.ipynb
```

o abrirla desde VS Code.

Para exportar una version HTML:

```bash
jupyter nbconvert --to html notebooks/05_informe_ejecutivo_datagastro.ipynb
```

No hace falta generar PDF en la demo interna si requiere dependencias externas.

La notebook está pensada como informe ejecutivo reproducible. No reemplaza al dashboard Streamlit; lo complementa.

## Orden sugerido para presentar

1. Resumen ejecutivo.
2. Explicación de fuentes F01-F05 y qué NO mide cada una.
3. Oferta gastronómica registrada F01.
4. Dinamismo formal F02.
5. Espacios F03.
6. Eventos y programas F04/F05.
7. Qué puede responder hoy.
8. Qué todavía no puede responder.
9. Roadmap.

## Mensaje clave

DataGastro no intenta inventar un número único del sector gastronómico. Separa fuentes porque cada una mide una dimensión distinta:

- oferta registrada;
- habilitaciones aprobadas;
- espacios feriales/mercados/FIAB;
- eventos;
- programas y políticas.

Esa separación es una fortaleza metodológica.

## Recomendación de uso

En una demo interna:

1. Empezar con la notebook para contar el relato.
2. Después abrir el dashboard para exploración interactiva.
3. Cerrar con próximos pasos: geocodificación USIG, permisos de área gastronómica F06 y export ejecutivo.
4. Usar `docs/CHECKLIST_DEMO_DATAGASTRO.md` para validar comandos, KPIs y frases que no deben afirmarse.

## Advertencias que deben decirse explícitamente

- F02 no son locales activos.
- F03 no cuenta puestos/personas como ferias o mercados.
- F04/F05 son relevamientos manuales trazables, no datasets oficiales completos.
- No hay medición de impacto, empleo, ventas ni cierres.
- No se deben sumar F01 + F02.
