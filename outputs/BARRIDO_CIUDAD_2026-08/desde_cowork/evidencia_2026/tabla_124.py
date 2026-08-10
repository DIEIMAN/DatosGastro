# -*- coding: utf-8 -*-
"""Genera la tabla completa de las 124 concentraciones para el Anexo B.

Cada fila: barrio, comuna, locales, hectareas, y a que polo pertenece (si pertenece).
"""
import geopandas as gpd, csv, io, re, unicodedata

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
CRS=5347
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
bar=gpd.read_file('/home/claude/out/insumos/caba_barrios.geojson').to_crs(CRS)

# ---------- las formas de los polos, igual que en el mapa ----------
ref=gpd.read_file(f'{BASE}/geometria_r8/referencias_r8.geojson').to_crs(CRS)
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
per=gpd.read_file(f'{BASE}/ronda_15/geometria/perimetros_18.geojson').to_crs(CRS)
crit=list(csv.DictReader(io.open('/home/claude/out/criterio_admision_55.csv',encoding='utf-8')))
adm=[r for r in crit if r['categoria_por_criterio']=='polo admitido']
ref_i=ref.set_index('referencia_id'); zon_i=zon.set_index('zona_id')
per_g={z:g.geometry.union_all() for z,g in per.groupby('zona_id')}
ACENTO={'Nunez':'Núñez','Villa Ortuzar':'Villa Ortúzar','Garcia del Rio':'García del Río',
        'Donado-Holmberg':'Donado–Holmberg','Nueva Pompeya · eje Av. Saenz':'Nueva Pompeya · eje Av. Sáenz',
        'Centro y Microcentro':'Microcentro'}
FUSION={'R09','R19','Z43'}
filas=[]; hecho=set()
for r in adm:
    i=r['polo_id']; nom=ACENTO.get(r['nombre'],r['nombre'])
    if i in per_g: filas.append((nom,per_g[i])); continue
    if i in FUSION:
        if 'F' in hecho: continue
        hecho.add('F'); filas.append(('Chacarita · Colegiales · Federico Lacroze',
                                      ref_i.loc['R09R19_CHACAGIALES','geometry'])); continue
    if i in ref_i.index: filas.append((nom,ref_i.loc[i,'geometry']))
    elif i in zon_i.index: filas.append((nom,zon_i.loc[i,'geometry']))
POL=gpd.GeoDataFrame({'polo':[a for a,_ in filas]},geometry=[b for _,b in filas],crs=f'EPSG:{CRS}')

def mayor(izq, der, campo):
    """Para cada fila de izq, el valor de `campo` en der con mayor superficie compartida."""
    j=gpd.overlay(izq[['polo_id','geometry']], der, how='intersection', keep_geom_type=False)
    if j.empty: return {}
    j=j[j.geometry.area>0].copy(); j['a']=j.geometry.area
    idx=j.groupby('polo_id')['a'].idxmax()
    b=j.loc[idx]
    return {r.polo_id:(getattr(r,campo), r.a) for r in b.itertuples()}

BARRIO=mayor(con, bar[['BARRIO','COMUNA','geometry']], 'BARRIO')
COMUNA=mayor(con, bar[['BARRIO','COMUNA','geometry']], 'COMUNA')
POLO  =mayor(con, POL, 'polo')

def titulo(s):
    chicas={'de','del','y','la','las','los','el'}
    return ' '.join(w.capitalize() if w.lower() not in chicas else w.lower()
                    for w in str(s).title().split())

out=[]
for r in con.itertuples():
    a=r.geometry.area
    pol,pa=POLO.get(r.polo_id,(None,0))
    dentro = pol if pa/a>=0.5 else None
    out.append(dict(id=r.polo_id,
                    barrio=titulo(BARRIO.get(r.polo_id,('—',0))[0]),
                    comuna=int(COMUNA.get(r.polo_id,(0,0))[0] or 0),
                    locales=int(r.n_locales), ha=round(r.ha,1),
                    polo=dentro or '—'))
out.sort(key=lambda d:(-d['locales']))

w=csv.DictWriter(io.open('/home/claude/out/anexo_B_124.csv','w',newline='',encoding='utf-8'),
                 fieldnames=['id','barrio','comuna','locales','ha','polo'])
w.writeheader(); [w.writerow(d) for d in out]

dentro=[d for d in out if d['polo']!='—']
print('124 filas · adentro de algún polo:',len(dentro),'· locales:',sum(d['locales'] for d in dentro))
print('afuera:',len(out)-len(dentro),'· locales:',sum(d['locales'] for d in out if d['polo']=='—'))

L=['| concentración | barrio | comuna | locales | ha | polo al que pertenece |','|---|---|---:|---:|---:|---|']
for d in out:
    L.append(f"| {d['id']} | {d['barrio']} | {d['comuna']} | {d['locales']} | {str(d['ha']).replace('.',',')} | {d['polo']} |")
io.open('/home/claude/out/_tabla_124.md','w',encoding='utf-8').write('\n'.join(L)+'\n')
print('tabla escrita')
