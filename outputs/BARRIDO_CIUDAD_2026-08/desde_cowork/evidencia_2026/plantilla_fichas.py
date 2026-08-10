# -*- coding: utf-8 -*-
"""Ordena todas las paginas de polo con la misma plantilla y renombra sus bloques.

No inventa contenido: si a una pagina le falta un bloque, lo reporta y sigue.
"""
import io, re, sys

CAN = [
    ('Perímetro',                                   'Dónde está'),
    ('Dónde está',                                  'Dónde está'),
    ('Anclaje normativo',                           'Reconocimiento oficial'),
    ('Reconocimiento oficial',                      'Reconocimiento oficial'),
    ('Por qué es un polo',                          'Por qué es un polo'),
    ('Los establecimientos que vale la pena nombrar','Los establecimientos'),
    ('Los establecimientos',                        'Los establecimientos'),
    ('Los lugares históricos',                      'Los establecimientos'),
    ('Lo que se perdió',                            'Lo que se perdió'),
    ('Contexto comercial',                          'Cómo le va al comercio alrededor'),
    ('Cómo le va al comercio alrededor',            'Cómo le va al comercio alrededor'),
    ('Límites de lectura',                          'Qué no se puede concluir de esta página'),
    ('Qué no se puede concluir de esta página',     'Qué no se puede concluir de esta página'),
    ('Lo que falta',                                'Lo que falta'),
]
ORDEN = ['Dónde está','Reconocimiento oficial','Por qué es un polo','Los establecimientos',
         'Lo que se perdió','Cómo le va al comercio alrededor',
         'Qué no se puede concluir de esta página','Lo que falta']
OBLIG = ['Dónde está','Por qué es un polo','Los establecimientos',
         'Cómo le va al comercio alrededor','Qué no se puede concluir de esta página','Lo que falta']

def etiqueta(ln):
    """Si el renglon abre un bloque canonico, devuelve (nombre_nuevo, resto_del_renglon)."""
    for viejo, nuevo in CAN:
        e = re.escape(viejo)
        m = re.match(r'^\*\*' + e + r'([.:,]?)\*\*(.*)$', ln)
        if m:
            return nuevo, m.group(2)
        m = re.match(r'^\*\*' + e + r'\b(.*?)\*\*(.*)$', ln)          # «**Por qué es un polo — cumple tres**»
        if m:
            return nuevo, (m.group(1) + m.group(2))
        m = re.match(r'^' + e + r'\b([ .—:,].*)$', ln)                 # sin negrita
        if m:
            return nuevo, m.group(1)
    return None, None

def partir(cuerpo):
    """Devuelve (encabezado, [(nombre, renglones)]) de una pagina."""
    enc, bloques, actual, buf = [], [], None, []
    for ln in cuerpo:
        nom, resto = etiqueta(ln)
        if nom:
            if actual: bloques.append((actual, buf))
            else: enc = buf
            actual, buf = nom, [f'**{nom}.**{resto.rstrip()}'.rstrip()]
        else:
            buf.append(ln)
    if actual: bloques.append((actual, buf))
    else: enc = buf
    return enc, bloques

def recomponer(enc, bloques):
    vistos = {}
    for nom, b in bloques:
        vistos.setdefault(nom, []).extend(b + [''])
    out = [l for l in enc]
    while out and not out[-1].strip(): out.pop()
    out.append('')
    for nom in ORDEN:
        if nom in vistos:
            b = vistos[nom]
            while b and not b[-1].strip(): b.pop()
            out.extend(b); out.append('')
    # cualquier bloque que no este en el orden canonico va al final, sin perderse
    for nom in vistos:
        if nom not in ORDEN:
            out.extend(vistos[nom]); out.append('')
    return out

def procesar(path, saltar_titulo):
    L = io.open(path, encoding='utf-8').read().split('\n')
    out, i, tocadas, faltantes = [], 0, 0, []
    while i < len(L):
        m = re.match(r'^# (?!#)(.+)$', L[i])
        if not m or saltar_titulo(m.group(1).strip()):
            out.append(L[i]); i += 1; continue
        titulo = m.group(1).strip()
        j = i + 1
        while j < len(L) and not re.match(r'^# (?!#)', L[j]): j += 1
        enc, bloques = partir(L[i+1:j])
        if bloques:
            out.append(L[i]); out.extend(recomponer(enc, bloques)); tocadas += 1
            hay = {n for n, _ in bloques}
            f = [k for k in OBLIG if k not in hay]
            if f: faltantes.append((titulo, f))
        else:
            out.extend(L[i:j])
        i = j
    io.open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return tocadas, faltantes

SALTAR = lambda t: t.startswith(('Comuna ', 'Sección', 'Lo que sale'))
total, todos = 0, []
for p in ['/home/claude/SECCION_VII_REFERENCIAS_PUBLICADAS.md',
          '/home/claude/SECCION_VII_ZONAS_INCORPORADAS.md',
          '/home/claude/out/FICHAS_SUR_NUEVAS.md']:
    n, f = procesar(p, SALTAR)
    print(f'{n:3d} páginas ordenadas · {p.split("/")[-1]}')
    total += n; todos += f
print(f'\ntotal: {total} páginas con la misma plantilla')
if todos:
    print(f'\npáginas a las que les falta algún bloque obligatorio ({len(todos)}):')
    for t, f in todos: print(f'   {t}: falta {", ".join(f)}')
