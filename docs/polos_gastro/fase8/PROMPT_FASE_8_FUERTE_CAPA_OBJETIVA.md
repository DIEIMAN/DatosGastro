# Prompt futuro - Fase 8 fuerte / capa objetiva

No ejecutar este prompt ahora. Es un borrador para una fase posterior.

## Contexto

Estamos trabajando en `C:\proyectos\Gastronomia\DataGastro`, proyecto PolosGastro.

Fase 7 dejo un Borrador 2 interno. Fase 8 liviana reviso evidencia documental de casos debiles y
pendientes. Ahora se busca una fase fuerte para construir o evaluar una capa objetiva de oferta
gastronomica por barrio, subzona o corredor, usando fuentes publicas abiertas y trazables.

## Reglas

- No usar Google Places.
- No usar Google Places API.
- No leer ni imprimir API keys.
- No usar plataformas privadas como dataset descargable.
- No tocar datos fuente originales.
- No modificar Borrador 2 como informe final.
- No generar PDF/DOCX.
- No generar mapas finales sin revision humana.
- No publicar resultados.
- No cambiar clasificaciones automaticamente.
- No mezclar registros administrativos con locales activos.
- No afirmar densidad real sin metodologia explicita.

## Objetivo

Buscar, inventariar y evaluar fuentes abiertas GCBA/AGC/BA Data/ENTUR relevantes para construir
una capa objetiva auxiliar sobre oferta gastronomica territorial.

La capa debe servir para contextualizar:

- areas nucleo;
- zonas relevantes;
- emergentes;
- anexos;
- casos en espera de evidencia;
- corredores puntuales como Paternal, Garcia del Rio, Caseros, Corrientes, Bajo Belgrano y otros.

## Fuentes a priorizar

- BA Data - Oferta y Establecimientos gastronomicos.
- AGC / habilitaciones aprobadas, si existe dataset abierto vigente y documentado.
- Ente de Turismo / oferta gastronomica.
- Fuentes oficiales GCBA de mercados, patios o programas gastronomicos.
- Boletin Oficial solo si aporta normativa o autorizaciones territoriales claras.

## Producto esperado

Crear derivados nuevos en una carpeta futura, por ejemplo:

- `docs/polos_gastro/fase8_fuerte/INVENTARIO_CAPA_OBJETIVA.md`
- `outputs/polos_gastro/fase8_fuerte/tablas/fuentes_capa_objetiva.csv`
- `outputs/polos_gastro/fase8_fuerte/tablas/diagnostico_cobertura_territorial.csv`
- `docs/polos_gastro/fase8_fuerte/NOTAS_METODOLOGICAS_CAPA_OBJETIVA.md`

## Criterios minimos

Para cada fuente:

- que mide;
- que NO mide;
- fecha de publicacion o actualizacion;
- cobertura territorial;
- granularidad;
- variables utiles;
- limitaciones;
- riesgo de uso;
- si permite o no aproximar densidad;
- si entra al pipeline o queda como insumo exploratorio;
- si contiene datos personales o sensibles;
- si requiere validacion humana.

## Casos de contraste prioritario

- Paternal.
- Parque Saavedra / Avenida Garcia del Rio.
- Federico Lacroze / Libertador a Cabildo.
- Avenida Corrientes.
- Avenida Boedo.
- Bajo Belgrano.
- Belgrano R.
- Villa Pueyrredon / Avenida San Martin.
- Avenida Caseros / Barracas.
- Abasto.
- Puerto Madero, con advertencia de estado documental medio.

## Salida esperada

La salida debe decir con claridad:

- que fuente sirve para contexto;
- que fuente sirve para medicion objetiva;
- que fuente no sirve para validar polos;
- que casos mejoran con evidencia objetiva;
- que casos siguen requiriendo validacion humana;
- que cambios de clasificacion se recomiendan, siempre con `aplicar_ahora_si_no = NO` salvo
  correccion obvia de bajo riesgo.

## Recordatorio de tono

Usar lenguaje prudente:

- "con la evidencia disponible";
- "requiere validacion adicional";
- "no constituye delimitacion oficial";
- "no permite afirmar densidad";
- "se recomienda revisar".
