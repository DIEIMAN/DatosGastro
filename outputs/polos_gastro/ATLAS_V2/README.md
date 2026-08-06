# Atlas DGDGAS - dos ediciones

Un mismo corpus cerrado R01-R22, dos documentos con destinatarios distintos. Ninguna
cifra, geometria ni decision territorial cambia entre uno y otro.

## Edicion de conduccion (entregable de esta fase)

- PDF: ATLAS_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf
- Extension: 51 paginas A4 vertical.
- Destinatario: equipo del Ministro. Quien abre el documento sin conocer el proyecto
  tiene que entenderlo sin preguntarle nada a nadie.
- Se deriva de la V2.1 restando: se simplifica como se dice, no que se dice. Cada
  salvedad sigue estando, en castellano, una sola vez, en el lugar donde importa.
- QA: 31 controles, incluidos los dos propios de esta edicion -
  `vocabulario_conduccion` (ningun termino de metodo llega al lector) y
  `diff_cifras_v21_conduccion` (ningun numero se movio respecto de la V2.1).
- Verificacion frase por frase: `qa/TRAZABILIDAD_LENGUAJE.csv`.

## Edicion tecnica

- PDF: ATLAS_TECNICO_REFERENCIAS_GASTRONOMICAS_CABA_DGDGAS.pdf
- Extension: 58 paginas A4 vertical.
- Es la V2.1 tal cual, renombrada: no se le quito nada ni se reescribio nada. La portada
  la declara como edicion tecnica y el Anexo G remite a la edicion de conduccion.
- Es el respaldo metodologico completo y el destino de todo lo que salio de la otra.
- QA: los 28 controles de la V2.1.

## Ediciones anteriores

La V2 y la V2.1 auditadas permanecen en esta carpeta, sin modificar, junto con sus
paquetes de revision.

## Reproducibilidad

Ejecutar desde la raiz del repositorio, sin red:

    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_geometrias_editoriales_v2.py
    .venv/Scripts/python.exe -B outputs/polos_gastro/ATLAS_V2/scripts/build_atlas_v2.py --finalize-visual

El generador verifica hashes de los insumos congelados, trabaja sin red, rechaza
referencias distintas de R01-R22, rechaza un total de paginas distinto del declarado por
cada edicion y no modifica ningun activo fuente.
