# -*- coding: utf-8 -*-
import geopandas as gpd, csv, re, os, io
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
INS='/home/claude/out/insumos'; OUT='/home/claude/out/mapas'; os.makedirs(OUT,exist_ok=True); CRS=5347
ref=gpd.read_file(f'{BASE}/geometria_r8/referencias_r8.geojson').to_crs(CRS)
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
hit=gpd.read_file(f'{BASE}/hitos/hitos_capa_2026.geojson').to_crs(CRS)
per=gpd.read_file(f'{BASE}/ronda_15/geometria/perimetros_18.geojson').to_crs(CRS)
bar=gpd.read_file(f'{INS}/caba_barrios.geojson').to_crs(CRS)
com=gpd.read_file(f'{INS}/caba_comunas.geojson').to_crs(CRS)
com['c']=com['COMUNAS'].astype(float).astype(int)
est={r['zona_id']:r['cerrado_si_no'] for r in csv.DictReader(io.open(f'{BASE}/ronda_15/perimetros_18.csv',encoding='utf-8-sig'))}
crit=list(csv.DictReader(io.open('/home/claude/out/criterio_admision_55.csv',encoding='utf-8')))
adm=[r for r in crit if r['categoria_por_criterio']=='polo admitido']
ref_i=ref.set_index('referencia_id'); zon_i=zon.set_index('zona_id')
per_g={z:g.geometry.union_all() for z,g in per.groupby('zona_id')}
FUSION={'R09','R19','Z43'}; SUR={'Z50':'S_BARRACAS','Z51':'S_BARRACAS','Z52':'S_LABOCA','Z53':'S_LABOCA','Z54':'Z40'}
cie=gpd.read_file(f'{BASE}/ronda_17/geometria/perimetros_cierre.geojson').to_crs(CRS)
cie=cie[cie['pieza']=='la zona entera, como se adopta']
NUEVO={r.zona_id:r.geometry for r in cie.itertuples()}
c18=gpd.read_file(f'{BASE}/ronda_18/geometria/perimetros_ronda_18.geojson').to_crs(CRS)
for r in c18.itertuples():
    if r.pieza in ('la zona entera, como se adopta','la zona entera · lectura_2_extendida'):
        NUEVO[r.zona_id]=r.geometry
# ---------- ronda 19: La Boca sobre Almirante Brown se extiende por las calles que su texto nombra ----------
c19=gpd.read_file(f'{BASE}/ronda_19/geometria/cinco_sin_ancla_versiones.geojson').to_crs(CRS)
for r in c19.itertuples():
    if r.zona_id=='Z52' and str(r.version).startswith('C '): NUEVO['Z52']=r.geometry
CERRADO={'Z40','Z54','Z35','Z39','Z37','Z44','Z53','Z52'}; SIN_BORDE={'Z41','Z46','Z27'}; A_MEDIAS={'Z33'}
import unicodedata
def _n(x):
    x=unicodedata.normalize('NFD',x or '')
    return ''.join(c for c in x if unicodedata.category(c)!='Mn').lower().strip()
FAM={}
for r in csv.DictReader(io.open('/home/claude/out/familias_polos.csv',encoding='utf-8')):
    FAM[_n(re.sub(r'^[RZ]\d{1,2}[a-z]?\s*·\s*','',r['nombre']))]=r['familia']
FAM_MANO={'avenida corrientes':'corredor','boulevard caseros':'corredor','abasto':'nucleo',
 'donado-holmberg':'corredor','federico lacroze':'corredor','retiro':'piezas',
 'monserrat y congreso':'piezas','balvanera · once':'nucleo','nueva pompeya y parque patricios':'piezas',
 'almagro':'piezas','flores · avellaneda y pasaje ruperto godoy':'nucleo'}
def familia(nom,g):
    f=FAM.get(_n(nom)) or FAM_MANO.get(_n(nom))
    if f and f!='?': return f
    try:
        if g.geom_type=='MultiPolygon' and len(g.geoms)>1: return 'piezas'
        import math
        xs,ys=g.minimum_rotated_rectangle.exterior.coords.xy
        L=[math.dist((xs[i],ys[i]),(xs[i+1],ys[i+1])) for i in range(4)]
        a,b=max(L[0],L[1]),min(L[0],L[1])
        if b and a/b>=2.0: return 'corredor'
    except Exception: pass
    return 'nucleo'
COL={'nucleo':'#1F6FB2','corredor':'#E08A1E','piezas':'#12897B','disperso':'#8E5AA8'}
OSC={'nucleo':'#0F4470','corredor':'#9A5A08','piezas':'#075A51','disperso':'#5B3270'}
ETQF={'nucleo':'núcleo compacto','corredor':'corredor sobre una avenida',
      'piezas':'varias piezas bajo un mismo nombre','disperso':'oferta repartida'}
def comunas_de(s): return sorted({int(t) for t in re.findall(r'\d+', s or '')})
def corto(n,k=30): return n if len(n)<=k else n[:k].rsplit(' ',1)[0]+'…'
rows=[]
for r in adm:
    i=r['polo_id']; C=comunas_de(r['comuna'])
    if i in NUEVO:
        g,key=NUEVO[i],i
        cl='propio' if i in CERRADO else ('pieza' if i in A_MEDIAS else 'barrio')
    elif i in per_g: g,cl,key=per_g[i],('propio' if est.get(i)=='si' else 'pieza'),i
    elif i in FUSION: g,cl,key=ref_i.loc['R09R19_CHACAGIALES','geometry'],'propio','FUS'
    elif i in SUR: g,cl,key=zon_i.loc[SUR[i],'geometry'],'barrio',SUR[i]
    elif i in ref_i.index: g,cl,key=ref_i.loc[i,'geometry'],'propio',i
    else:
        d=str(zon_i.loc[i,'detalle_geometria'])
        cl='propio' if (d.startswith('envolvente editorial') or d.startswith('perímetro delimitado')) else 'barrio'
        g,key=zon_i.loc[i,'geometry'],i
    rows.append(dict(pid=i,nombre=r['nombre'],clase=cl,key=key,comunas=C,geometry=g))
P=gpd.GeoDataFrame(rows,crs=f'EPSG:{CRS}')
formas=[]
for k,grp in P.groupby('key'):
    ids=list(grp.pid)
    etq=corto(grp.nombre.iloc[0],38)
    if k=='FUS': etq='Chacarita · Colegiales · Federico Lacroze'
    formas.append(dict(key=k,etq=etq,clase=grp.clase.iloc[0],
                       comunas=sorted({c for L in grp.comunas for c in L}),geometry=grp.geometry.iloc[0]))
F=gpd.GeoDataFrame(formas,crs=f'EPSG:{CRS}')
F['familia']=[familia(r.etq,r.geometry) for r in F.itertuples()]
NC={1:'Retiro · San Nicolás · Puerto Madero · San Telmo · Monserrat · Constitución',2:'Recoleta',
 3:'Balvanera · San Cristóbal',4:'La Boca · Barracas · Parque Patricios · Nueva Pompeya',5:'Almagro · Boedo',
 6:'Caballito',7:'Flores · Parque Chacabuco',8:'Villa Soldati · Villa Riachuelo · Villa Lugano',
 9:'Liniers · Mataderos · Parque Avellaneda',10:'Villa Real · Monte Castro · Versalles · Floresta · Vélez Sarsfield · Villa Luro',
 11:'Villa Gral. Mitre · Villa Devoto · Villa del Parque · Villa Santa Rita',
 12:'Coghlan · Saavedra · Villa Urquiza · Villa Pueyrredón',13:'Núñez · Belgrano · Colegiales',14:'Palermo',
 15:'Chacarita · Villa Crespo · Paternal · Villa Ortúzar · Agronomía · Parque Chas'}
hechos=[]
for c in sorted({x for r in formas for x in r['comunas']}|{8}):
    sel=F[F.comunas.apply(lambda L:c in L)]
    gc=com[com.c==c]
    _g=[gc.geometry.union_all()]+([sel.geometry.union_all()] if len(sel) else [])
    xmin,ymin,xmax,ymax=gpd.GeoSeries(_g,crs=F.crs).total_bounds
    w,h=xmax-xmin,ymax-ymin; pad=max(max(w,h)*0.07,380)
    xmin-=pad; xmax+=pad; ymin-=pad; ymax+=pad; w,h=xmax-xmin,ymax-ymin
    figw=7.6; figh=max(4.2,min(9.6,figw*(h/w)+0.95))
    fig,ax=plt.subplots(figsize=(figw,figh),dpi=300)
    com.plot(ax=ax,facecolor='#fbf9f6',edgecolor='#cfc8bf',linewidth=0.7,zorder=0)
    gc.plot(ax=ax,facecolor='#ffffff',edgecolor='#a9a096',linewidth=1.4,zorder=1)
    bar.boundary.plot(ax=ax,color='#e0d9d0',linewidth=0.55,zorder=2)
    con.plot(ax=ax,facecolor='#eae4db',edgecolor='#ded6c9',linewidth=0.3,zorder=3)
    otr=F[~F.comunas.apply(lambda L:c in L)]
    otr.plot(ax=ax,facecolor='#dccec9',edgecolor='#c6ada3',linewidth=0.4,alpha=.72,zorder=4)
    for cl,al,hz,ls,ht in [('barrio',.20,5,'-','///'),('pieza',.62,6,(0,(2.6,1.4)),None),('propio',.88,7,'-',None)]:
        for f in ['nucleo','corredor','piezas','disperso']:
            s2=sel[(sel.clase==cl)&(sel.familia==f)]
            if len(s2): s2.plot(ax=ax,facecolor=COL[f],edgecolor=OSC[f],linewidth=0.9,alpha=al,
                                zorder=hz,hatch=ht,linestyle=ls)
    hit.cx[xmin:xmax,ymin:ymax].plot(ax=ax,color='#141d26',markersize=6,zorder=8,alpha=.85)
    for _,r in sel.iterrows():
        p=r.geometry.representative_point()
        ax.annotate(r.etq,(p.x,p.y),fontsize=6.4,ha='center',va='center',zorder=9,clip_on=True,
            color=OSC[r.familia] if r.clase=='barrio' else '#16202b',
            path_effects=[pe.withStroke(linewidth=2.6,foreground='white')])
    ax.set_xlim(xmin,xmax); ax.set_ylim(ymin,ymax); ax.set_aspect('equal'); ax.set_axis_off()
    esc=1000 if w<5000 else 2000
    sx=xmin+w*0.04; sy=ymin+h*0.045
    ax.plot([sx,sx+esc],[sy,sy],color='#141d26',lw=2,solid_capstyle='butt',zorder=10)
    ax.text(sx+esc/2,sy+h*0.016,f'{esc//1000} km',ha='center',fontsize=6,color='#141d26')
    ax.set_title(f'Comuna {c}',fontsize=13,loc='left',color='#141d26',pad=2)
    ax.text(0,1.008,NC.get(c,''),transform=ax.transAxes,fontsize=6.5,color='#5b5148',va='bottom')
    pres=[f for f in ['nucleo','corredor','piezas','disperso'] if len(sel[sel.familia==f])]
    leg=[Patch(fc=COL[f],ec=OSC[f],alpha=.88,label=ETQF[f]) for f in pres]
    leg+=[Patch(fc='#b9b3aa',ec='#7f7970',alpha=.28,hatch='///',label='todavía sin su borde dibujado'),
         Patch(fc='#dccec9',ec='#c6ada3',label='polo de otra comuna'),
         Patch(fc='#eae4db',ec='#ded6c9',label='concentración de locales detectada'),
         Line2D([],[],ls='',marker='o',ms=3.5,color='#141d26',label='establecimiento histórico verificado')]
    ax.legend(handles=leg,loc='lower right',frameon=True,facecolor='white',edgecolor='#e6e0d8',
              fontsize=5.9,handlelength=1.3,borderpad=0.4,labelspacing=0.4,framealpha=.95)
    plt.savefig(f'{OUT}/comuna_{c:02d}.png',bbox_inches='tight',facecolor='white',pad_inches=0.14); plt.close()
    hechos.append((c,len(sel)))
print('mapas comunales:',len(hechos),hechos)
