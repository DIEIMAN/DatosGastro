# Handoff documental → Codex corrida expansión V4

**Fecha:** 2026-07-12  
**De:** investigador_documental_externo  
**Para:** Codex (corrida territorial futura)  
**No hacer ahora:** Places, clustering, geometrías, commits.

## 1. Estado documental por zona

Ver `DIAGNOSTICO_DOCUMENTAL_ZONAS_EXPANSION_V4.csv`.

## 2. Formas territoriales posibles (priors)

| Zona | Prior de forma | Alternativa nula |
|---|---|---|
| Crespo | multi-eje | un solo polígono barrial |
| Chacarita | corredor Newbery ± núcleo Dorrego | barrio completo / Lacroze |
| Caballito | multinodo | un polo |
| Caseros | corredor corto | Barracas / avenida larga |
| Centro | subunidades | unidad única |
| Abasto | núcleo + relación Corrientes | fusión con pizza centro |
| Boedo | eje débil | polo |
| Devoto | núcleo plaza | corredor largo |
| DoHo | corredor par de calles | barrio Urquiza |
| Urquiza | multieje | = DoHo |
| Nuevo Bajo | núcleo esquina | Retiro/Microcentro |
| Lacroze | tramos | avenida completa |
| García del Río | corredor lineal | parque = polo |
| Paternal | archipiélago | corredor continuo |
| Pueyrredón | indeterminada | corredor San Martín |

## 3. Evidencia usable post hoc (interpretar resultados)

- Denominaciones Turismo BA (Crespo, Chacarita; Caseros en itinerario; Goyena).
- Tramos de prensa verificados (Newbery, García del Río, Esmeralda-Paraguay 2020, Paternal 2024).
- **No** usar prensa para mover un polígono "hasta que se vea bien".

## 4. Nombres autorizados vs dudosos

- **Autorizados para análisis:** ver normalización `nombre_recomendado_para_analisis`.
- **Dudosos:** DoHo, Chacalermo, Nuevo Bajo, Polo Caseros, Microcentro-como-todo.

## 5. Objeciones a tener en pantalla

`MATRIZ_OBJECIONES_DOCUMENTALES_EXPANSION_V4.csv` — especialmente Crespo=Palermo, DoHo marca, Centro unitario, Paternal sin concentración, Lacroze sin continuidad.

## 6. Preguntas espaciales mínimas por tanda

1. ¿Número de clusters estables?  
2. ¿Morfología (corredor/núcleo/disperso)?  
3. ¿Solapamiento con vecinos?  
4. ¿Sensibilidad a radio/eps?

## 7. Decisiones que no deben forzarse

- Adopción de polo.
- Nombre público final.
- Fusión de zonas.
- Exclusión definitiva sin informe de vacío espacial (salvo vacíos documentales ya marcados INSUFICIENTE que solo merecen exploratorio).

## 8. Criterios para futuras recomendaciones

| Si el spatial… | Entonces documentalmente… |
|---|---|
| Confirma corredor en tramo documentado | Se puede **caracterizar** como corredor candidato |
| Encuentra multi-núcleo | Preferir lenguaje multinodo; no un solo polo |
| No encuentra estructura | Conservar como barrio con oferta / archipiélago / diferir |
| Funde con Palermo u otra zona adoptada | Reportar continuidad; no inventar independencia |

## 9. Orden sugerido de tandas (documental)

1. Crespo, Chacarita  
2. Caseros, Caballito nodos, DoHo+Urquiza, García del Río  
3. Subunidades Centro, Nuevo Bajo, Abasto  
4. Devoto, Paternal  
5. Boedo, Lacroze tramos, Pueyrredón  

## 10. Archivos de entrada

- `docs/polos_gastro/evidencia_documental_expansion_v4/`  
- `outputs/polos_gastro/evidencia_documental_expansion_v4/*.csv`  

## 11. Superficies que no tocar

Informe político V2.1, fase27/28, preflight en curso, V3/V3.1, evidencia V1.1, pipeline F01–F05, Places sin autorización.
