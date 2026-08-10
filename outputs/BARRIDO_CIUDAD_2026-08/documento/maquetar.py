# -*- coding: utf-8 -*-
import io, os, re, base64, markdown
BUILD='/home/claude/out/build'
md=io.open(f'{BUILD}/ATLAS_V3_DOCUMENTO.md',encoding='utf-8').read()
MARCA='# Resumen'
cuerpo = MARCA + md.split(MARCA,1)[1]

lines=cuerpo.split('\n'); out=[]; first=True
for ln in lines:
    if re.match(r'^# ', ln):
        if first: first=False
        else: out.append('<div class="pb"></div>')
    out.append(ln)
cuerpo='\n'.join(out)
html_body=markdown.markdown(cuerpo, extensions=['tables','attr_list','sane_lists','md_in_html'])

def b64(p):
    return base64.b64encode(open(os.path.join(BUILD,p),'rb').read()).decode()
def emb(m):
    p=os.path.join(BUILD,m.group(2))
    if not os.path.exists(p): return m.group(0)
    return f'<img alt="{m.group(1)}" src="data:image/png;base64,{b64(m.group(2))}">'
html_body=re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', emb, html_body)

TAPA=f"""
<section class="tapa">
  <div class="tapa-marca">Dirección General de Desarrollo Gastronómico<br>
    <span>Ministerio de Desarrollo Económico · Gobierno de la Ciudad de Buenos Aires</span></div>
  <div class="tapa-centro">
    <div class="tapa-linea"></div>
    <h1 class="tapa-tit">Atlas de Referencias<br>Gastronómicas</h1>
    <div class="tapa-sub">de la Ciudad de Buenos Aires</div>
    <div class="tapa-ver">Versión 3 · agosto de 2026</div>
  </div>
  <div class="tapa-pie">
    <p><strong>Documento en edición.</strong> El relevamiento está cerrado y el texto está escrito.
    Lo que está en curso es la edición: el trazado de los perímetros que faltan y el armado final.
    <strong>Cada cifra lleva su fuente y su fecha, y cada cosa que falta está declarada donde falta.</strong></p>
  </div>
</section>
<div class="pb"></div>
<section class="portadilla">
  <h2 class="pt-h">El atlas en seis cifras</h2>
  <table class="cifras">
   <tr><td class="n">23.981</td><td>locales gastronómicos relevados en toda la Ciudad</td></tr>
   <tr><td class="n">41</td><td>polos gastronómicos, en catorce de las quince comunas</td></tr>
   <tr><td class="n">55</td><td>lugares estudiados con la misma regla, sin excepción para los que ya estaban</td></tr>
   <tr><td class="n">12.688</td><td>locales en las 124 concentraciones medidas · el 53 % de la gastronomía de la Ciudad en el 15 % de su superficie</td></tr>
   <tr><td class="n">90</td><td>bares notables de la Ciudad, y 88 abiertos</td></tr>
   <tr><td class="n">15</td><td>lugares donde cocina una colectividad, con sus calles</td></tr>
  </table>
</section>
<div class="pb"></div>
<section class="mapa-pagina">
  <img class="mapa-tapa" src="data:image/png;base64,{b64('cartografia/mapa_general.png')}">
</section>
<div class="pb"></div>
<section class="indice">
  <h2 class="pt-h">Índice</h2>
  <table class="idx">
   <tr><td class="r">—</td><td><strong>Resumen ejecutivo</strong></td></tr>
   <tr><td class="r">I</td><td>Presentación</td></tr>
   <tr><td class="r">II</td><td>Qué es un polo gastronómico, y con qué criterio entra</td></tr>
   <tr><td class="r">III</td><td>De dónde salen los datos</td></tr>
   <tr><td class="r">IV</td><td>Cómo se leyó el territorio</td></tr>
   <tr><td class="r">V</td><td>Los referentes de la Ciudad</td></tr>
   <tr><td class="r">VI</td><td>Las comunidades y el territorio</td></tr>
   <tr><td class="r">VII</td><td><strong>La Ciudad, comuna por comuna</strong> — los 41 polos</td></tr>
   <tr><td class="r">VIII</td><td>Las zonas que se midieron y quedaron fuera del criterio</td></tr>
   <tr><td class="r">IX</td><td>El alcance de este atlas</td></tr>
   <tr><td class="r">A</td><td>Anexo · El criterio de admisión y permanencia, completo</td></tr>
   <tr><td class="r">B</td><td>Anexo · Las 124 concentraciones detectadas</td></tr>
   <tr><td class="r">C</td><td>Anexo · Correspondencia, glosario, fuentes y licencias</td></tr>
  </table>
  <p class="idx-nota"><strong>Quien tenga apuro puede leer la II y la IX, y después ir directo a su
  comuna.</strong> La II explica qué se está mirando; la IX, qué no se puede concluir de lo que se ve.</p>
</section>
<div class="pb"></div>
"""

CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family:"DejaVu Serif",Georgia,serif; font-size:9.6pt; line-height:1.52; color:#22201d;
       margin:0; hyphens:auto; text-align:justify; }
h1,h2,h3,h4 { font-family:"DejaVu Sans",Helvetica,sans-serif; color:#1a1714; text-align:left; line-height:1.2; }
h1 { font-size:20pt; margin:0 0 13pt 0; padding-bottom:6pt; border-bottom:2.2pt solid #b0402d; letter-spacing:-.2pt; }
h2 { font-size:13.2pt; margin:19pt 0 7pt 0; color:#7d2417; }
h3 { font-size:10.8pt; margin:15pt 0 5pt 0; border-left:3pt solid #b0402d; padding-left:7pt; }
h4 { font-size:9.7pt; margin:11pt 0 4pt 0; color:#4b453f; }
p { margin:0 0 6.5pt 0; }
strong { color:#151311; } em { color:#3d3833; }
blockquote { margin:9pt 0; padding:7pt 11pt; background:#faf6f1; border-left:2.6pt solid #c98f7f; font-size:9.2pt; }
blockquote p:last-child { margin-bottom:0; }
table { border-collapse:collapse; width:100%; margin:9pt 0; font-size:8.3pt;
        font-family:"DejaVu Sans",sans-serif; page-break-inside:avoid; }
th { background:#f2ece5; text-align:left; font-weight:600; color:#4b453f; }
th,td { border:0.5pt solid #e2dbd2; padding:3.6pt 5pt; vertical-align:top; text-align:left; }
tr:nth-child(even) td { background:#fbf9f6; }
img { max-width:100%; height:auto; display:block; margin:10pt auto; page-break-inside:avoid; }
hr { border:none; border-top:0.6pt solid #e2dbd2; margin:14pt 0; }
ul,ol { margin:0 0 7pt 0; padding-left:15pt; } li { margin-bottom:2.6pt; }
code { font-family:"DejaVu Sans Mono",monospace; font-size:8.4pt; background:#f4f1ec; padding:0 2pt; }
.pb { page-break-before:always; }
h1,h2,h3 { page-break-after:avoid; }

/* --- tapa --- */
.tapa { height:246mm; display:flex; flex-direction:column; justify-content:space-between; text-align:left; }
.tapa-marca { font-family:"DejaVu Sans",sans-serif; font-size:9pt; color:#7d2417; font-weight:600; line-height:1.5; }
.tapa-marca span { color:#8a8078; font-weight:400; font-size:8pt; }
.tapa-centro { margin-top:-22mm; }
.tapa-linea { width:56mm; height:3.2pt; background:#b0402d; margin-bottom:11mm; }
.tapa-tit { font-size:35pt; line-height:1.06; margin:0; border:none; padding:0; letter-spacing:-1pt; color:#1a1714; }
.tapa-sub { font-family:"DejaVu Sans",sans-serif; font-size:16pt; color:#4b453f; margin-top:5mm; letter-spacing:-.3pt; }
.tapa-ver { font-family:"DejaVu Sans",sans-serif; font-size:11pt; color:#7d2417; margin-top:13mm; font-weight:600; }
.tapa-pie { border-top:0.8pt solid #e2dbd2; padding-top:5mm; font-size:8.6pt; color:#4b453f; }
.tapa-pie p { margin:0; }
.pt-h { margin-top:0; font-size:14pt; color:#7d2417; }
.cifras td { border:none; border-bottom:0.5pt solid #ece5dc; padding:5.5pt 4pt; font-size:9.2pt;
             font-family:"DejaVu Serif",serif; background:none !important; }
.cifras td.n { font-family:"DejaVu Sans",sans-serif; font-weight:700; font-size:12pt; color:#b0402d;
               width:26mm; white-space:nowrap; }
.mapa-pagina { height:245mm; display:flex; align-items:center; justify-content:center; }
.mapa-tapa { max-height:243mm; width:auto; margin:0 auto; }
.idx td { border:none; border-bottom:0.5pt solid #ece5dc; padding:5pt 4pt; font-size:9.4pt;
          font-family:"DejaVu Serif",serif; background:none !important; }
.idx td.r { font-family:"DejaVu Sans",sans-serif; font-weight:700; color:#b0402d; width:14mm; }
.idx-nota { margin-top:8mm; font-size:9pt; color:#4b453f; }
"""
html=f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · V3</title>
<style>{CSS}</style></head><body>{TAPA}{html_body}</body></html>"""
io.open(f'{BUILD}/atlas.html','w',encoding='utf-8').write(html)

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file://'+f'{BUILD}/atlas.html', wait_until='networkidle')
    pg.pdf(path='/home/claude/out/Atlas_V3_agosto_2026.pdf', format='A4', print_background=True,
           margin={'top':'20mm','bottom':'18mm','left':'18mm','right':'18mm'},
           display_header_footer=True, header_template='<div></div>',
           footer_template='<div style="width:100%;font-family:DejaVu Sans,sans-serif;font-size:7pt;'
                'color:#8a8078;padding:0 18mm;display:flex;justify-content:space-between;">'
                '<span>Atlas de Referencias Gastronómicas de la Ciudad de Buenos Aires · V3 · agosto de 2026</span>'
                '<span class="pageNumber"></span></div>')
    b.close()
print('PDF:', round(os.path.getsize('/home/claude/out/Atlas_V3_agosto_2026.pdf')/1e6,2),'MB')
