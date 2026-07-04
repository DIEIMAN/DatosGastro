# Checklist sync Claude Design - DGDGAS Informes v1

Usar esta checklist solo cuando exista autorizacion explicita para trabajar con el proyecto remoto en `claude.ai/design` o con `design-sync`.

## Identificacion del proyecto remoto

- [ ] Proyecto remoto existe.
- [ ] Nombre correcto confirmado: `DGDGAS Informes` o `DGDGAS Informes - v1`.
- [ ] Version remota identificada.
- [ ] Fuente de verdad acordada: repo local, Claude Design remoto o sincronizacion bidireccional controlada.

## Tokens

- [ ] Tokens importados.
- [ ] `meta.system` y version coinciden.
- [ ] Marca publica coincide: DGDGAS - Direccion General de Gastronomia.
- [ ] No se usa DataGastro como marca publica por defecto.
- [ ] Paleta `brand.*` coincide.
- [ ] Paleta `text.*` coincide.
- [ ] Paleta `surface.*` coincide.
- [ ] Paleta `border.*` coincide.
- [ ] Paleta `status.*` coincide.
- [ ] Secuencia `chart.sequence` coincide.
- [ ] Tipografias coinciden.
- [ ] Escala tipografica coincide.
- [ ] Layout A4, margenes y espaciado coinciden.
- [ ] Radios coinciden.
- [ ] Tokens de tabla coinciden.
- [ ] Tokens de cajas coinciden.
- [ ] Tokens de mapa coinciden.
- [ ] Footer coincide.
- [ ] Estados de contenido coinciden.

## Componentes

- [ ] Componentes importados.
- [ ] Portada institucional coincide.
- [ ] Indice coincide.
- [ ] Ficha de relevamiento coincide.
- [ ] Caja "Pregunta analizada" coincide.
- [ ] Caja "Lectura de resultados" coincide.
- [ ] Nota metodologica breve coincide.
- [ ] Caja "Alcance / advertencia" coincide.
- [ ] Caja "Requiere validacion" coincide.
- [ ] Tabla institucional coincide.
- [ ] Tabla de polos coincide.
- [ ] Ficha de polo coincide.
- [ ] Pagina con mapa territorial coincide.
- [ ] Pagina con grafico coincide.
- [ ] Pagina de sintesis coincide.
- [ ] Pagina de aspectos a considerar coincide.
- [ ] Pagina de anexo coincide.
- [ ] Estado de documentacion coincide.

## Plantillas

- [ ] Plantillas importadas.
- [ ] P0 Portada coincide.
- [ ] P1 Indice coincide.
- [ ] P2 Datos generales coincide.
- [ ] P3 Preguntas / variables coincide.
- [ ] P4 Resultado con grafico coincide.
- [ ] P5 Resultado con mapa coincide.
- [ ] P6 Ficha de polo coincide.
- [ ] P7 Tabla comparativa / de polos coincide.
- [ ] P8 Sintesis coincide.
- [ ] P9 Aspectos a considerar coincide.
- [ ] P10 Anexo coincide.
- [ ] Template YAML de contenido coincide con la estructura aprobada.
- [ ] Payload Google Docs coincide con los bloques aprobados.

## Diferencias y decisiones

- [ ] Diferencias detectadas documentadas.
- [ ] Diferencias clasificadas: token, componente, plantilla, texto, QA o implementacion.
- [ ] Cambios a aplicar en repo definidos.
- [ ] Cambios que dependen de Claude Design definidos.
- [ ] Cambios que dependen de Python/backend definidos.
- [ ] Cambios que requieren instalar dependencias identificados.
- [ ] Cambios no aceptados documentados.

## Guardrails antes de aplicar cambios en repo

- [ ] No tocar informes finales.
- [ ] No tocar Cafecito.
- [ ] No tocar PolosGastro.
- [ ] No tocar MercadosGastro.
- [ ] No tocar CasasDePastas.
- [ ] No modificar PDFs finales.
- [ ] No tocar datos fuente.
- [ ] No instalar dependencias sin autorizacion explicita.
- [ ] No commit.
- [ ] No push.
- [ ] No staging.
- [ ] No usar `git add .`.

## Cierre

- [ ] Archivos modificados listados.
- [ ] Cambios aplicados solo en `docs/datagastro_design_system/` o `scripts/shared/reporting_dgdgas/`, si correspondia.
- [ ] QA de privacidad y no fuga tecnica revisado.
- [ ] `git diff --cached --name-only` verificado vacio.
- [ ] Estado final reportado antes de cualquier fase de aplicacion a informes.
