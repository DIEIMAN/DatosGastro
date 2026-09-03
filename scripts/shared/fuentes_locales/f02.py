"""Lector unico de F02 (habilitaciones aprobadas, AGC / datos abiertos GCBA).

F02 no tiene un esquema unico: los ocho archivos crudos difieren en delimitador,
codificacion y nombres de columna. Un lector escrito contra un solo anio lee ese anio
y devuelve cero (o basura) para el resto. Este modulo resuelve las tres diferencias en
un solo lugar.

Lo medido sobre los archivos de `data/raw` (2026-08-27):

  archivo        delimitador  codificacion  esquema   nomenclatura de rubro
  2015_2018      ";"          utf-8         legacy    descripcion_rubro (mayusculas)
  2019           ";"          utf-8         legacy    descripcion_rubro
  2020           ";"          utf-8         legacy    DescripcionRubro + DescripcionSubRubro
  2021           ";"          utf-8         legacy    idem (con columnas "Unnamed" de cola)
  2022           ";"          utf-8 (*)     legacy    idem
  2023           ";"          utf-8         legacy    idem, codigo_rubro tipo "1.4.2"
  2024           ";"          cp1252        legacy    idem
  2025           ","          utf-8         moderno   rubro / razon_social / domicilio

  (*) 2022 ademas trae doble codificacion adentro del propio archivo; se repara al
      leer (ver texto.reparar_mojibake).

Dos errores que este modulo existe para no repetir:

  1. Leer todo con delimitador "," (el lector heredado de casas_pastas): los siete
     archivos legacy caian como una sola columna y aportaban CERO filas. El estudio
     quedaba midiendo solo 2025.
  2. Leer todo lo legacy con latin-1: siete de los ocho archivos son UTF-8, y leerlos
     como latin-1 rompe los acentos justo en la nomenclatura moderna
     ("ELABORACION DE PRODUCTOS DE PANADERIA" con tilde). Sobre el conjunto crudo, la
     lectura equivocada pierde alrededor del 70 % de las filas con rubro de pan o pasta.

Privacidad (guardrail 7): el esquema legacy trae `titulares` y `cuits`, y el moderno
trae `telefono` y `cod_postal_titular`. Este lector NO expone ninguno de esos campos:
se descartan en el parseo y no hay forma de pedirlos desde la API publica del modulo.
Las filas legacy quedan, por lo tanto, sin nombre de establecimiento; se identifican
por partida matriz y domicilio.

Guardrail 5: lo que sale de aca son HABILITACIONES, no "locales activos".
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

from .texto import clave_columna, reparar_mojibake

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PATRON_F02 = "f02_habilitaciones_aprobadas_*.csv"

# Columnas que no se leen nunca: datos personales (guardrail 7).
COLUMNAS_PROHIBIDAS = {"titulares", "cuits", "cuit", "telefono", "codpostaltitular", "email"}

# F02 desnormalizado puede traer filas larguisimas (campo `calles` con muchas entradas).
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


@dataclass(frozen=True)
class DialectoF02:
    """Como se abre un archivo F02 concreto."""
    path: Path
    delimitador: str
    codificacion: str
    esquema: str  # "legacy" | "moderno"
    periodo: str  # "2015_2018", "2019", ... tal como viene del nombre de archivo


@dataclass
class RegistroF02:
    """Una fila de F02, con nombres de campo estables entre anios."""
    archivo_origen: str
    periodo: str
    esquema: str
    id_registro: str = ""          # partida matriz; estable, pero no necesariamente unica
    solicitud: str = ""            # una habilitacion; solo legacy
    unidad_funcional: str = ""     # UF dentro del inmueble; solo legacy, puede venir vacia
    partida_horizontal: str = ""   # partida de la UF; solo legacy
    nombre: str = ""               # solo esquema moderno (razon social); legacy va vacio
    rubro: str = ""
    subrubro: str = ""
    codigo_rubro: str = ""
    descripcion: str = ""          # comentarios / observaciones publicas
    domicilio: str = ""
    comuna: str = ""
    superficie: str = ""
    fecha_habilitacion: str = ""   # tal como viene
    anio_habilitacion: str = ""    # 4 digitos, derivado
    disposicion: str = ""
    crudo: dict = field(default_factory=dict, repr=False)

    @property
    def clave_habilitacion(self) -> str:
        """Identificador del LOCAL habilitado, no del inmueble.

        `id_registro` (partida matriz) identifica la parcela: el 51 % de los inmuebles del
        universo de panaderias aloja mas de una habilitacion, asi que agrupar por partida
        fusiona locales distintos de un mismo edificio. La solicitud es una habilitacion, y
        la unidad funcional la desagrega cuando el tramite cubre varias UF.

        El esquema moderno no publica la solicitud, pero publica la `disposicion`, que es
        el acto que aprueba la habilitacion y cumple el mismo papel: en el archivo 2025 hay
        3.500 disposiciones sobre 2.947 partidas, o sea que contar por partida sub-cuenta
        tambien ahi. Queda vacia en las filas modernas sin disposicion (el 4,7 %), que
        tienen que caer a partida + nombre.

        Sin unidad funcional no se inventa una: la UF viene vacia en el 47 % de las filas
        legacy, y agregarla como "" a la clave equivaldria a agrupar por solicitud sola,
        que es lo que ya hace esta rama.
        """
        base = self.solicitud or self.disposicion
        if not base:
            return ""
        return f"{base}/{self.unidad_funcional}" if self.unidad_funcional else base

    @property
    def rubro_completo(self) -> str:
        """Rubro + subrubro, que es el texto contra el que clasifica cada rubro."""
        return " ".join(x for x in (self.rubro, self.subrubro) if x).strip()

    @property
    def texto_clasificable(self) -> str:
        """Todo el texto no personal utilizable por un clasificador de rubro."""
        return " ".join(x for x in (self.rubro_completo, self.nombre, self.descripcion) if x).strip()


# ---------------------------------------------------------------------------------------
# Deteccion de dialecto
# ---------------------------------------------------------------------------------------
def _leer_encabezado(path: Path) -> tuple[bytes, str]:
    with open(path, "rb") as fh:
        crudo = fh.readline()
    sin_bom = crudo.removeprefix(b"\xef\xbb\xbf")  # el BOM ensuciaba el primer encabezado
    return crudo, sin_bom.decode("latin-1", errors="replace")


def _detectar_codificacion(path: Path) -> str:
    """utf-8-sig si el archivo entero decodifica; cp1252 si no (caso 2024)."""
    try:
        with open(path, encoding="utf-8-sig", errors="strict") as fh:
            while fh.read(1 << 20):
                pass
        return "utf-8-sig"
    except UnicodeDecodeError:
        return "cp1252"


@lru_cache(maxsize=128)
def _detectar_dialecto_cache(path_texto: str, size: int, mtime_ns: int) -> DialectoF02:
    """Detecta una vez por version fisica del archivo.

    ``size`` y ``mtime_ns`` forman parte de la clave para no conservar una deteccion
    vieja si una descarga oficial se reemplaza durante el mismo proceso.
    """
    del size, mtime_ns
    path = Path(path_texto)
    _, encabezado = _leer_encabezado(path)
    delimitador = ";" if encabezado.count(";") > encabezado.count(",") else ","
    claves = {clave_columna(c) for c in encabezado.split(delimitador)}
    esquema = "moderno" if "razonsocial" in claves else "legacy"
    periodo = path.stem.replace("f02_habilitaciones_aprobadas_", "")
    return DialectoF02(path, delimitador, _detectar_codificacion(path), esquema, periodo)


def detectar_dialecto(path: str | Path) -> DialectoF02:
    path = Path(path).resolve()
    stat = path.stat()
    return _detectar_dialecto_cache(str(path), stat.st_size, stat.st_mtime_ns)


def listar_archivos_f02(raw: str | Path | None = None) -> list[Path]:
    return sorted(Path(raw or RAW).glob(PATRON_F02))


# ---------------------------------------------------------------------------------------
# Parseo de filas
# ---------------------------------------------------------------------------------------
_ANIO = re.compile(r"(?:19|20)\d{2}")


def _anio(*textos: str) -> str:
    for texto in textos:
        if not texto:
            continue
        m = re.search(r"DI-((?:19|20)\d{2})", texto)
        if m:
            return m.group(1)
        m = _ANIO.search(texto)
        if m:
            return m.group(0)
    return ""


def _fila_canonica(fila: dict) -> dict:
    """Reindexa la fila por clave canonica y descarta las columnas personales."""
    salida = {}
    for k, v in fila.items():
        if not k:
            continue
        clave = clave_columna(k)
        if clave in COLUMNAS_PROHIBIDAS or clave.startswith("unnamed") or not clave:
            continue
        if isinstance(v, list):  # cola de campos extra (delimitadores sueltos en la fila)
            v = " ".join(str(x) for x in v if x)
        salida[clave] = reparar_mojibake(str(v or "")).strip()
    return salida


def _tomar(fila: dict, *claves: str) -> str:
    for clave in claves:
        valor = fila.get(clave_columna(clave), "")
        if valor:
            return valor
    return ""


def _codigo_uf(valor: str) -> str:
    """Normaliza un codigo de unidad funcional / partida horizontal.

    Acepta "0001" y "0001;0002" (un tramite sobre dos UF); descarta cualquier valor con
    letras, que en 2021 es texto de rubro caido en la columna por el corrimiento de campos.
    Los ceros a la izquierda se sacan para que "0001" y "1" sean la misma UF entre anios, y
    la lista se ordena y se deduplica: el archivo repite el mismo codigo por cada parcela
    de la habilitacion ("1;1"), y sin normalizar eso serian dos claves distintas.
    """
    partes = {x.strip().lstrip("0") or "0" for x in valor.split(";") if x.strip().isdigit()}
    return ";".join(sorted(partes, key=int))


# Una direccion completa: nombre de calle en mayusculas y altura. "GAONA AV. 3756".
_DIRECCION_COMPLETA = re.compile(r"^[^\d;]{3,60}\s\d{1,5}[A-Za-z]?$")
# Cola de una direccion partida: nombre de pila o continuacion, seguido de altura.
# "  JERONIMO 188", " JUAN AGUSTIN 4196".
_COLA_DIRECCION = re.compile(r"^[^\d;]{2,40}\s\d{1,5}[A-Za-z]?$")


def _reparar_domicilio_partido(fila_original: dict, domicilio: str) -> str:
    """Recompone las direcciones que el archivo 2021 rompe al escribir sin comillas.

    En 2021 los campos van sin comillas y varios contienen ";" adentro, asi que el CSV
    los parte y corre todas las columnas siguientes. Pasan dos cosas distintas:

    1. Las calles con apellido y nombre se escriben "SALGUERO; JERONIMO 188": la calle
       queda sin altura y la cola cae en la columna de al lado.
    2. El rubro de pizzeria es "Com. min. elab. y vta. Pizza; fuga-zza; faina;
       empanadas; postres; flanes; churros; grill" — ocho campos. Eso corre la fila
       siete posiciones y la direccion termina en una columna sin nombre. Son 498 filas
       de 2021, y son justamente pizzerias.

    En total 2.675 filas del archivo (el 9,1 %) quedan con la calle sin altura y por lo
    tanto sin geocodificar. Se recuperan por forma, no por posicion: primero la cola
    pegada al lado, y si no, la primera direccion completa que aparezca en el resto de
    la fila.

    Guardrail 7: solo se aceptan valores con forma de direccion (terminan en altura).
    Un nombre de persona no tiene altura y una razon social tampoco; un CUIT no tiene
    letras. Nada de eso matchea, no se conserva y no se lee para ninguna otra cosa.
    """
    if not domicilio or re.search(r"\d", domicilio):
        return domicilio

    valores = [(clave_columna(k) if k else "", v) for k, v in fila_original.items()]
    posterior = []
    visto_calles = False
    for clave, v in valores:
        if visto_calles:
            if isinstance(v, list):
                posterior.extend(str(x) for x in v)
            else:
                posterior.append(str(v or ""))
        elif clave == "calles":
            visto_calles = True
    posterior = [reparar_mojibake(x).strip() for x in posterior]

    if posterior and _COLA_DIRECCION.match(posterior[0]):
        return f"{domicilio} {posterior[0]}"
    for candidato in posterior:
        if _DIRECCION_COMPLETA.match(candidato) and sum(c.isalpha() for c in candidato) >= 3:
            return candidato
    return domicilio


def _a_registro(fila: dict, dial: DialectoF02) -> RegistroF02:
    can = _fila_canonica(fila)
    if dial.esquema == "moderno":
        disposicion = _tomar(can, "disposicion")
        rubro = _tomar(can, "rubro")
        return RegistroF02(
            archivo_origen=dial.path.name,
            periodo=dial.periodo,
            esquema=dial.esquema,
            id_registro=_tomar(can, "nropartidamatriz", "partida_matriz"),
            nombre=_tomar(can, "razon_social"),
            rubro=rubro,
            codigo_rubro=_tomar(can, "codigo_rubro"),
            descripcion=_tomar(can, "comentarios"),
            domicilio=_tomar(can, "domicilio"),
            comuna=_tomar(can, "comuna"),
            disposicion=disposicion,
            anio_habilitacion=_anio(disposicion),
            crudo=can,
        )

    fecha = _tomar(can, "fecha_habilitacion")
    # La partida matriz legacy es numerica, y una habilitacion sobre dos parcelas la trae
    # como "291211;291212": se toma la primera. En cambio, en las filas corridas de 2021
    # esta columna recibe basura del rubro (" flanes"), que no es un identificador.
    partida = _tomar(can, "partida_matriz").split(";")[0].strip()
    if not partida.isdigit():
        partida = ""
    # `unidad_funcional` y `partida_horizontal` desagregan el inmueble en locales. Traen
    # dos formas legitimas ("0001", y "0001;0002" cuando el tramite cubre dos UF) y una
    # ilegitima: en las filas corridas de 2021 la columna recibe texto del rubro
    # ("BOTONERIA", "churros"), que no identifica nada. Se acepta solo lo numerico.
    unidad = _codigo_uf(_tomar(can, "unidad_funcional"))
    horizontal = _codigo_uf(_tomar(can, "partida_horizontal"))
    # `calles` puede traer varias entradas separadas por ";": la primera es la puerta.
    domicilio = _tomar(can, "calles").split(";")[0].strip()
    domicilio = _reparar_domicilio_partido(fila, domicilio)
    return RegistroF02(
        archivo_origen=dial.path.name,
        periodo=dial.periodo,
        esquema=dial.esquema,
        id_registro=partida,
        solicitud=_tomar(can, "solicitud"),
        unidad_funcional=unidad,
        partida_horizontal=horizontal,
        nombre="",  # titulares no se leen: dato personal
        rubro=_tomar(can, "descripcion_rubro"),
        subrubro=_tomar(can, "descripcion_sub_rubro"),
        codigo_rubro=_tomar(can, "codigo_rubro"),
        domicilio=domicilio,
        superficie=_tomar(can, "superficie"),
        fecha_habilitacion=fecha,
        anio_habilitacion=_anio(fecha),
        crudo=can,
    )


# ---------------------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------------------
def iter_f02(
    archivos: Sequence[str | Path] | None = None,
    *,
    raw: str | Path | None = None,
    filtro: Callable[[RegistroF02], bool] | None = None,
    incluir_crudo: bool = False,
) -> Iterator[RegistroF02]:
    """Recorre TODOS los archivos F02 disponibles, cada uno con su dialecto.

    `filtro` se aplica sobre el registro ya normalizado; usarlo evita materializar
    cientos de miles de filas cuando el estudio solo quiere las de un rubro.
    `incluir_crudo=False` (por defecto) libera el dict de la fila original, que es lo
    que hace que recorrer los ocho archivos no se coma la memoria.
    """
    rutas = [Path(a) for a in archivos] if archivos else listar_archivos_f02(raw)
    for ruta in rutas:
        dial = detectar_dialecto(ruta)
        with open(ruta, encoding=dial.codificacion, errors="replace", newline="") as fh:
            for fila in csv.DictReader(fh, delimiter=dial.delimitador):
                reg = _a_registro(fila, dial)
                if not incluir_crudo:
                    reg.crudo = {}
                if filtro is None or filtro(reg):
                    yield reg


def perfilar_f02(raw: str | Path | None = None) -> list[dict]:
    """Diagnostico por archivo: dialecto, filas leidas y cobertura de campos clave.

    Sirve de control de regresion: si un archivo nuevo entra con otro esquema y el
    lector no lo entiende, aca se ve como filas=0 o como rubro vacio, en vez de
    aparecer como "el rubro no existia ese anio".
    """
    perfil = []
    for ruta in listar_archivos_f02(raw):
        dial = detectar_dialecto(ruta)
        filas = con_rubro = con_domicilio = con_id = con_anio = 0
        anios = set()
        for reg in iter_f02([ruta]):
            filas += 1
            con_rubro += bool(reg.rubro_completo)
            con_domicilio += bool(reg.domicilio)
            con_id += bool(reg.id_registro)
            con_anio += bool(reg.anio_habilitacion)
            if reg.anio_habilitacion:
                anios.add(int(reg.anio_habilitacion))
        nominales = [int(x) for x in re.findall(r"(?:19|20)\d{2}", dial.periodo)]
        if len(nominales) == 2:
            esperados = set(range(min(nominales), max(nominales) + 1))
        else:
            esperados = set(nominales)
        periodo_coherente = bool(anios & esperados) if esperados else None
        perfil.append({
            "archivo": ruta.name,
            "periodo": dial.periodo,
            "esquema": dial.esquema,
            "delimitador": dial.delimitador,
            "codificacion": dial.codificacion,
            "filas": filas,
            "con_rubro": con_rubro,
            "con_domicilio": con_domicilio,
            "con_partida_matriz": con_id,
            "con_anio": con_anio,
            "anio_min": min(anios) if anios else "",
            "anio_max": max(anios) if anios else "",
            "anios_detectados": ",".join(str(x) for x in sorted(anios)),
            "periodo_coherente": periodo_coherente,
        })
    return perfil


def _cli(argv: Iterable[str]) -> int:
    import json
    perfil = perfilar_f02()
    if "--json" in argv:
        print(json.dumps(perfil, ensure_ascii=False, indent=2))
        return 0
    cols = ["archivo", "esquema", "delimitador", "codificacion", "filas", "con_rubro",
            "con_domicilio", "con_partida_matriz", "con_anio", "anio_min", "anio_max",
            "periodo_coherente"]
    anchos = [max(len(c), *(len(str(p[c])) for p in perfil)) for c in cols]
    print("  ".join(c.ljust(a) for c, a in zip(cols, anchos)))
    for p in perfil:
        print("  ".join(str(p[c]).ljust(a) for c, a in zip(cols, anchos)))
    total = sum(p["filas"] for p in perfil)
    print(f"\ntotal filas F02: {total:,}")
    vacios = [p["archivo"] for p in perfil if p["filas"] == 0 or p["con_rubro"] == 0]
    if vacios:
        print("ATENCION, archivos sin filas o sin rubro: " + ", ".join(vacios))
        return 1
    incoherentes = [p["archivo"] for p in perfil if p["periodo_coherente"] is False]
    if incoherentes:
        print("ALERTA, el periodo del nombre no aparece en los datos: " + ", ".join(incoherentes))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
