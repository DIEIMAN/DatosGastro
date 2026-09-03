# -*- coding: utf-8 -*-
"""Mapa general del Atlas V3.

Color = familia del polo (nucleo, corredor, varias piezas, disperso).
Relleno = si el borde esta dibujado; trama = todavia se muestra el barrio.
"""
import geopandas as gpd, csv, io, re, unicodedata
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
INS='/home/claude/out/insumos'
CRS=5347

ref=gpd.read_file(f'{BASE}/geometria_r8/referencias_r8.geojson').to_crs(CRS)
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
hit=gpd.read_file(f'{BASE}/hitos/hitos_capa_2026.geojson').to_crs(CRS)
per=gpd.read_file(f'{BASE}/ronda_15/geometria/perimetros_18.geojson').to_crs(CRS)
bar=gpd.read_file(f'{INS}/caba_barrios.geojson').to_crs(CRS)
com=gpd.read_file(f'{INS}/caba_comunas.geojson').to_crs(CRS)
est={r['zona_id']:r['cerrado_si_no'] for r in csv.DictReader(io.open(f'{BASE}/ronda_15/perimetros_18.csv',encoding='utf-8-sig'))}
crit=list(csv.DictReader(io.open('/home/claude/out/criterio_admision_55.csv',encoding='utf-8')))
adm=[r for r in crit if r['categoria_por_criterio']=='polo admitido']

# ---------- familia declarada en la ficha ----------
def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    return ''.join(c for c in s if unicodedata.category(c)!='Mn').lower().strip()
FAM_FICHA={}
try:
    for r in csv.DictReader(io.open('/home/claude/out/familias_polos.csv',encoding='utf-8')):
        FAM_FICHA[norm(re.sub(r'^[RZ]\d{1,2}[a-z]?\s*·\s*','',r['nombre']))]=r['familia']
except FileNotFoundError:
    pass
# los que la ficha no declara, resueltos a mano y a la vista del trazado
FAM_MANO={'avenida corrientes':'corredor','boulevard caseros':'corredor','abasto':'nucleo',
          'donado-holmberg':'corredor','federico lacroze':'corredor','retiro':'piezas',
          'monserrat y congreso':'piezas','balvanera · once':'nucleo','balvanera - once':'nucleo',
          'nueva pompeya y parque patricios':'piezas','almagro':'piezas',
          'flores · avellaneda y pasaje ruperto godoy':'nucleo',
          'flores - avellaneda y pasaje ruperto godoy':'nucleo'}

def familia(nombre, geom):
    k=norm(nombre)
    f=FAM_FICHA.get(k) or FAM_MANO.get(k)
    if f and f!='?': return f
    try:
        if geom.geom_type=='MultiPolygon' and len(geom.geoms)>1: return 'piezas'
        mrr=geom.minimum_rotated_rectangle
        xs,ys=mrr.exterior.coords.xy
        import math
        lados=[math.dist((xs[i],ys[i]),(xs[i+1],ys[i+1])) for i in range(4)]
        largo,ancho=max(lados[0],lados[1]),min(lados[0],lados[1])
        if ancho and largo/ancho>=2.0: return 'corredor'
    except Exception:
        pass
    return 'nucleo'

ref_i=ref.set_index('referencia_id'); zon_i=zon.set_index('zona_id')
per_g={z:g.geometry.union_all() for z,g in per.groupby('zona_id')}

# ---------- cierre geometrico (ronda 17): los bordes nuevos mandan ----------
cie=gpd.read_file(f'{BASE}/ronda_17/geometria/perimetros_cierre.geojson').to_crs(CRS)
cie=cie[cie['pieza']=='la zona entera, como se adopta']
NUEVO={r.zona_id:r.geometry for r in cie.itertuples()}
# ---------- cierre geometrico (ronda 18): Caminito cerrado, Mataderos tentativo ----------
c18=gpd.read_file(f'{BASE}/ronda_18/geometria/perimetros_ronda_18.geojson').to_crs(CRS)
for r in c18.itertuples():
    if r.pieza in ('la zona entera, como se adopta','la zona entera · lectura_2_extendida'):
        NUEVO[r.zona_id]=r.geometry
# ---------- ronda 19: La Boca sobre Almirante Brown se extiende por las calles que su texto nombra ----------
c19=gpd.read_file(f'{BASE}/ronda_19/geometria/cinco_sin_ancla_versiones.geojson').to_crs(CRS)
for r in c19.itertuples():
    if r.zona_id=='Z52' and str(r.version).startswith('C '): NUEVO['Z52']=r.geometry
# ---------- los seis repartos decididos: el mapa dibuja lo que la pagina publica ----------
_rep=gpd.read_file(f'{INS}/bordes_repartidos.geojson').to_crs(CRS)
_REP={r.polo_id:r.geometry for r in _rep.itertuples()}
for _k in ('R08','R21','R12','R13','Z37','Z46'):
    if _k in _REP: NUEVO[_k]=_REP[_k]

# ---------- Retiro: el mapa dibujaba un poligono oficial mas grande que el barrio ----------
# el texto publica el barrio (451,52 ha) y el mapa dibujaba 467,14: 15,62 ha y 118 locales de
# diferencia. Las otras tres paginas sin borde usan la capa de barrios, asi que Retiro tambien.
_bar=gpd.read_file(f'{INS}/caba_barrios.geojson').to_crs(CRS)
_cb=[c for c in _bar.columns if 'barrio' in c.lower()][0]
_ret=_bar[_bar[_cb].astype(str).str.upper()=='RETIRO'].geometry.union_all()
# Z46 lo fija el reparto de arriba (barrio menos el solape con el Microcentro)

# borde propio dibujado; los tres que siguen con el barrio; el tentativo
# los repartidos conservan su borde propio: entran a NUEVO por el reparto, no por falta de borde
CERRADO={'Z40','Z54','Z35','Z39','Z37','Z44','Z53','Z52','R08','R12','R13','R21'}
SIN_BORDE={'Z41','Z46','Z27'}
A_MEDIAS={'Z33'}
FUSION={'R09','R19','Z43'}
SUR={'Z50':'S_BARRACAS','Z51':'S_BARRACAS','Z52':'S_LABOCA','Z53':'S_LABOCA','Z54':'Z40'}

rows=[]; hecho=set()
for r in adm:
    i=r['polo_id']; nom=r['nombre']
    if i in NUEVO:
        b='si' if i in CERRADO else ('pieza' if i in A_MEDIAS else 'no')
        rows.append(dict(pid=i,nombre=nom,borde=b,n=1,geometry=NUEVO[i])); continue
    if i in per_g:
        rows.append(dict(pid=i,nombre=nom,borde=('si' if est.get(i)=='si' else 'pieza'),n=1,geometry=per_g[i])); continue
    if i in FUSION:
        if 'F' in hecho: continue
        hecho.add('F')
        rows.append(dict(pid='R09R19Z43',nombre='Chacarita · Colegiales · Federico Lacroze',borde='si',n=3,
                         geometry=ref_i.loc['R09R19_CHACAGIALES','geometry'])); continue
    if i in SUR:
        cont=SUR[i]
        if cont=='Z40':
            if not any(rr['pid']=='Z40' for rr in rows):
                rows.append(dict(pid='Z40',nombre='Nueva Pompeya y Parque Patricios',borde='no',n=1,
                                 geometry=zon_i.loc['Z40','geometry']))
            for rr in rows:
                if rr['pid']=='Z40': rr['n']+=1
            continue
        if cont in hecho: continue
        hecho.add(cont)
        rows.append(dict(pid=i,nombre={'S_BARRACAS':'Barracas','S_LABOCA':'La Boca'}[cont],borde='no',
                         n=sum(1 for k,v in SUR.items() if v==cont and k not in per_g and k not in NUEVO),
                         geometry=zon_i.loc[cont,'geometry'])); continue
    if i in ref_i.index:
        rows.append(dict(pid=i,nombre=nom,borde='si',n=1,geometry=ref_i.loc[i,'geometry']))
    elif i in zon_i.index:
        d=str(zon_i.loc[i,'detalle_geometria'])
        b='si' if (d.startswith('envolvente editorial') or d.startswith('perímetro delimitado')) else 'no'
        rows.append(dict(pid=i,nombre=nom,borde=b,n=1,geometry=zon_i.loc[i,'geometry']))

P=gpd.GeoDataFrame(rows,crs=f'EPSG:{CRS}')
P['familia']=[familia(r.nombre,r.geometry) for r in P.itertuples()]
print('formas:',len(P),'| polos:',int(P.n.sum()))
print(P[P.n>1][['pid','nombre','n']].to_string())
print(P.groupby(['familia','borde']).n.sum())

COL={'nucleo':'#1F6FB2','corredor':'#E08A1E','piezas':'#12897B','disperso':'#8E5AA8'}
OSC={'nucleo':'#0F4470','corredor':'#9A5A08','piezas':'#075A51','disperso':'#5B3270'}
ETQ={'nucleo':'núcleo compacto','corredor':'corredor sobre una avenida',
     'piezas':'varias piezas bajo un mismo nombre','disperso':'oferta repartida'}

x0,y0,x1,y1=com.total_bounds
asp=(y1-y0)/(x1-x0)
fig,ax=plt.subplots(figsize=(11.0, 11.0*asp+0.55), dpi=300)

com.plot(ax=ax,facecolor='#fbfaf8',edgecolor='#d8d2ca',linewidth=0.8,zorder=0)
bar.boundary.plot(ax=ax,color='#e8e3db',linewidth=0.35,zorder=1)
con.plot(ax=ax,facecolor='#efece6',edgecolor='#e2ddd4',linewidth=0.2,zorder=2)

for f in ['nucleo','corredor','piezas','disperso']:
    g=P[(P.familia==f)&(P.borde=='no')]
    if len(g): g.plot(ax=ax,facecolor=COL[f],edgecolor=OSC[f],linewidth=0.7,alpha=0.16,hatch='///',zorder=3)
for f in ['nucleo','corredor','piezas','disperso']:
    g=P[(P.familia==f)&(P.borde=='pieza')]
    if len(g): g.plot(ax=ax,facecolor=COL[f],edgecolor=OSC[f],linewidth=0.9,alpha=0.62,
                      linestyle=(0,(2.6,1.4)),zorder=4)
for f in ['nucleo','corredor','piezas','disperso']:
    g=P[(P.familia==f)&(P.borde=='si')]
    if len(g): g.plot(ax=ax,facecolor=COL[f],edgecolor=OSC[f],linewidth=0.6,alpha=0.88,zorder=5)

hit.plot(ax=ax,color='#20262e',markersize=1.6,zorder=6,alpha=.65)

ACENTO={'Nunez':'Núñez','Villa Ortuzar':'Villa Ortúzar','Garcia del Rio':'García del Río',
        'Donado-Holmberg':'Donado–Holmberg','Nueva Pompeya · eje Av. Saenz':'Nueva Pompeya · eje Av. Sáenz',
        'Centro y Microcentro':'Microcentro'}
P['nombre']=P['nombre'].map(lambda x: ACENTO.get(x,x))
CORTO={'Chacarita · Colegiales · Federico Lacroze':'Chacarita · Colegiales',
       'Nueva Pompeya y Parque Patricios':'Nueva Pompeya · Parque Patricios',
       'Flores · Avellaneda y Pasaje Ruperto Godoy':'Flores · Avellaneda'}
etq=[]
for r in P.itertuples():
    c=r.geometry.representative_point()
    etq.append([CORTO.get(r.nombre,r.nombre), c.x, c.y, r.familia, r.borde, r.geometry.area])
etq.sort(key=lambda e:-e[5])                       # las grandes fijan posicion primero
SEPX,SEPY=1500,380                                  # metros
puestas=[]
for e in etq:
    x,y=e[1],e[2]
    for _ in range(12):
        if not any(abs(x-px)<SEPX and abs(y-py)<SEPY for px,py in puestas): break
        y-=SEPY*0.9
    puestas.append((x,y))
    if abs(y-e[2])>1:
        ax.plot([e[1],x],[e[2],y],color='#9aa1a8',lw=0.35,zorder=6.5)
    ax.annotate(e[0],(x,y),fontsize=4.8,ha='center',va='center',zorder=7,
                color=OSC[e[3]] if e[4]=='no' else '#16202b',
                path_effects=[pe.withStroke(linewidth=2.2,foreground='white')])

pad=700
ax.set_xlim(x0-pad,x1+pad); ax.set_ylim(y0-pad,y1+pad)
sx=x0+700; sy=y1-1400
ax.plot([sx,sx+2000],[sy,sy],color='#20262e',lw=2,solid_capstyle='butt',zorder=8)
ax.text(sx+1000,sy+260,'2 km',ha='center',fontsize=6.5,color='#20262e')
ax.set_axis_off(); ax.set_aspect('equal')

cuenta=P.groupby('familia').n.sum().to_dict()
leg=[Patch(fc=COL[f],ec=OSC[f],alpha=.88,label=f'{ETQ[f]} · {int(cuenta.get(f,0))}')
     for f in ['nucleo','corredor','piezas','disperso'] if cuenta.get(f,0)]
leg+=[Patch(fc='#b9b3aa',ec='#7f7970',alpha=.62,ls=(0,(2.6,1.4)),
            label=f'borde tentativo, no cerrado · {int(P[P.borde=="pieza"].n.sum())}'),
      Patch(fc='#b9b3aa',ec='#7f7970',alpha=.30,hatch='///',
            label=f'todavía sin su borde dibujado · se muestra el barrio · {int(P[P.borde=="no"].n.sum())}'),
      Patch(fc='#efece6',ec='#e2ddd4',label='concentración de locales detectada · 124'),
      Line2D([],[],ls='',marker='o',ms=3,color='#20262e',label='establecimiento histórico con dirección verificada')]
ax.legend(handles=leg,loc='lower left',bbox_to_anchor=(0.015,0.015),frameon=False,fontsize=6.8,
          handlelength=1.6,borderpad=0.3,labelspacing=0.55)

ax.set_title('Los 39 polos gastronómicos de la Ciudad',fontsize=15,loc='left',color='#16202b',pad=3)
ax.text(0,1.004,'el color dice de qué tipo es cada polo · agosto de 2026',
        transform=ax.transAxes,fontsize=8.2,color='#5b5148',va='bottom')
fig.text(0.5,0.012,'Las áreas rayadas son el barrio que contiene al polo mientras se dibuja su borde: '
         'de ellas la cifra citable es la del barrio, no la del polo.',
         ha='center',fontsize=6.6,color='#7a6f64',style='italic')
plt.savefig('/home/claude/out/mapas/mapa_general.png',bbox_inches='tight',facecolor='white',pad_inches=0.24)
print('OK')
