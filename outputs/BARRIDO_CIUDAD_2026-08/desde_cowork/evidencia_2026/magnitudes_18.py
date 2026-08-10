# -*- coding: utf-8 -*-
"""Para los polos que todavia no tienen perimetro propio, mide la masa gastronomica
concentrada DENTRO DEL BARRIO que los contiene. No es el perimetro del polo."""
import geopandas as gpd, csv, io
BASE='/mnt/user-data/uploads/DataGastro/outputs/BARRIDO_CIUDAD_2026-08'
CRS=5347
zon=gpd.read_file(f'{BASE}/geometria_r7/zonas_r8.geojson').to_crs(CRS)
con=gpd.read_file(f'{BASE}/borrador_polos/polos_publicables.geojson').to_crs(CRS)
crit=list(csv.DictReader(open('criterio_admision_55.csv',encoding='utf-8')))
adm={r['polo_id']:r for r in crit if r['categoria_por_criterio']=='polo admitido'}
z=zon.set_index('zona_id')
SUR={'Z50':'S_BARRACAS','Z51':'S_BARRACAS','Z52':'S_LABOCA','Z53':'S_LABOCA','Z54':'Z40'}
objetivo=[]
for pid,r in adm.items():
    if pid in SUR: cont=SUR[pid]
    elif pid in z.index and str(z.loc[pid,'detalle_geometria']).startswith('polígono administrativo'): cont=pid
    else: continue
    objetivo.append((pid, r['nombre'], cont))
con['ha_c']=con.geometry.area/10000.0
filas=[]
for pid,nombre,cont in objetivo:
    g=z.loc[cont,'geometry']
    inter=con.geometry.intersection(g).area
    frac=inter/con.geometry.area
    sel=con[frac>0.5]
    filas.append(dict(polo_id=pid, nombre=nombre, contenedor=cont,
        contenedor_nombre=str(z.loc[cont,'nombre']),
        ha_del_contenedor=round(g.area/10000,2),
        n_concentraciones=len(sel),
        concentraciones=' '.join(sorted(sel.polo_id)),
        locales_en_concentraciones=int(sel.n_locales.sum()),
        ha_en_concentraciones=round(float(sel.ha_c.sum()),2),
        pct_del_barrio_concentrado=round(100*float(sel.ha_c.sum())/(g.area/10000),1),
        criterio='concentración con más del 50 % de su superficie dentro del contenedor'))
filas.sort(key=lambda r:-r['locales_en_concentraciones'])
cols=list(filas[0].keys())
with io.open('magnitudes_sin_perimetro.csv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(filas)
print(f"{'polo':<7}{'nombre':<34}{'conc':>5}{'locales':>9}{'ha conc':>9}{'ha barrio':>11}{'% conc':>8}")
print('-'*84)
tot_l=tot_h=0
for r in filas:
    print(f"{r['polo_id']:<7}{r['nombre'][:33]:<34}{r['n_concentraciones']:>5}{r['locales_en_concentraciones']:>9}"
          f"{r['ha_en_concentraciones']:>9.1f}{r['ha_del_contenedor']:>11.1f}{r['pct_del_barrio_concentrado']:>7.1f}%")
    tot_l+=r['locales_en_concentraciones']; tot_h+=r['ha_en_concentraciones']
print('-'*84)
print(f"{'TOTAL':<41}{sum(r['n_concentraciones'] for r in filas):>5}{tot_l:>9}{tot_h:>9.1f}")
print("\nOJO: S_BARRACAS y S_LABOCA y Z40 se repiten como contenedor de dos polos; el total de arriba los cuenta dos veces.")
únicos={r['contenedor'] for r in filas}
print("contenedores únicos:", len(únicos))
