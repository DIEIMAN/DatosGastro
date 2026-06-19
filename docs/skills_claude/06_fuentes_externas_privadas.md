# Skill 06 — Fuentes externas y privadas

Regla central: **no scraping.** Solo **APIs oficiales, convenios, datos agregados o planes de
consulta/documentación**. No ejecutar llamadas pagas sin autorización. No guardar credenciales.

El detalle accionable (matriz priorizada, plantillas, roadmap) vive en `docs/fuentes_externas/`
y `config/fuentes_externas/`. Esta skill fija las **reglas de uso por plataforma**.

## 1. Tabla de reglas por fuente

| Fuente | Acceso permitido | Acción permitida hoy | Prohibido |
| --- | --- | --- | --- |
| **Google Places / Places Aggregate** | API oficial paga | Solo **plan** y diseño de piloto; revisar TOS | Llamar la API sin autorización presupuestaria; scraping de Google Maps |
| **Google Business Profile** | API con consentimiento del dueño | Diseñar piloto opt-in | Acceder a perfiles sin permiso |
| **Google Popular Times** | Sin API oficial estable | Mencionar como deseable | Scraping / librerías no oficiales |
| **OpenStreetMap / Overpass** | Abierto (ODbL) | **Script exploratorio permitido** con atribución y límites de uso | Abusar de servidores públicos |
| **Rappi** | Solo convenio | Preparar pedido de convenio / one-pager | Scraping de app/web |
| **PedidosYa / Delivery Hero** | Solo convenio | Preparar pedido de convenio | Scraping |
| **Mercado Pago / adquirentes / bancos** | Convenio (datos agregados) | Documentar pedido agregado con umbrales | Datos nominales, CUIT visible, scraping |
| **Mercado Libre** | API marketplace | Solo si surge línea de costos/insumos | Mezclar con universo de locales; scraping |
| **POS (Fudo, Maxirest, etc.)** | Convenio / opt-in | Diseñar piloto voluntario agregado | Facturación individual pública |
| **Reservas (TheFork, OpenTable, Meitre...)** | Convenio / opt-in | Identificar plataformas y pedir reunión | Scraping |
| **TripAdvisor / Terra** | API/comercial | Pedir demo si se mide turismo | Scraping de reviews |
| **Instagram / Meta** | API restringida / opt-in | Campañas y hashtags oficiales | Scraping de perfiles |
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
integración). Si la fuente requiere scraping de plataforma privada o trae datos sensibles sin
convenio: **no entra al pipeline institucional.**

## 5. Credenciales y costos

- **No guardar credenciales** en el repo ni en outputs. Usar variables de entorno fuera del repo.
- **No ejecutar llamadas pagas** sin que Diego autorice proyecto y presupuesto.
- Los scripts de fuentes externas que requieren API deben quedar en modo **"plan/dry-run"** hasta
  tener autorización (ver `scripts/external_sources/`).
