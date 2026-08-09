# -*- coding: utf-8 -*-
"""Ensambla el Atlas V3 en un solo documento, enruta las fichas segun el criterio
y coloca la cartografia. Salida: ATLAS_V3_DOCUMENTO.md"""
import io, os, re, csv, datetime
EV='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08/desde_cowork/evidencia_2026'
DC='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08/desde_cowork'
H='/home/claude'; O='/home/claude/out'
def rd(p): return io.open(p,encoding='utf-8').read()
def lineas(p,a,b=None):
    L=rd(p).split('\n'); return '\n'.join(L[a-1:(b if b else len(L))]).strip('\n')

A=f'{EV}/ATLAS_V3_SECCIONES_II_V_VI_IX.md'; B=f'{DC}/ATLAS_V3_SECCIONES_I_IV_VII.md'
S={}
S['I']  = rd(f'{H}/SECCION_I_PRESENTACION.md')
S['II'] = lineas(A,36,248)
S['III']= lineas(B,179,285)
S['IV'] = lineas(B,286,382)
S['V']  = lineas(A,249,387)
S['VI'] = lineas(A,388,465)
S['VIII']=rd(f'{O}/SECCION_VIII_LO_QUE_NO_ENTRO.md')
S['IX'] = lineas(A,466)
ANEXO_A = rd(f'{O}/CRITERIO_DE_ADMISION_Y_PERMANENCIA.md')
ANEXO_B = rd(f'{H}/ANEXO_B_LAS_124_CONCENTRACIONES.md')
ANEXO_C = rd(f'{H}/ANEXO_C_CORRESPONDENCIA_GLOSARIO_FUENTES.md')

# ---------- VII: partir en bloques y enrutar ----------
def bloques(txt):
    out=[]; cur=None; buf=[]
    for ln in txt.split('\n'):
        m=re.match(r'^# (?!#)(.*)$', ln)
        if m:
            if cur is not None: out.append((cur,'\n'.join(buf).strip('\n')))
            cur=m.group(1).strip(); buf=[]
        else:
            if cur is None: continue
            buf.append(ln)
    if cur is not None: out.append((cur,'\n'.join(buf).strip('\n')))
    return out

refs_txt = rd(f'{H}/SECCION_VII_REFERENCIAS_PUBLICADAS.md')
zon_txt  = rd(f'{H}/SECCION_VII_ZONAS_INCORPORADAS.md')
COMO_LEER = lineas(f'{H}/SECCION_VII_REFERENCIAS_PUBLICADAS.md',20,63)

FUERA_ZONAS = {'San Cristóbal','Flores · casco histórico','Floresta','Coghlan'}
FUERA_REFS  = {'R22 · Villa Pueyrredón'}

def recolectar(txt, fuera):
    dentro=[]; sacados=[]; comuna=None
    for tit,cuerpo in bloques(txt):
        if tit.startswith('Comuna '): comuna=tit; continue
        if tit.startswith('Lo que sale de escribir'): continue
        if tit.startswith('Sección VII'): continue
        if tit in fuera: sacados.append((tit,cuerpo,comuna)); continue
        dentro.append((comuna,tit,cuerpo))
    return dentro, sacados

d1,s1 = recolectar(refs_txt, FUERA_REFS)
d2,s2 = recolectar(zon_txt, FUERA_ZONAS)

# fichas nuevas del sur, todas Comuna 4
nuevas=[('Comuna 4',t,c) for t,c in bloques(rd(f'{O}/FICHAS_SUR_NUEVAS.md'))]
fichas = d1 + d2 + nuevas
def numcom(s):
    m=re.search(r'\d+', s or ''); return int(m.group()) if m else 99
por_comuna={}
for com,tit,cue in fichas: por_comuna.setdefault(numcom(com),[]).append((tit,cue))

MAPAS='cartografia'
vii=['# VII · La Ciudad, comuna por comuna','', COMO_LEER, '',
     '> **Cada comuna abre con su mapa.** El relleno sólido marca los polos con perímetro propio; '
     'el rayado, los que todavía no lo tienen y se representan con el barrio que los contiene. '
     '**Las áreas rayadas no se pueden usar para medir superficie ni comparar tamaños.**','']
for c in sorted(por_comuna):
    vii.append(f'\n---\n\n## Comuna {c}\n')
    m=f'{MAPAS}/comuna_{c:02d}.png'
    if os.path.exists(f'{O}/mapas/comuna_{c:02d}.png'):
        vii.append(f'![Mapa de la Comuna {c}]({m})\n')
    for tit,cue in por_comuna[c]:
        vii.append(f'### {tit}\n'); vii.append(cue); vii.append('')
S['VII']='\n'.join(vii)

# los sacados van a la VIII como fichas completas
extra=['\n---\n---\n\n## 4 · Las fichas completas de las cinco que salieron\n',
       'Estas cinco tenían ficha escrita en la sección VII de la edición anterior de este documento. '
       '**El criterio las movió de categoría y las fichas se mudan acá enteras, sin recortar**, '
       'porque lo que documentan sigue siendo cierto: lo que cambió es dónde entran.\n']
for tit,cue,com in s1+s2:
    extra.append(f'\n### {tit}\n'); extra.append(cue); extra.append('')
S['VIII']=S['VIII']+'\n'+'\n'.join(extra)

# ---------- normalizar niveles ----------
def demote(t, n=1):
    return re.sub(r'^(#{1,5}) ', lambda m:'#'*(len(m.group(1))+n)+' ', t, flags=re.M)
for k in ['I','II','III','IV','V','VI','VIII','IX']:
    S[k]=re.sub(r'^# ', '# ', S[k], flags=re.M)

TIT={'I':'I · Presentación','II':'II · Qué es un polo gastronómico','III':'III · De dónde salen los datos',
     'IV':'IV · Cómo se leyó el territorio','V':'V · Los referentes de la Ciudad',
     'VI':'VI · Las comunidades y el territorio','VII':'VII · La Ciudad, comuna por comuna',
     'VIII':'VIII · Lo que se midió y no entró','IX':'IX · Qué no dice este atlas'}
def normalizar(k,txt):
    if k=='VII':
        return txt
    L=txt.split('\n'); out=[]; primera=True
    for ln in L:
        if re.match(r'^# (?!#)', ln):
            if primera: out.append(f'# {TIT[k]}'); primera=False; continue
            out.append('#'+ln)   # demote
        elif re.match(r'^#{2,5} ', ln): out.append('#'+ln)
        else: out.append(ln)
    if primera: out.insert(0, f'# {TIT[k]}\n')
    return '\n'.join(out)

hoy=datetime.date(2026,8,10).strftime('%d de agosto de %Y')
tapa=f"""# Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires

## Versión 3 · agosto de 2026

**Dirección General de Desarrollo Gastronómico**
Ministerio de Desarrollo Económico · Gobierno de la Ciudad de Buenos Aires

---

> **Documento en edición.** El relevamiento está cerrado y el texto está escrito. Lo que está en
> curso es la edición: el trazado de los perímetros que faltan y el armado final. **Cada cifra de
> este documento lleva su fuente y su fecha, y cada cosa que falta está declarada donde falta.**

---

|  |  |
|---|---|
| **23.981** | locales gastronómicos relevados en toda la Ciudad |
| **41** | polos admitidos, en catorce de las quince comunas |
| **55** | zonas evaluadas con el mismo criterio |
| **12.688** | locales en los polos · el 53 % de la gastronomía relevada en el 15 % de la superficie |
| **90 de 90** | bares notables verificados uno por uno, con fecha y fuente |
| **15** | enclaves comunitarios delimitados con calles y alturas |

---

![Los polos gastronómicos admitidos]({MAPAS}/mapa_general.png)

---

## Índice

| | |
|---|---|
| **I** | Presentación |
| **II** | Qué es un polo gastronómico, y con qué criterio entra |
| **III** | De dónde salen los datos |
| **IV** | Cómo se leyó el territorio |
| **V** | Los referentes de la Ciudad |
| **VI** | Las comunidades y el territorio |
| **VII** | **La Ciudad, comuna por comuna** — los 41 polos |
| **VIII** | Lo que se midió y no entró |
| **IX** | Qué no dice este atlas |
| **Anexo A** | El criterio de admisión y permanencia, completo |
| **Anexo B** | Las 124 concentraciones detectadas |
| **Anexo C** | Correspondencia, glosario, fuentes y licencias |

---
"""
partes=[tapa]
for k in ['I','II','III','IV','V','VI','VII','VIII','IX']:
    partes.append('\n\n---\n\n'+normalizar(k,S[k]))
for t,txt in [('Anexo A · El criterio de admisión y permanencia',ANEXO_A),
              ('Anexo B · Las 124 concentraciones detectadas',ANEXO_B),
              ('Anexo C · Correspondencia, glosario, fuentes y licencias',ANEXO_C)]:
    body=re.sub(r'^# .*$','',txt,count=1,flags=re.M).strip('\n')
    body=re.sub(r'^(#{1,5}) ', lambda m:'#'*(len(m.group(1))+1)+' ', body, flags=re.M)
    partes.append(f'\n\n---\n\n# {t}\n\n'+body.strip('\n'))
doc='\n'.join(partes)
io.open(f'{O}/ATLAS_V3_DOCUMENTO.md','w',encoding='utf-8').write(doc)
print('fichas en VII:',sum(len(v) for v in por_comuna.values()),'| comunas:',len(por_comuna))
print('fichas movidas a VIII:',len(s1)+len(s2), [t for t,_,_ in s1+s2])
print('palabras:',len(doc.split()),'| caracteres:',len(doc))
