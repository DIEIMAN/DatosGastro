# Comparación Fase 25 vs. pipeline nuevo

## Síntesis

Fase 25 y el pipeline nuevo responden preguntas distintas. Fase 25 organiza una semilla de 22 polos/ejes con geometrías prudentes y cinco mapas de detalle. El pipeline nuevo estudia 13 macrozonas con 6.461 puntos y detecta subestructura cuantitativa. El segundo mejora evidencia y legibilidad, pero introduce falsa precisión cuando convierte concentración en polígonos.

## Qué mejoró

1. **Datos:** de 106 referencias geolocalizadas usadas para la construcción inicial de contenedores a 3.240 puntos F01/F02 dentro de macrozonas y 3.221 señales Places nuevas.
2. **Método:** HDBSCAN separa densidades variables y ruido. Fase 25 no tenía detector cuantitativo equivalente.
3. **Cartografía:** v4.2 tiene jerarquía visual más clara, capas de QA y familias explícitas.
4. **Trazabilidad:** cada punto final tiene fuente y asignación única; 163 -> 41 retenidos -> 31 está reconstruido.

## Qué empeoró o quedó abierto

1. KMeans crea 91 polígonos sin fundamento territorial.
2. La contención por macrozona impide descubrimiento fuera del marco previo.
3. Las 31 unidades conservan 16 pares solapados en v4; v4.1 corrige sólo la visualización.
4. Seis zonas dependen en más de 60 % de Places.
5. El nombre y la jerarquía de cada unidad siguen siendo decisiones editoriales.

## Lectura por zona

- **Palermo:** Fase 25 acierta al separar Soho/Hollywood/Las Cañitas como lectura editorial. El pipeline aporta densidad, pero Soho es sensible a parámetros y Hollywood debe mostrarse como red de núcleos, no como un único polígono.
- **San Telmo:** Fase 25 es prudente al usar Mercado/Defensa/casco histórico. El pipeline confirma concentración, pero la partición cambia con parámetros. Conviene un núcleo orientativo y ejes, no ocho microáreas.
- **Corrientes:** Fase 25 representa correctamente un eje. El pipeline aporta evidencia para distinguir tramos, pero 23 tiles KMeans son peores que el corredor editorial.
- **Microcentro:** el pipeline aporta subestructura ausente en Fase 25. Debe mostrarse como núcleos/peatonales, con decisión humana sobre la separación respecto de Corrientes.
- **Belgrano:** Fase 25 conserva la mejor jerarquía conceptual —macroárea con subzonas—. El pipeline agrega evidencia, pero es inestable y muy sensible a epsilon.
- **Caballito:** el pipeline descubre volumen y posibles núcleos, pero 60,4 % Places y 33 divisiones KMeans no permiten reemplazar aún la lectura genérica de Fase 25.
- **Recoleta:** el pipeline aporta intensidad, pero la forma es difusa y sensible a epsilon. Heatmap o núcleos separados son más honestos.
- **Villa Crespo y Chacarita:** evidencia nueva relevante, alta dependencia Places y baja estabilidad. No deberían pasar al mapa principal sin pruebas adicionales.
- **Puerto Madero:** Fase 25 representa mejor la morfología como banda de docks/frente costero. El pipeline es estable pero 71,1 % Places; usar eje/frente, no manchas.
- **Costanera Norte:** Fase 25 usa un eje aproximado. El pipeline depende 93,1 % de Places. Mantener sólo como señal exploratoria/puntos.
- **Caseros/Barracas:** Fase 25 usa corredor aproximado; la nueva evidencia es mayor pero 69,0 % Places. Corredor en anexo, no polígono firme.

## Recomendación para un informe político/institucional

Conservar la prudencia territorial de Fase 25 y actualizarla con evidencia cuantitativa del pipeline nuevo. No sustituir todas las geometrías por v4.2. Usar método híbrido: polígonos sólo para núcleos compactos; ejes/buffers para corredores y frentes; núcleos separados para redes; heatmap/puntos para señales débiles.

La tabla completa está en `comparacion_por_zona_fase25_nuevo.csv`.

