# -*- coding: utf-8 -*-
"""Mapa general del Atlas V3. Distingue el perimetro propio del poligono del barrio,
que es un provisorio y no debe leerse como la extension del polo."""
import geopandas as gpd, csv
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
CRS=5347
ref=gpd.read_file(f'{BASE}/geometria_r8/referencias_r8.geojson').to_crs(CRS)
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
hit=gpd.read_file(f'{BASE}/hitos/hitos_capa_2026.geojson').to_crs(CRS)
crit=list(csv.DictReader(open('/home/claude/out/criterio_admision_55.csv',encoding='utf-8')))
adm=[r for r in crit if r['categoria_por_criterio']=='polo admitido']

ref_i=ref.set_index('referencia_id'); zon_i=zon.set_index('zona_id')
FUSION={'R09','R19','Z43'}
SUR={'Z50':'S_BARRACAS','Z51':'S_BARRACAS','Z52':'S_LABOCA','Z53':'S_LABOCA','Z54':'Z40'}

def clase(det):
    if det.startswith('envolvente editorial'): return 'propio'
    if det.startswith('perímetro delimitado'): return 'propio'
    return 'barrio'

rows=[]; hecho=set()
for r in adm:
    i=r['polo_id']
    if i in FUSION:
        if 'FUS' in hecho: continue
        hecho.add('FUS')
        rows.append(dict(pid='R09·R19·Z43', etq='R09/19/43', nombre='Chacagiales', clase='propio',
                         n=3, geometry=ref_i.loc['R09R19_CHACAGIALES','geometry'])); continue
    if i in SUR:
        cont=SUR[i]
        cuantos=sum(1 for k,v in SUR.items() if v==cont)
        if cont=='Z40':                      # Z54 cae dentro del poligono que ya dibuja Z40
            for rr in rows:
                if rr['pid']=='Z40': rr['etq']='Z40·Z54'; rr['n']+=1
            continue
        if cont in hecho: continue
        hecho.add(cont)
        rows.append(dict(pid=i, etq={'S_BARRACAS':'Z50·Z51','S_LABOCA':'Z52·Z53'}[cont],
                         nombre=r['nombre'], clase='barrio', n=cuantos,
                         geometry=zon_i.loc[cont,'geometry'])); continue
    if i in ref_i.index:
        rows.append(dict(pid=i, etq=i, nombre=r['nombre'], clase='propio', n=1,
                         geometry=ref_i.loc[i,'geometry']))
    elif i in zon_i.index:
        rows.append(dict(pid=i, etq=i, nombre=r['nombre'],
                         clase=clase(zon_i.loc[i,'detalle_geometria']), n=1,
                         geometry=zon_i.loc[i,'geometry']))
polos=gpd.GeoDataFrame(rows, crs=f'EPSG:{CRS}')
prop=polos[polos.clase=='propio']; barr=polos[polos.clase=='barrio']
print('formas:',len(polos),'| perimetro propio:',prop.n.sum(),'polos en',len(prop),'formas',
      '| por trazar:',barr.n.sum(),'polos en',len(barr),'formas')

barrios = zon[zon['detalle_geometria'].str.startswith('polígono administrativo', na=False)]

fig,ax=plt.subplots(figsize=(9.6,11.4), dpi=200)
barrios.boundary.plot(ax=ax,color='#dcd7d0',linewidth=0.4,zorder=1)
con.plot(ax=ax,facecolor='#eae4db',edgecolor='#ded6c9',linewidth=0.25,zorder=2)
barr.plot(ax=ax,facecolor='#c98f7f',edgecolor='#9c5343',linewidth=0.8,alpha=0.30,zorder=3,hatch='////')
prop.plot(ax=ax,facecolor='#b0402d',edgecolor='#6f2014',linewidth=0.6,alpha=0.88,zorder=4)
hit.plot(ax=ax,color='#16202a',markersize=2.0,zorder=5,alpha=.8)

for _,r in polos.iterrows():
    c=r.geometry.representative_point()
    prop_ = r.clase=='propio'
    ax.annotate(r.etq,(c.x,c.y),fontsize=4.3,ha='center',va='center',
                color='white' if prop_ else '#7d2417', zorder=6,
                bbox=dict(boxstyle='round,pad=0.13',fc='#6f2014' if prop_ else '#fdf9f4',
                          ec='none' if prop_ else '#c98f7f', lw=.4, alpha=.9))

xmin,ymin,xmax,ymax=polos.total_bounds; pad=900
ax.set_xlim(xmin-pad,xmax+pad); ax.set_ylim(ymin-pad,ymax+pad)
x0=xmin-pad+500; y0=ymin-pad+500
ax.plot([x0,x0+2000],[y0,y0],color='#16202a',lw=2,solid_capstyle='butt',zorder=7)
ax.text(x0+1000,y0+190,'2 km',ha='center',fontsize=6.5,color='#16202a')
ax.set_axis_off(); ax.set_aspect('equal')
leg=[Patch(fc='#b0402d',ec='#6f2014',alpha=.88,label=f'polo con perímetro propio · {int(prop.n.sum())}'),
     Patch(fc='#c98f7f',ec='#9c5343',alpha=.30,hatch='////',
           label=f'perímetro todavía no trazado · se muestra el barrio que lo contiene · {int(barr.n.sum())}'),
     Patch(fc='#eae4db',ec='#ded6c9',label='concentración detectada por densidad · 124'),
     Line2D([],[],ls='',marker='o',ms=3,color='#16202a',label='referente con dirección verificada · 215')]
ax.legend(handles=leg,loc='lower right',frameon=False,fontsize=6.3,handlelength=1.5,borderpad=0.3,
          labelspacing=0.55)
ax.set_title('Los 41 polos gastronómicos admitidos',fontsize=13.5,loc='left',color='#16202a',pad=2)
ax.text(0,1.005,'sobre las 124 concentraciones detectadas por densidad · agosto de 2026',
        transform=ax.transAxes,fontsize=7.6,color='#5b5148',va='bottom')
fig.text(0.5,0.012,'Las áreas rayadas son la extensión del barrio, no la del polo: son un provisorio '
         'hasta que se trace el perímetro. No se pueden usar para medir superficie ni comparar tamaños.',
         ha='center',fontsize=6.4,color='#7a6f64',style='italic')
plt.savefig('/home/claude/out/mapas/mapa_general.png',bbox_inches='tight',facecolor='white',pad_inches=0.25)
print('OK')
