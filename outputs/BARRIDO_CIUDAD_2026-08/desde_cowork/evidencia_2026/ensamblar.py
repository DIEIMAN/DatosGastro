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

A=f'{H}/ATLAS_V3_SECCIONES_II_V_VI_IX.md'; B=f'{H}/ATLAS_V3_SECCIONES_I_IV_VII.md'

def seccion(path, romano):
    """Devuelve el bloque que empieza en '# <romano> ·' hasta el proximo H1."""
    L=io.open(path,encoding='utf-8').read().split('\n')
    ini=None
    for i,ln in enumerate(L):
        if re.match(r'^# '+romano+r' [·.]', ln):
            ini=i; break
        if ini is None and re.match(r'^# '+romano+r'\b', ln):
            ini=i; break
    if ini is None: raise SystemExit(f'no encontre la seccion {romano} en {path}')
    fin=len(L)
    for j in range(ini+1,len(L)):
        if re.match(r'^# (?!#)', L[j]): fin=j; break
    return '\n'.join(L[ini:fin]).strip('\n')
S={}
import re as _re
S['I']  = rd(f'{H}/SECCION_I_PRESENTACION.md')
# la nota interna de reescritura no va al documento publicado
S['I']  = _re.sub(r'\*Reescrita el 9 de agosto de 2026\..*?\*\n', '', S['I'], flags=_re.S, count=1)
S['I']  = _re.sub(r'\n## Nota de esta reescritura, para quien compare versiones.*$', '', S['I'], flags=_re.S)
S['II'] = seccion(A,'II')
S['III']= seccion(B,'III')
S['IV'] = seccion(B,'IV')
S['V']  = seccion(A,'V')
S['VI'] = seccion(A,'VI')
S['VIII']=rd(f'{O}/SECCION_VIII_LO_QUE_NO_ENTRO.md')
S['IX'] = seccion(A,'IX')
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
def _como_leer(path):
    """Todo lo que va debajo de '## Cómo leer estas páginas' hasta el proximo H1.
    Se busca por marca y no por numero de linea: antes se cortaba a mitad de una frase."""
    t=rd(path).split('## Cómo leer estas páginas',1)[1]
    return re.split(r'\n# (?!#)', t, 1)[0].strip('\n')
COMO_LEER = _como_leer(f'{H}/SECCION_VII_REFERENCIAS_PUBLICADAS.md')

FUERA_ZONAS = {'San Cristóbal','Flores · casco histórico','Floresta','Coghlan'}
FUERA_REFS  = {'Villa Pueyrredón'}

def limpio(t):
    """Saca el codigo interno del titulo de una ficha: 'R14 · Boedo' -> 'Boedo'."""
    return re.sub(r'^[RZ]\d{1,2}[a-z]?\s*·\s*', '', t).strip()

def recolectar(txt, fuera):
    dentro=[]; sacados=[]; comuna=None
    for tit,cuerpo in bloques(txt):
        if tit.startswith('Comuna '): comuna=tit; continue
        if tit.startswith('Lo que sale de escribir'): continue
        if tit.startswith('Sección VII'): continue
        tit=limpio(tit)
        if tit in fuera: sacados.append((tit,cuerpo,comuna)); continue
        dentro.append((comuna,tit,cuerpo))
    return dentro, sacados

d1,s1 = recolectar(refs_txt, FUERA_REFS)
d2,s2 = recolectar(zon_txt, FUERA_ZONAS)

# fichas nuevas del sur, todas Comuna 4
nuevas=[('Comuna 4',t,c) for t,c in bloques(rd(f'{O}/FICHAS_SUR_NUEVAS.md'))]
fichas = d1 + d2 + nuevas
# ---------- un mapa por polo ----------
import unicodedata
def _nk(x):
    x=unicodedata.normalize('NFD',x or '')
    x=''.join(c for c in x if unicodedata.category(c)!='Mn').lower()
    return re.sub(r'[^a-z0-9]+',' ',x).strip()
MAPA_POLO={}
try:
    for r in csv.DictReader(io.open(f'{O}/mapas_polos.csv',encoding='utf-8')):
        MAPA_POLO[_nk(r['nombre'])]=r['archivo']
except FileNotFoundError:
    pass
# las que no llevan su nombre exacto en la capa
ALIAS={'centro microcentro':'microcentro','av montes de oca':'barracas av montes de oca',
       'chacagiales':'chacarita colegiales federico lacroze'}
DESTACADOS={}
try:
    for r in csv.DictReader(io.open(f'{O}/destacados.csv',encoding='utf-8')):
        DESTACADOS[_nk(r['polo'])]=r['texto']
except FileNotFoundError:
    pass
EXTRA={}
try:
    for r in csv.DictReader(io.open(f'{O}/extras_paginas.csv',encoding='utf-8')):
        EXTRA.setdefault(_nk(r['polo']),{})[r['tipo']]=r['texto']
except FileNotFoundError:
    pass
def extra_de(t,k):
    kk=_nk(t)
    return (EXTRA.get(kk) or EXTRA.get(_nk(ALIAS.get(kk,kk))) or {}).get(k)

JUNTOS={}
try:
    for r in csv.DictReader(io.open(f'{O}/cuantos_y_juntos.csv',encoding='utf-8')):
        JUNTOS[_nk(r['polo'])]=r['texto']
except FileNotFoundError:
    pass
JALIAS={'centro microcentro':'centro y microcentro','microcentro':'centro y microcentro',
        'av montes de oca':'barracas av montes de oca',
        'flores avellaneda':'flores avellaneda y pasaje ruperto godoy',
        'la boca caminito':'la boca caminito y vuelta de rocha',
        'barrio coreano':'baek ku barrio coreano'}
def juntos_de(t):
    kk=_nk(t)
    for k in (kk, _nk(ALIAS.get(kk,kk)), _nk(JALIAS.get(kk,kk))):
        if k in JUNTOS: return JUNTOS[k]
    return None

FALTA={}
try:
    for r in csv.DictReader(io.open(f'{O}/bloques_faltantes.csv',encoding='utf-8')):
        FALTA.setdefault(_nk(r['polo']),{})[r['bloque']]=r['texto']
except FileNotFoundError:
    pass
def falta_de(t,b):
    kk=_nk(t)
    for k in (kk, _nk(ALIAS.get(kk,kk)), _nk(JALIAS.get(kk,kk))):
        if k in FALTA and b in FALTA[k]: return FALTA[k][b]
    return None

ANCLAS={}
try:
    for r in csv.DictReader(io.open(f'{O}/anclas_afuera.csv',encoding='utf-8')):
        ANCLAS[_nk(r['polo'])]=r['texto']
except FileNotFoundError:
    pass
def anclas_de(t):
    kk=_nk(t)
    for k in (kk, _nk(ALIAS.get(kk,kk)), _nk(JALIAS.get(kk,kk))):
        if k in ANCLAS: return ANCLAS[k]
    return None

def destacados_de(t):
    k=_nk(t); k=ALIAS.get(k,k)
    return DESTACADOS.get(_nk(k))

def mapa_de(t):
    k=_nk(t)
    k=ALIAS.get(k,k)
    return MAPA_POLO.get(_nk(k))

def numcom(s):
    m=re.search(r'\d+', s or ''); return int(m.group()) if m else 99
por_comuna={}
for com,tit,cue in fichas: por_comuna.setdefault(numcom(com),[]).append((tit,cue))

MAPAS='cartografia'
MAG = io.open(f'{O}/MAGNITUD_DE_LOS_18.md',encoding='utf-8').read()
MAG = MAG.split('## Lo que sí se puede medir sin inventar un perímetro',1)[1]
MAG = MAG.split('## Qué destraba esto',1)[0].strip()

# ---------- los veinte que ya estaban publicados ----------
PRIMEROS = ['Palermo','Avenida Corrientes','San Telmo','Puerto Madero','Belgrano','Recoleta',
            'Costanera Norte','Villa Crespo','Chacagiales','Caballito','Boulevard Caseros','Microcentro',
            'Centro / Microcentro','Abasto','Avenida Boedo','Devoto','Donado–Holmberg','Villa Urquiza',
            'García del Río','La Paternal']
PRIM = {_nk(x) for x in PRIMEROS}
def ya_estaba(t): return _nk(t) in PRIM

def ficha(tit, cue):
    """Arma una pagina completa: bloques faltantes, cifras, destacados, salvedad y mapa."""
    # la historia editorial ya la dice el titulo de la parte: se saca del subtitulo de cada pagina
    cue=re.sub(r'\s*—\s*(ya estaba en la versión anterior|nuevo en esta edición)\s*·\s*', ' — ', cue, count=1)
    cue=re.sub(r'\s*·\s*(ya estaba en la versión anterior|nuevo en esta edición)\b', '', cue, count=1)
    for b,antes in (('reconocimiento',('**Por qué es un polo.**','**Los establecimientos.**')),
                    ('perdido',('**Cómo le va al comercio alrededor.**',
                                '**Qué no se puede concluir de esta página.**','**Lo que falta.**'))):
        tx=falta_de(tit,b)
        if not tx: continue
        L=cue.split('\n'); corte=len(L)
        for k,ln in enumerate(L):
            if ln.startswith(antes): corte=k; break
        cue='\n'.join(L[:corte]).rstrip()+'\n\n'+tx+'\n\n'+'\n'.join(L[corte:])
    cj=juntos_de(tit)
    if cj:
        L=cue.split('\n'); corte=len(L)
        for k,ln in enumerate(L):
            if ln.startswith(('**Los establecimientos.**','**Para conocer.**','**Cómo le va al comercio alrededor.**')):
                corte=k; break
        cue='\n'.join(L[:corte]).rstrip()+'\n\n'+cj+'\n\n'+'\n'.join(L[corte:])
    de=destacados_de(tit) or extra_de(tit,'para_conocer')
    dato=extra_de(tit,'dato')
    if dato: de=(de+'\n\n'+dato) if de else dato
    if de:
        L=cue.split('\n'); corte=len(L)
        for k,ln in enumerate(L):
            if ln.startswith(('**Cómo le va al comercio alrededor.**','**Qué no se puede concluir de esta página.**','**Lo que falta.**')):
                corte=k; break
        cue='\n'.join(L[:corte]).rstrip()+'\n\n'+de+'\n\n'+'\n'.join(L[corte:])
    ca=anclas_de(tit)
    if ca:
        L=cue.split('\n'); corte=len(L)
        for k,ln in enumerate(L):
            if ln.startswith('**Lo que falta.**'): corte=k; break
        cue='\n'.join(L[:corte]).rstrip()+'\n\n'+ca+'\n\n'+'\n'.join(L[corte:])
    mp=mapa_de(tit)
    if mp and os.path.exists(f'{O}/mapas/polos/{mp}'):
        L=cue.split('\n'); k=0
        while k<len(L) and not L[k].strip(): k+=1
        if k<len(L): k+=1
        cue='\n'.join(L[:k])+f'\n\n![{tit}]({MAPAS}/polos/{mp})\n'+'\n'.join(L[k:])
    return f'### {tit}\n\n'+cue

APERTURA_1 = """Este atlas se construyó sobre una lista que la Dirección ya venía siguiendo: **veintidós polos
gastronómicos**, publicados en la edición anterior. Esta primera parte es esa lista, medida de nuevo
con el método que explica la sección II y dibujada con los bordes de esta edición.

**Veinte de los veintidós siguen siendo polos, y esos veinte se publican en diecinueve páginas.**
Tres cosas se movieron, y las tres dicen algo sobre cómo funciona la regla.

- **Esmeralda y Paraguay** dejó de ser un polo aparte y quedó adentro de Retiro. La medición mostró
  que el núcleo coreano y asiático que ese polo marcaba está sobre las mismas cuadras que Retiro
  documenta, y dos nombres para un solo lugar cuentan los locales dos veces.
- **Villa Pueyrredón** no llegó al mínimo de dos condiciones: cumple una sola y su continuidad es la
  más baja de todas las zonas medidas. Pasó a *lugar en observación*, y su página entera está en la
  sección VIII.
- **Chacarita y Federico Lacroze se publican ahora en una sola página**, junto con Colegiales, que
  esta edición sumaba por separado. Se llama **Chacagiales**, que es la palabra que usa la prensa, y
  la razón es medida: Chacarita tenía el 63,7 % de su superficie adentro de Federico Lacroze, y a
  ciento veinte metros la cadena de locales cercanos junta 732 y toca las tres. No eran tres polos
  vecinos: eran uno contado tres veces.

Ninguno de los veinte se achicó por la revisión. Tres se ampliaron con evidencia nueva, y la
verificación de que la ampliación contiene entero lo que ya estaba publicado dio cero superficie
perdida en los tres casos."""

APERTURA_2 = """La segunda parte son los **veinte polos que este relevamiento sumó**: zonas que la Ciudad tiene y
que la edición anterior no había medido. Diez de ellas están en el sur y en el oeste, que es donde el
mapa anterior tenía sus huecos más grandes. Un vigesimoprimero, Colegiales, también es nuevo, y su
página no está acá: quedó como subzona de Chacagiales, en la primera parte, porque comparte objeto
con dos polos que ya estaban publicados.

Se midieron con exactamente la misma vara que los de la primera parte, y por eso se publican juntos:
**el mapa completo son treinta y nueve polos**, y la diferencia entre una parte y la otra es de
historia editorial, no de método ni de exigencia."""

IDX_BARRIOS = rd(f'{O}/INDICE_DE_BARRIOS.md').strip()
vii=['# VII · Los polos, uno por uno','', COMO_LEER, '', '---', '', IDX_BARRIOS, '',
     '> **Cada página abre con su mapa.** El color dice de qué tipo es cada polo: núcleo compacto, '
     'corredor sobre una avenida, varias piezas bajo un mismo nombre u oferta repartida. Los polos '
     'vecinos van en gris, para que se vea qué hay alrededor.','',
     '---','',
     '# Primera parte · Los diecinueve que ya estaban','',
     f'![Los veinte polos que ya estaban publicados]({MAPAS}/mapa_22.png)','',
     APERTURA_1,'']
for c in sorted(por_comuna):
    fichas_c=[(tit,cue) for tit,cue in por_comuna[c] if ya_estaba(tit)]
    if not fichas_c: continue
    vii.append(f'\n## Comuna {c}\n')
    for tit,cue in fichas_c: vii.append(ficha(tit,cue)); vii.append('')

vii += ['','---','','# Segunda parte · Los veinte que se suman','',
        f'![Los 39 polos gastronómicos de la Ciudad]({MAPAS}/mapa_general.png)','',
        APERTURA_2,'',
        '## Los que todavía no tienen borde dibujado','',
        'Tres de los treinta y nueve polos no tienen todavía su borde dibujado —y un cuarto, Mataderos, '
        'sólo tiene uno transitorio—, y los cuatro están en esta segunda parte. Lo que sí se puede '
        'medir sin inventar un borde es **cuánta gastronomía hay concentrada dentro del barrio que los '
        'contiene** — las concentraciones detectadas por densidad cuya superficie cae en más de la '
        'mitad adentro de ese barrio.','', MAG,'']
for c in sorted(por_comuna):
    fichas_c=[(tit,cue) for tit,cue in por_comuna[c] if not ya_estaba(tit)]
    if not fichas_c: continue
    vii.append(f'\n## Comuna {c}\n')
    for tit,cue in fichas_c: vii.append(ficha(tit,cue)); vii.append('')

COM8 = """No hay ningún polo en la Comuna 8, y conviene decirlo acá y no sólo en el anexo.

Se midieron cuatro concentraciones, con 400 locales entre las cuatro. Ninguna llegó a cumplir dos de
las seis condiciones: no hay allí establecimientos con historia reconocida, ni prensa ni guías que
traten a la zona como un lugar al que se va a comer, ni un mercado o una galería que organice el
movimiento alrededor.

Se buscó con la misma vara que en el resto de la Ciudad, y el resultado es ése. Es probablemente el
dato más útil de esta sección, porque señala dónde hay locales sobre los que apoyarse y todavía no
hay nada que los acompañe."""

vii += ['','---','','# La Ciudad, comuna por comuna','',
        'Las dos partes de arriba ordenan los polos por historia. Este cierre los ordena por '
        'territorio: **quince mapas, uno por comuna**, con todo lo que cae adentro de cada una.','']
for c in sorted(set(por_comuna)|{8}):
    vii.append(f'\n## Comuna {c}\n')
    if os.path.exists(f'{O}/mapas/comuna_{c:02d}.png'):
        vii.append(f'![Mapa de la Comuna {c}]({MAPAS}/comuna_{c:02d}.png)\n')
    if c==8: vii.append(COM8); vii.append(''); continue
    nombres=[tit for tit,_ in por_comuna[c]]
    if nombres:
        vii.append('**' + ' · '.join(nombres) + '**'); vii.append('')
S['VII']='\n'.join(vii)

# los sacados van a la VIII como fichas completas
extra=['\n---\n\n## 4 · Los cinco que salieron, con su página entera\n',
       'Estos cinco tenían página propia en el cuerpo de este atlas. La regla los movió de categoría y '
       'su página se muda acá entera, sin recortar, porque lo que documenta sigue siendo cierto: lo que '
       'cambió es dónde entran.\n',
       '> **Cómo leer estas cinco páginas.** Están tal como se escribieron cuando cada zona era un polo, '
       'y por eso a veces hablan en presente de «este polo». La categoría que vale es la que encabeza '
       'cada una —lugar en observación, zona en estudio o zona medida y no aceptada—.\n']
for tit,cue,com in s1+s2:
    extra.append(f'\n### {tit}\n'); extra.append(cue); extra.append('')
S['VIII']=S['VIII']+'\n'+'\n'.join(extra)

# ---------- normalizar niveles ----------
def demote(t, n=1):
    return re.sub(r'^(#{1,5}) ', lambda m:'#'*(len(m.group(1))+n)+' ', t, flags=re.M)
for k in ['I','II','III','IV','V','VI','VIII','IX']:
    S[k]=re.sub(r'^# ', '# ', S[k], flags=re.M)

TIT={'I':'I · Presentación','II':'II · Qué es un polo gastronómico','III':'III · De dónde salen los datos',
     'IV':'IV · Cómo se leyó el territorio','V':'V · Los establecimientos con historia',
     'VI':'VI · Las colectividades y sus calles','VII':'VII · La Ciudad, comuna por comuna',
     'VIII':'VIII · Los lugares que se midieron y no llegaron','IX':'IX · El alcance de este atlas'}
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

> Cada cifra de este documento lleva su fuente y su fecha, y cada cosa que todavía falta está
> declarada en el lugar donde falta.

---

|  |  |
|---|---|
| **23.981** | locales gastronómicos relevados en toda la Ciudad |
| **39** | polos gastronómicos, en catorce de las quince comunas |
| **53** | lugares estudiados con la misma regla |
| **12.688** | locales en las 124 concentraciones medidas · el 53 % de la gastronomía de la Ciudad en el 15 % de su superficie |
| **90** | bares notables de la Ciudad, y 88 abiertos |
| **15** | lugares donde cocina una colectividad, con sus calles |

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
| **V** | Los establecimientos con historia de la Ciudad |
| **VI** | Las colectividades y sus calles |
| **VII** | **La Ciudad, comuna por comuna** — los 39 polos |
| **VIII** | Los lugares que se midieron y no llegaron |
| **IX** | El alcance de este atlas |
| **Anexo A** | La regla completa, y por qué se calibró así |
| **Anexo B** | Las 124 concentraciones detectadas |
| **Anexo C** | Glosario y fuentes |

---
"""
RESUMEN = rd(f'{O}/RESUMEN_EJECUTIVO.md')
tapa=re.sub(r'\n---\s*$','',tapa.rstrip())+'\n'
QUE_SIGUE = rd(f'{O}/QUE_SIGUE.md').strip()
partes=[tapa, '\n\n---\n\n'+RESUMEN, '\n\n---\n\n'+QUE_SIGUE]
for k in ['I','II','III','IV','V','VI','VII','VIII','IX']:
    partes.append('\n\n---\n\n'+normalizar(k,S[k]))
for t,txt in [('Anexo A · La regla completa',ANEXO_A),
              ('Anexo B · Las 124 concentraciones detectadas',ANEXO_B),
              ('Anexo C · Glosario y fuentes',ANEXO_C)]:
    body=re.sub(r'^# .*$','',txt,count=1,flags=re.M).strip('\n')
    body=re.sub(r'^(#{1,5}) ', lambda m:'#'*(len(m.group(1))+1)+' ', body, flags=re.M)
    partes.append(f'\n\n---\n\n# {t}\n\n'+body.strip('\n'))
doc='\n'.join(partes)
io.open(f'{O}/ATLAS_V3_DOCUMENTO.md','w',encoding='utf-8').write(doc)

# el maquetador lee de build/: se sincroniza acá para que no se desfase nunca mas
import shutil
B=f'{O}/build'
os.makedirs(f'{B}/cartografia',exist_ok=True)
shutil.copy2(f'{O}/ATLAS_V3_DOCUMENTO.md', f'{B}/ATLAS_V3_DOCUMENTO.md')
for f in os.listdir(f'{O}/mapas'):
    if f.endswith('.png'): shutil.copy2(f'{O}/mapas/{f}', f'{B}/cartografia/{f}')
os.makedirs(f'{B}/cartografia/polos',exist_ok=True)
for f in os.listdir(f'{O}/mapas/polos'):
    if f.endswith('.png'): shutil.copy2(f'{O}/mapas/polos/{f}', f'{B}/cartografia/polos/{f}')
print('sincronizado a build/:', len(os.listdir(f'{B}/cartografia')), 'mapas')
print('paginas en VII:',sum(len(v) for v in por_comuna.values()),'| comunas:',len(por_comuna))
print('paginas movidas a VIII:',len(s1)+len(s2), [t for t,_,_ in s1+s2])
print('palabras:',len(doc.split()),'| caracteres:',len(doc))
