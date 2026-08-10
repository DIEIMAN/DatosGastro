# -*- coding: utf-8 -*-
"""Arma, para cada polo, el bloque de lugares destacados que hay adentro de su borde.

Sale de la capa de establecimientos con reconocimiento: Bares Notables, MICHELIN,
pizzerias emblematicas, restaurantes iconicos, rankings internacionales, mercados y
heladerias historicas.
"""
import geopandas as gpd, pandas as pd, csv, io, re, os, unicodedata

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
CRS=5347

src=io.open('/home/claude/out/mapa_general.py',encoding='utf-8').read()
exec(src.split("P=gpd.GeoDataFrame(rows")[0])
P=gpd.GeoDataFrame(rows,crs=f'EPSG:{CRS}')
ACENTO={'Nunez':'Núñez','Villa Ortuzar':'Villa Ortúzar','Garcia del Rio':'García del Río',
        'Donado-Holmberg':'Donado–Holmberg','Nueva Pompeya · eje Av. Saenz':'Nueva Pompeya · eje Av. Sáenz',
        'Centro y Microcentro':'Microcentro'}
P['nombre']=P['nombre'].map(lambda x: ACENTO.get(x,x))

H=gpd.read_file(f'{BASE}/hitos/hitos_capa_2026.geojson').to_crs(CRS)
H=H[H.geometry.notna()].copy()

ORDEN=['Bar Notable','Restaurante Icónico','Pizzería emblemática','MICHELIN',
       'Ranking internacional','Mercado/patio','Heladería histórica','Patrimonio normativo']
SG={'Bar Notable':'1 Bar Notable','Restaurante Icónico':'1 restaurante icónico',
    'Pizzería emblemática':'1 pizzería emblemática','MICHELIN':'1 en la guía MICHELIN',
    'Ranking internacional':'1 en un ranking internacional','Mercado/patio':'1 mercado',
    'Heladería histórica':'1 heladería histórica','Patrimonio normativo':'1 con protección patrimonial'}
PL={'Bar Notable':'Bares Notables','Restaurante Icónico':'restaurantes icónicos',
    'Pizzería emblemática':'pizzerías emblemáticas','MICHELIN':'en la guía MICHELIN',
    'Ranking internacional':'en rankings internacionales','Mercado/patio':'mercados y patios de comidas',
    'Heladería histórica':'heladerías históricas','Patrimonio normativo':'con protección patrimonial'}
ETQ_L={'Bar Notable':'Bares Notables','Restaurante Icónico':'Restaurantes icónicos',
       'Pizzería emblemática':'Pizzerías emblemáticas','MICHELIN':'En la guía MICHELIN',
       'Ranking internacional':'En rankings internacionales','Mercado/patio':'Mercados y patios de comidas',
       'Heladería histórica':'Heladerías históricas','Patrimonio normativo':'Con protección patrimonial'}
MENOR={'de','del','y','la','las','los','el','a','al','en'}
def bonito(n):
    n=str(n or '').strip()
    if n.isupper() or n.replace(' ','').isupper():
        n=' '.join(w.capitalize() if w.lower() not in MENOR else w.lower() for w in n.split())
        if n: n=n[0].upper()+n[1:]
    return n

def _tit(x):
    return ' '.join(w.capitalize() if w.lower() not in MENOR else w.lower() for w in x.split()).strip()

def limpiar(d):
    """«MOREAU DE JUSTO, ALICIA AV. 1840» -> «Av. Alicia Moreau de Justo 1840»."""
    d=str(d or '').strip()
    if d.lower() in ('nan','none',''): return ''
    if d.upper()!=d: return d                      # ya viene escrita como corresponde
    m=re.match(r'^(.*?)\s+(\d[\w/-]*)$', d)         # separo la altura
    cuerpo, alt = (m.group(1), m.group(2)) if m else (d, '')
    tipo=''
    for t,lab in [('AV.','Av.'),('AVDA.','Av.'),('AV','Av.'),('PJE.','Pje.'),('PASAJE','Pje.'),
                  ('CALLE',''),('DIAG.','Diag.')]:
        if re.search(r'(^|[\s,.])'+re.escape(t)+r'($|[\s,])', cuerpo):
            cuerpo=re.sub(r'(^|[\s,.])'+re.escape(t)+r'($|[\s,])',' ',cuerpo).strip(' ,'); tipo=lab; break
    if ',' in cuerpo:
        ape,nom=[x.strip(' ,') for x in cuerpo.split(',',1)]
        cuerpo=f'{_tit(nom)} {_tit(ape)}'.strip()
    else:
        cuerpo=_tit(cuerpo)
    return ' '.join(x for x in [tipo,cuerpo,alt] if x)

filas=[]
for r in P.itertuples():
    dentro=H[H.geometry.within(r.geometry)]; cerca=False
    if not len(dentro):
        dentro=H[H.geometry.distance(r.geometry)<=300]; cerca=True
    if not len(dentro): continue
    bloques=[]
    for t in ORDEN:
        g=dentro[dentro.tipo==t]
        if not len(g): continue
        nombres=[]
        for e in g.itertuples():
            dir_=limpiar(e.direccion)
            rec=limpiar(e.reconocimiento)
            extra=''
            if t=='MICHELIN' and rec and rec!='Recomendado/seleccionado':
                extra=f' · {rec}'
            if t=='Ranking internacional' and rec:
                extra=f' · {rec}'
            nombres.append(f'**{bonito(e.nombre)}**' + (f', {dir_}' if dir_ else '') + extra)
        bloques.append((t,len(g),nombres))
    filas.append((r.pid,r.nombre,r.borde,dentro,bloques,cerca))

def parrafo(nombre,borde,dentro,bloques,cerca):
    n=len(dentro)
    cab=[SG[t] if c==1 else f'{c} {PL[t]}' for t,c,_ in bloques]
    L=[]
    aviso=' Son los del barrio y no los del polo, porque su borde todavía no está dibujado.' if borde=='no' else ''
    donde='En el entorno inmediato, a menos de trescientos metros, hay' if cerca else 'Adentro hay'
    L.append(f'**Para conocer.** {donde} **{n} lugares con reconocimiento**: ' +
             (', '.join(cab[:-1]) + ' y ' + cab[-1] if len(cab)>1 else cab[0]) + '.' + aviso)
    # un dato que valga la pena destacar, si el reconocimiento lo sostiene
    rec=[str(x) for x in dentro.reconocimiento.fillna('')]
    est=sum(1 for x in rec if 'Estrella' in x)
    bib=sum(1 for x in rec if 'Bib Gourmand' in x)
    best=sum(1 for x in rec if '50 Best' in x)
    nota=[]
    if est: nota.append(f'**{est} con estrella MICHELIN**' if est>1 else '**uno con estrella MICHELIN**')
    if bib: nota.append(f'{bib} con Bib Gourmand' if bib>1 else 'uno con Bib Gourmand')
    if best: nota.append(f'{best} en la lista de los 50 mejores de América Latina'
                         if best>1 else 'uno en la lista de los 50 mejores de América Latina')
    if nota:
        L.append('')
        L.append('Entre ellos, ' + (', '.join(nota[:-1]) + ' y ' + nota[-1] if len(nota)>1 else nota[0]) + '.')
    L.append('')
    for t,c,nombres in bloques:
        L.append(f'- *{ETQ_L[t]}* — ' + ' · '.join(nombres))
    return '\n'.join(L)

out={}
for pid,nombre,borde,dentro,bloques,cerca in filas:
    out[nombre]=parrafo(nombre,borde,dentro,bloques,cerca)

w=csv.writer(io.open('/home/claude/out/destacados.csv','w',newline='',encoding='utf-8'))
w.writerow(['polo','texto'])
for k,v in out.items(): w.writerow([k,v])
print('polos con lugares destacados:',len(out),'de',len(P))
tot=sum(len(d) for _,_,_,d,_,_ in filas)
print('establecimientos ubicados dentro de algún polo:',tot,'de',len(H))
for k in list(out)[:2]:
    print('\n---',k,'---\n',out[k][:400])
