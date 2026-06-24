# Mercados gastronómicos CABA — Prompt para Perplexity (localizador de fuentes)

> Perplexity (o búsqueda asistida) se usa **solo para localizar fuentes**, no como fuente final.
> Toda afirmación debe quedar respaldada por una URL verificable (título, medio, fecha). Sin URL
> comprobable, **no entra** al relevamiento. **No ejecutado en esta etapa.**

## Regla de uso

1. El resultado es una **lista de fuentes**, no un dato definitivo.
2. Se verifica cada URL antes de usarla.
3. Priorizar oficiales; descartar blogs sin fuente.
4. No copiar datos personales (teléfonos, mails, referentes).
5. El pedido es **exclusivamente** sobre mercados gastronómicos / espacios tipo mercado con eje
   gastronómico.

## Prompt sugerido

```text
Actuá como asistente de investigación documental. Necesito localizar FUENTES (no opiniones)
sobre los MERCADOS GASTRONÓMICOS de la Ciudad Autónoma de Buenos Aires (CABA), Argentina.

Alcance: espacios donde la gastronomía, los alimentos, las bebidas o la experiencia
gastronómica son el EJE PRINCIPAL. Incluí:
1. Mercados gastronómicos públicos, privados o mixtos.
2. Food halls / patios gastronómicos curados.
3. Mercados de productores y mercados de alimentos.
4. Ferias gastronómicas relevantes (permanentes o periódicas).
5. Mercados barriales o históricos con oferta alimentaria/gastronómica significativa.
6. Mercados con perfil turístico ligado a su oferta gastronómica.

NO incluir mercados de pulgas, antigüedades, ropa, artesanías, diseño, shoppings ni galerías
comerciales, salvo que tengan una oferta gastronómica central y reconocible. Tampoco
supermercados comunes, mayoristas sin experiencia gastronómica, restaurantes individuales fuera
de un mercado, ni ferias generales sin foco alimentario claro.

Para cada mercado gastronómico, si está disponible en la fuente, indicá:
- nombre del mercado
- tipo (gastronómico público / privado / mixto / food hall / de productores / feria
  gastronómica / barrial alimentario / turístico gastronómico)
- barrio y, si figura, comuna
- dirección o zona
- horarios y días de apertura
- oferta gastronómica (comida/bebida) y oferta alimentaria (productos)
- público objetivo (barrial / turístico)
- relación con políticas, eventos o circuitos gastronómicos, si consta

Requisitos de fuentes (estrictos):
- Priorizá: sitios oficiales del Gobierno de la Ciudad (buenosaires.gob.ar), Buenos Aires Data
  (BA Data), Ente de Turismo / Turismo BA, BA Capital Gastronómica, sitios oficiales de cada
  mercado, y prensa con autoría y fecha.
- NO uses blogs ni agregadores sin fuente original citada.
- Para cada dato, citá la fuente con TÍTULO, MEDIO y URL, y la fecha de publicación si consta.

Formato de salida: una tabla con columnas:
nombre | tipo | barrio | comuna | direccion_o_zona | horarios | oferta_gastronomica | publico | fuente | url | fecha

Si un dato no está en una fuente confiable, dejalo como "pendiente". Si un espacio no tiene eje
gastronómico claro, marcalo como "fuera de alcance". No inventes datos ni URLs.
```

## Después de Perplexity

- Volcar las URLs a una tabla documental interna (`outputs/mercados_caba/internal/`).
- Verificar cada fuente; las verificadas alimentan las fichas con su nivel de confianza.
- Descartar o marcar `fuera_de_alcance_no_gastronomico` los espacios sin eje gastronómico.
- Nunca citar Perplexity como fuente; citar la fuente original.
