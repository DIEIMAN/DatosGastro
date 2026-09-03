# Política de fuentes para los wrappers

## Permitido

- Sitios y plataformas con contenido comercial públicamente visible y autorización explícita
  del usuario para la tarea.
- Portales oficiales y datasets abiertos.
- OpenStreetMap/Overpass con atribución ODbL, consultas acotadas y caché local.
- Archivos locales autorizados, con salidas internas y sin datos personales.
- APIs oficiales solo cuando exista autorización y presupuesto; por defecto, dry-run.

## Condiciones estrictas

- Google Maps, Rappi, PedidosYa, Mercado Libre, TripAdvisor, TheFork y redes se tratan como
  fuentes externas de señal, nunca como padrón ni prueba única de vigencia.
- No eludir login, CAPTCHA, paywall, robots ni controles de acceso.
- No reutilizar perfiles, contraseñas o cookies. Una sesión ya iniciada por el usuario solo puede
  usarse con autorización puntual, lectura acotada y sin extraer credenciales.
- No recolectar perfiles privados, mensajes, usuarios, consumidores, repartidores ni datos
  personales; no automatizar compras, reservas, publicaciones o formularios.
- Declarar URL, fecha/hora, campos, cantidad consultada, herramienta y limitaciones. Aplicar
  pausas, caché y topes predefinidos.
- Escritura en Drive, fuentes crudas, superficies protegidas o pipeline F01–F05.

La recolección queda como `EVIDENCIA_EXTERNA_NO_CANONICA`. Para entrar al pipeline requiere
contrato, compatibilidad de uso, controles, corroboración y aprobación explícita. Nunca mezclar
universos F/I/E como un total único.
