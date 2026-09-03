# Skill 06 — Fuentes externas y privadas

Regla central: **separar recolección, evidencia e integración.** Se permite relevar información
comercial públicamente visible mediante navegador o extracción automatizada cuando haya
autorización explícita, alcance acotado, trazabilidad, ritmo prudente y salida interna. No
ejecutar llamadas pagas sin autorización. No guardar credenciales, cookies ni tokens.

El detalle accionable (matriz priorizada, plantillas, roadmap) vive en `docs/fuentes_externas/`
y `config/fuentes_externas/`. Esta skill fija las **reglas de uso por plataforma**.

## 1. Tabla de reglas por fuente

| Fuente | Acceso permitido | Acción permitida hoy | Prohibido |
| --- | --- | --- | --- |
| **Google Maps / Places Aggregate** | Web pública visible / API oficial paga | Relevamiento controlado interno o piloto API autorizado | Eludir controles; afirmar vigencia solo por la plataforma; API paga sin presupuesto |
| **Google Business Profile** | API con consentimiento del dueño | Diseñar piloto opt-in | Acceder a perfiles sin permiso |
| **Google Popular Times** | Sin API oficial estable | Muestra controlada como señal contextual | Publicarlo como medición representativa o actividad real |
| **OpenStreetMap / Overpass** | Abierto (ODbL) | **Script exploratorio permitido** con atribución y límites de uso | Abusar de servidores públicos |
| **Rappi** | Web/app visible; convenio para escala | Relevamiento acotado de oferta publicada; preparar convenio | Capturar usuarios/repartidores; confundir disponibilidad con universo total |
| **PedidosYa / Delivery Hero** | Web/app visible; convenio para escala | Relevamiento acotado de oferta publicada; preparar convenio | Capturar usuarios/repartidores; confundir disponibilidad con universo total |
| **Mercado Pago / adquirentes / bancos** | Convenio (datos agregados) | Documentar pedido agregado con umbrales | Datos nominales, CUIT visible, scraping |
| **Mercado Libre** | API marketplace | Solo si surge línea de costos/insumos | Mezclar con universo de locales; scraping |
| **POS (Fudo, Maxirest, etc.)** | Convenio / opt-in | Diseñar piloto voluntario agregado | Facturación individual pública |
| **Reservas (TheFork, OpenTable, Meitre...)** | Web visible; convenio / opt-in | Señales de presencia/disponibilidad y pedido de reunión | Afirmar ocupación real desde una consulta aislada |
| **TripAdvisor / Terra** | Web visible; API/comercial | Presencia turística y muestra de reseñas con fecha | Reproducir textos extensos o tratar ratings como censo |
| **Instagram / Meta** | Contenido público; API restringida / opt-in | Señales fechadas de actividad y campañas | Perfiles privados, mensajes, datos personales o inferencias sobre personas |
| **TikTok Research API** | API con elegibilidad | Tendencias por keywords oficiales | Usarlo como padrón de locales |
| **Google Trends** | Interfaz pública | Indicador de demanda en informes | Scraping automático masivo |
| **Operadoras móviles / Waze / SUBE** | Convenio | Consultar si ya hay convenio GCBA | Pedir datos granulares de individuos |

## 2. Qué pedir a una plataforma privada (mínimos agregados)

Tabla **mensual, agregada por comuna/barrio y categoría**, nunca datos personales:

- mes; comuna/barrio; rubro/categoría gastronómica;
- cantidad de comercios activos en la plataforma;
- cantidad agregada de pedidos/transacciones;
- monto agregado o índice base 100; ticket promedio agregado;
- franjas horarias de mayor actividad; altas/bajas;
- plataforma/fuente; aclaración metodológica.

**Umbral mínimo de comercios por celda** para evitar reidentificación. No pedir usuarios,
tarjetas, repartidores, domicilios ni CUIT nominal salvo base legal clara (ver skill 03).

## 3. Orden estratégico recomendado

1. Primero cerrar lo **público/interno crítico**: padrón vivo AGC, permisos de área gastronómica,
   eventos oficiales operativos. (Evita decir "44 mil locales activos".)
2. Piloto externo rápido y barato: **OSM** abierto + **Google Places** controlado, en 2 comunas
   (San Nicolás y Palermo).
3. En paralelo, abrir **convenios** de delivery/pagos para demanda real.

## 4. Antes de tocar cualquier fuente externa

Responder el `checklist_legal_y_metodologico.md` (acceso, privacidad, universo, calidad,
integración). La extracción puede alimentar una carpeta de evidencia interna; para entrar al
pipeline institucional necesita contrato de fuente, condiciones de uso compatibles, controles,
corroboración y aprobación explícita.

## 5. Credenciales y costos

- **No guardar credenciales** en el repo ni en outputs. Usar variables de entorno fuera del repo.
- **No ejecutar llamadas pagas** sin que Diego autorice proyecto y presupuesto.
- Los scripts de fuentes externas que requieren API deben quedar en modo **"plan/dry-run"** hasta
  tener autorización (ver `scripts/external_sources/`).
