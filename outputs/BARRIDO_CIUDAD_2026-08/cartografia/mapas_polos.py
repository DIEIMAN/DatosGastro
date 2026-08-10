# -*- coding: utf-8 -*-
"""Un mapa chico por polo, para que la unidad de lectura sea el polo y no la comuna."""
import geopandas as gpd, csv, re, os, io, unicodedata, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
INS='/home/claude/out/insumos'; OUT='/home/claude/out/mapas/polos'
os.makedirs(OUT, exist_ok=True); CRS=5347

# ---------- las mismas formas y familias que el mapa general ----------
src=io.open('/home/claude/out/mapa_general.py',encoding='utf-8').read()
exec(src.split("P=gpd.GeoDataFrame(rows")[0])
P=gpd.GeoDataFrame(rows,crs=f'EPSG:{CRS}')
P['familia']=[familia(r.nombre,r.geometry) for r in P.itertuples()]
ACENTO={'Nunez':'Núñez','Villa Ortuzar':'Villa Ortúzar','Garcia del Rio':'García del Río',
        'Donado-Holmberg':'Donado–Holmberg','Nueva Pompeya · eje Av. Saenz':'Nueva Pompeya · eje Av. Sáenz',
        'Centro y Microcentro':'Microcentro'}
P['nombre']=P['nombre'].map(lambda x: ACENTO.get(x,x))

COL={'nucleo':'#1F6FB2','corredor':'#E08A1E','piezas':'#12897B','disperso':'#8E5AA8'}
OSC={'nucleo':'#0F4470','corredor':'#9A5A08','piezas':'#075A51','disperso':'#5B3270'}
ETQ={'nucleo':'núcleo compacto','corredor':'corredor sobre una avenida',
     'piezas':'varias piezas bajo un mismo nombre','disperso':'oferta repartida'}
BORDE={'si':'borde dibujado','pieza':'borde a medias','no':'sin borde · se muestra el barrio'}

def slug(s):
    s=unicodedata.normalize('NFD',s)
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    return re.sub(r'[^a-z0-9]+','_',s).strip('_')[:44]

ciudad=com.geometry.union_all()
hecho=[]
for r in P.itertuples():
    g=r.geometry
    x0,y0,x1,y1=g.bounds
    w,h=x1-x0,y1-y0
    lado=max(w,h,700)*1.45                       # cuadro cuadrado con aire
    cx,cy=(x0+x1)/2,(y0+y1)/2
    x0,x1=cx-lado/2,cx+lado/2; y0,y1=cy-lado/2,cy+lado/2

    fig,ax=plt.subplots(figsize=(5.6,5.0),dpi=190)
    com.plot(ax=ax,facecolor='#fbfaf8',edgecolor='#cfc8bf',linewidth=1.0,zorder=0)
    bar.plot(ax=ax,facecolor='none',edgecolor='#ded8d0',linewidth=0.6,zorder=1)
    con.cx[x0:x1,y0:y1].plot(ax=ax,facecolor='#efece6',edgecolor='#e0dbd2',linewidth=0.3,zorder=2)
    otros=P[P.pid!=r.pid]
    otros.cx[x0:x1,y0:y1].plot(ax=ax,facecolor='#ddd6d0',edgecolor='#c3b9b0',linewidth=0.5,alpha=.85,zorder=3)
    gs=gpd.GeoSeries([g],crs=P.crs)
    if r.borde=='no':
        gs.plot(ax=ax,facecolor=COL[r.familia],edgecolor=OSC[r.familia],linewidth=1.1,alpha=.20,hatch='///',zorder=4)
    elif r.borde=='pieza':
        gs.plot(ax=ax,facecolor=COL[r.familia],edgecolor=OSC[r.familia],linewidth=1.2,alpha=.62,
                linestyle=(0,(2.6,1.4)),zorder=4)
    else:
        gs.plot(ax=ax,facecolor=COL[r.familia],edgecolor=OSC[r.familia],linewidth=0.9,alpha=.88,zorder=4)
    hh=hit.cx[x0:x1,y0:y1]
    if len(hh): hh.plot(ax=ax,color='#20262e',markersize=11,zorder=6,alpha=.9)

    # nombres de los barrios que el cuadro toca
    for b in bar.cx[x0:x1,y0:y1].itertuples():
        c=b.geometry.intersection(gpd.GeoSeries([g],crs=P.crs).total_bounds is not None and b.geometry)
        p=b.geometry.representative_point()
        if x0<p.x<x1 and y0<p.y<y1:
            ax.annotate(str(b.BARRIO).title(),(p.x,p.y),fontsize=5.6,ha='center',va='center',
                        color='#9a9188',zorder=5,
                        path_effects=[pe.withStroke(linewidth=2.0,foreground='white')])

    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect('equal'); ax.set_axis_off()
    esc=200 if lado<1800 else (500 if lado<5000 else 1000)
    sx=x0+lado*0.06; sy=y0+lado*0.06
    ax.plot([sx,sx+esc],[sy,sy],color='#20262e',lw=2,solid_capstyle='butt',zorder=8)
    ax.text(sx+esc/2,sy+lado*0.018,f'{esc} m' if esc<1000 else '1 km',
            ha='center',fontsize=6,color='#20262e')

    # localizador: la Ciudad entera con el polo marcado
    ins=fig.add_axes([0.755,0.055,0.20,0.20])
    gpd.GeoSeries([ciudad],crs=P.crs).plot(ax=ins,facecolor='#f2efeb',edgecolor='#cfc8bf',linewidth=0.5)
    ins.plot([cx],[cy],marker='o',ms=4,color=OSC[r.familia])
    ins.set_axis_off(); ins.set_aspect('equal')

    ax.set_title(r.nombre,fontsize=10.5,loc='left',color='#16202b',pad=3)
    ax.text(0,1.012,f'{ETQ[r.familia]} · {BORDE[r.borde]}',transform=ax.transAxes,
            fontsize=6.6,color='#5b5148',va='bottom')
    f=f'{OUT}/{slug(r.nombre)}.png'
    plt.savefig(f,bbox_inches='tight',facecolor='white',pad_inches=0.12); plt.close()
    hecho.append((r.nombre,os.path.basename(f)))

w=csv.writer(io.open('/home/claude/out/mapas_polos.csv','w',newline='',encoding='utf-8'))
w.writerow(['nombre','archivo']); [w.writerow(x) for x in hecho]
print('mapas por polo:',len(hecho))
