# -*- coding: utf-8 -*-
import geopandas as gpd, csv, re, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.ops import unary_union

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
OUT='/home/claude/out/mapas'; os.makedirs(OUT,exist_ok=True); CRS=5347
ref=gpd.read_file(f'{BASE}/geometria_r8/referencias_r8.geojson').to_crs(CRS)
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
hit=gpd.read_file(f'{BASE}/hitos/hitos_capa_2026.geojson').to_crs(CRS)
crit=list(csv.DictReader(open('/home/claude/out/criterio_admision_55.csv',encoding='utf-8')))
adm=[r for r in crit if r['categoria_por_criterio']=='polo admitido']
ref_i=ref.set_index('referencia_id'); zon_i=zon.set_index('zona_id')
barrios=zon[zon['detalle_geometria'].str.startswith('polígono administrativo',na=False)]
FUSION={'R09','R19','Z43'}; SUR={'Z50':'S_BARRACAS','Z51':'S_BARRACAS','Z52':'S_LABOCA','Z53':'S_LABOCA','Z54':'Z40'}
def es_propio(d): return d.startswith('envolvente editorial') or d.startswith('perímetro delimitado')
def comunas_de(s): return sorted({int(t) for t in re.findall(r'\d+', s or '')})
def corto(n,k=30):
    n=n.replace('·','·')
    return n if len(n)<=k else n[:k].rsplit(' ',1)[0]+'…'

rows=[]
for r in adm:
    i=r['polo_id']
    if i in FUSION: g,pr,key=ref_i.loc['R09R19_CHACAGIALES','geometry'],True,'FUS'
    elif i in SUR:  g,pr,key=zon_i.loc[SUR[i],'geometry'],False,SUR[i]
    elif i in ref_i.index: g,pr,key=ref_i.loc[i,'geometry'],True,i
    else: g,pr,key=zon_i.loc[i,'geometry'],es_propio(zon_i.loc[i,'detalle_geometria']),i
    rows.append(dict(pid=i,nombre=r['nombre'],propio=pr,key=key,comunas=comunas_de(r['comuna']),geometry=g))
P=gpd.GeoDataFrame(rows,crs=f'EPSG:{CRS}')
# una forma por key, con etiqueta combinada
formas=[]
for k,grp in P.groupby('key'):
    ids=list(grp.pid); noms=list(grp.nombre)
    etq = f"{'·'.join(ids)} · {corto(noms[0])}" if len(ids)>1 else f"{ids[0]} · {corto(noms[0])}"
    if k=='FUS': etq='R09·R19·Z43 · Chacagiales'
    formas.append(dict(key=k,etq=etq,propio=bool(grp.propio.iloc[0]),
                       comunas=sorted({c for L in grp.comunas for c in L}),
                       geometry=grp.geometry.iloc[0]))
F=gpd.GeoDataFrame(formas,crs=f'EPSG:{CRS}')

NC={1:'Retiro · San Nicolás · Puerto Madero · San Telmo · Monserrat · Constitución',2:'Recoleta',
 3:'Balvanera · San Cristóbal',4:'La Boca · Barracas · Parque Patricios · Nueva Pompeya',5:'Almagro · Boedo',
 6:'Caballito',7:'Flores · Parque Chacabuco',8:'Villa Soldati · Villa Riachuelo · Villa Lugano',
 9:'Liniers · Mataderos · Parque Avellaneda',10:'Villa Real · Monte Castro · Versalles · Floresta · Vélez Sarsfield · Villa Luro',
 11:'Villa Gral. Mitre · Villa Devoto · Villa del Parque · Villa Santa Rita',
 12:'Coghlan · Saavedra · Villa Urquiza · Villa Pueyrredón',13:'Núñez · Belgrano · Colegiales',14:'Palermo',
 15:'Chacarita · Villa Crespo · Paternal · Villa Ortúzar · Agronomía · Parque Chas'}
hechos=[]
for c in sorted({x for r in formas for x in r['comunas']}):
    sel=F[F.comunas.apply(lambda L:c in L)]
    if sel.empty: continue
    xmin,ymin,xmax,ymax=sel.total_bounds
    w,h=xmax-xmin,ymax-ymin; pad=max(max(w,h)*0.09,420)
    xmin-=pad; xmax+=pad; ymin-=pad; ymax+=pad; w,h=xmax-xmin,ymax-ymin
    ratio=h/w; figw=7.6; figh=max(4.2,min(9.6,figw*ratio+0.9))
    fig,ax=plt.subplots(figsize=(figw,figh),dpi=200)
    barrios.boundary.plot(ax=ax,color='#dcd7d0',linewidth=0.7,zorder=1)
    con.plot(ax=ax,facecolor='#eae4db',edgecolor='#ded6c9',linewidth=0.35,zorder=2)
    otr=F[~F.comunas.apply(lambda L:c in L)]
    otr[otr.propio].plot(ax=ax,facecolor='#dccec9',edgecolor='#c6ada3',linewidth=0.4,alpha=.75,zorder=3)
    s2=sel[~sel.propio]; s1=sel[sel.propio]
    if len(s2): s2.plot(ax=ax,facecolor='#c98f7f',edgecolor='#9c5343',linewidth=1.0,alpha=.32,hatch='////',zorder=4)
    if len(s1): s1.plot(ax=ax,facecolor='#b0402d',edgecolor='#6f2014',linewidth=0.8,alpha=.9,zorder=5)
    hit.cx[xmin:xmax,ymin:ymax].plot(ax=ax,color='#16202a',markersize=6,zorder=6,alpha=.85)
    for _,r in sel.iterrows():
        p=r.geometry.representative_point()
        ax.annotate(r.etq,(p.x,p.y),fontsize=5.5,ha='center',va='center',zorder=7,clip_on=True,
            color='white' if r.propio else '#7d2417',
            bbox=dict(boxstyle='round,pad=0.22',fc='#6f2014' if r.propio else '#fffcf8',
                      ec='none' if r.propio else '#c98f7f',lw=.5,alpha=.93))
    ax.set_xlim(xmin,xmax); ax.set_ylim(ymin,ymax); ax.set_aspect('equal'); ax.set_axis_off()
    esc=1000 if w<5000 else 2000
    x0=xmin+w*0.05; y0=ymin+h*0.05
    ax.plot([x0,x0+esc],[y0,y0],color='#16202a',lw=2,solid_capstyle='butt',zorder=8)
    ax.text(x0+esc/2,y0+h*0.016,f'{esc//1000} km',ha='center',fontsize=6,color='#16202a')
    ax.set_title(f'Comuna {c}',fontsize=13,loc='left',color='#16202a',pad=2)
    ax.text(0,1.008,NC.get(c,''),transform=ax.transAxes,fontsize=6.5,color='#5b5148',va='bottom')
    leg=[Patch(fc='#b0402d',ec='#6f2014',alpha=.9,label='polo de esta comuna · perímetro propio'),
         Patch(fc='#c98f7f',ec='#9c5343',alpha=.32,hatch='////',label='polo de esta comuna · se muestra su barrio'),
         Patch(fc='#dccec9',ec='#c6ada3',label='polo de otra comuna'),
         Patch(fc='#eae4db',ec='#ded6c9',label='concentración detectada'),
         Line2D([],[],ls='',marker='o',ms=3.5,color='#16202a',label='referente verificado')]
    ax.legend(handles=leg,loc='lower right',frameon=True,facecolor='white',edgecolor='#e6e0d8',
              fontsize=5.4,handlelength=1.3,borderpad=0.4,labelspacing=0.4,framealpha=.94)
    f=f'{OUT}/comuna_{c:02d}.png'; plt.savefig(f,bbox_inches='tight',facecolor='white',pad_inches=0.14); plt.close()
    hechos.append((c,len(sel)))
print('mapas:',len(hechos),hechos)
