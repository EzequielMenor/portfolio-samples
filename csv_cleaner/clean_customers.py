#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Limpia una lista de clientes en CSV y escribe el resultado normalizado.

Solo stdlib (Python 3). Por cada fila aplica:

  1. Trim de espacios en todos los campos y colapso de espacios internos.
  2. Filas completamente vacías → eliminadas.
  3. Nombre → capitalización homogénea ("JUAN  DE LA FUENTE" → "Juan de la Fuente";
     las partículas de/del/la/... van en minúscula salvo en primera posición).
  4. Email → minúsculas y validación con regex. Si el campo trae varios emails
     pegados con comas o punto y coma, se rescata el primero válido. Los
     inválidos se conservan en la salida y se listan en el reporte final.
  5. Teléfono → formato español legible "+34 6XX XXX XXX": descarta letras y
     separadores, pela prefijos internacionales (+34, 0034) y valida 9 dígitos
     empezando por 6-9. Los no válidos se conservan tal cual y se listan.
  6. Ciudad → forma canónica con acentos mediante un mapa de alias
     ("MALAGA" → "Málaga", "la coruna" → "A Coruña"); sin alias, capitalización
     tipo título.
  7. Duplicados → eliminados conservando la primera aparición. Clave: nombre +
     email + dígitos del teléfono + ciudad, normalizados y sin acentos, de modo
     que también se detectan duplicados que solo difieren en el formato.

Al final imprime un resumen estadístico y el reporte de valores inválidos.

Uso:
    python3 clean_customers.py [entrada.csv [salida.csv]]

Sin argumentos lee messy_customers.csv y escribe cleaned_customers.csv,
ambos junto a este script.
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent

# Email: parte local sin puntos dobles ni en los extremos; dominio de etiquetas
# alfanuméricas (guion interior permitido) y TLD de 2 o más letras.
# Se aplica sobre el texto ya pasado a minúsculas.
EMAIL_RE = re.compile(
    r"^[a-z0-9_%+-]+(?:\.[a-z0-9_%+-]+)*"
    r"@[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)*"
    r"\.[a-z]{2,}$"
)

PARTICULAS = {"de", "del", "la", "las", "los", "el", "y", "e", "da", "das", "do", "dos"}

CIUDADES_CANON = [
    "A Coruña", "Albacete", "Alicante", "Almería", "Ávila", "Badajoz",
    "Barcelona", "Bilbao", "Burgos", "Cáceres", "Cádiz", "Castellón", "Ceuta",
    "Ciudad Real", "Córdoba", "Cuenca", "Elche", "Girona", "Granada",
    "Guadalajara", "Huelva", "Jaén", "Las Palmas", "León", "Lleida", "Logroño",
    "Lugo", "Madrid", "Málaga", "Melilla", "Murcia", "Ourense", "Oviedo",
    "Palma de Mallorca", "Pamplona", "Pontevedra", "Salamanca", "San Sebastián",
    "Santa Cruz de Tenerife", "Santander", "Segovia", "Sevilla", "Soria",
    "Tarragona", "Teruel", "Toledo", "Valencia", "Valladolid", "Vitoria",
    "Zaragoza",
]

# Alias habituales → nombre canónico (ampliable según la lista del cliente).
CIUDADES_ALIAS = {
    "la coruna": "A Coruña",
    "la coruña": "A Coruña",
    "coruna": "A Coruña",
    "coruña": "A Coruña",
    "donostia": "San Sebastián",
    "palma": "Palma de Mallorca",
    "vitoria gasteiz": "Vitoria",
    "tenerife": "Santa Cruz de Tenerife",
}


def sin_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def capitalizar(texto):
    """Title case a la española: partículas en minúscula salvo primera palabra."""
    salida = []
    for i, palabra in enumerate(texto.split()):
        baja = palabra.lower()
        salida.append(baja if (i > 0 and baja in PARTICULAS) else baja.capitalize())
    return " ".join(salida)


def construir_mapa_ciudades():
    mapa = {sin_acentos(c).lower(): c for c in CIUDADES_CANON}
    for alias, canon in CIUDADES_ALIAS.items():
        mapa[sin_acentos(alias).lower()] = canon
    return mapa


MAPA_CIUDADES = construir_mapa_ciudades()


def normalizar_nombre(crudo):
    return capitalizar(crudo.strip())


def normalizar_ciudad(crudo):
    limpio = " ".join(crudo.split())
    if not limpio:
        return ""
    clave = sin_acentos(limpio).lower()
    if clave in MAPA_CIUDADES:
        return MAPA_CIUDADES[clave]
    return capitalizar(limpio)


def normalizar_email(crudo):
    """Devuelve (email_limpio, es_valido, fue_rescatado_de_lista)."""
    texto = crudo.strip().lower()
    if not texto:
        return "", False, False
    if EMAIL_RE.match(texto):
        return texto, True, False
    if re.search(r"[,;]", texto):  # varios emails pegados en el mismo campo
        for parte in re.split(r"[,;]+", texto):
            candidato = parte.strip()
            if EMAIL_RE.match(candidato):
                return candidato, True, True
    return texto, False, False


def normalizar_telefono(crudo):
    """Devuelve (telefono_formateado, es_valido).

    Formato de salida: "+34 6XX XXX XXX". Si no es un número español válido
    (9 dígitos empezando por 6-9, con o sin prefijo internacional), devuelve
    el valor original recortado y es_valido=False.
    """
    digitos = "".join(c for c in crudo if c.isdigit())
    if digitos.startswith("00"):
        digitos = digitos[2:]
    if len(digitos) == 11 and digitos.startswith("34"):
        digitos = digitos[2:]
    if len(digitos) == 9 and digitos[0] in "6789":
        return "+34 {} {} {}".format(digitos[:3], digitos[3:6], digitos[6:]), True
    return crudo.strip(), False


def main(argv):
    entrada = Path(argv[1]) if len(argv) > 1 else AQUI / "messy_customers.csv"
    salida = Path(argv[2]) if len(argv) > 2 else AQUI / "cleaned_customers.csv"
    if not entrada.exists():
        print("Error: no existe el archivo de entrada: {}".format(entrada), file=sys.stderr)
        return 2

    filas_entrada = 0
    filas_vacias = 0
    duplicados = 0
    emails_invalidos = []      # (nº de fila en la entrada, valor original)
    telefonos_invalidos = []   # ídem
    emails_rescatados = 0
    telefonos_normalizados = 0
    ciudades_corregidas = 0
    claves_vistas = set()
    filas_salida = []

    with entrada.open(newline="", encoding="utf-8") as f:
        lector = csv.reader(f)
        next(lector, None)  # cabecera
        for numero, fila in enumerate(lector, start=2):  # la cabecera es la fila 1
            filas_entrada += 1
            celdas = list(fila[:4]) + [""] * max(0, 4 - len(fila))
            nombre_crudo, email_crudo, telefono_crudo, ciudad_cruda = celdas
            if not any(c.strip() for c in celdas):
                filas_vacias += 1
                continue

            nombre = normalizar_nombre(nombre_crudo)
            email, email_ok, email_rescatado = normalizar_email(email_crudo)
            telefono, telefono_ok = normalizar_telefono(telefono_crudo)
            ciudad = normalizar_ciudad(ciudad_cruda)

            if email and not email_ok:
                emails_invalidos.append((numero, email_crudo.strip()))
            if email_rescatado:
                emails_rescatados += 1
            if telefono_ok:
                telefonos_normalizados += 1
            elif telefono_crudo.strip():
                telefonos_invalidos.append((numero, telefono_crudo.strip()))
            if ciudad_cruda.strip() and ciudad != " ".join(ciudad_cruda.split()):
                ciudades_corregidas += 1

            digitos_clave = "".join(c for c in telefono if c.isdigit())
            clave = (sin_acentos(nombre).lower(), email, digitos_clave,
                     sin_acentos(ciudad).lower())
            if clave in claves_vistas:
                duplicados += 1
                continue
            claves_vistas.add(clave)
            filas_salida.append([nombre, email, telefono, ciudad])

    with salida.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["nombre", "email", "telefono", "ciudad"])
        escritor.writerows(filas_salida)

    print("Entrada : {}".format(entrada))
    print("Salida  : {}".format(salida))
    print()
    print("=== Resumen de limpieza ===")
    print("Filas de entrada           : {}".format(filas_entrada))
    print("Filas vacías eliminadas    : {}".format(filas_vacias))
    print("Duplicados eliminados      : {}".format(duplicados))
    print("Filas de salida            : {}".format(len(filas_salida)))
    print("Teléfonos normalizados     : {}".format(telefonos_normalizados))
    print("Teléfonos no válidos       : {}".format(len(telefonos_invalidos)))
    print("Ciudades corregidas        : {}".format(ciudades_corregidas))
    print("Emails rescatados (varios) : {}".format(emails_rescatados))
    print("Emails inválidos           : {}".format(len(emails_invalidos)))
    print()
    assert filas_entrada == filas_vacias + duplicados + len(filas_salida)
    print("Cuadre: {} entrada = {} vacías + {} duplicadas + {} salida".format(
        filas_entrada, filas_vacias, duplicados, len(filas_salida)))

    if emails_invalidos:
        print()
        print("--- Emails inválidos ({}) — se conservan en la salida tal cual ---".format(
            len(emails_invalidos)))
        for numero, valor in emails_invalidos:
            print("  fila {:>4}: {!r}".format(numero, valor))

    if telefonos_invalidos:
        print()
        print("--- Teléfonos no válidos ({}) — se conservan en la salida tal cual ---".format(
            len(telefonos_invalidos)))
        for numero, valor in telefonos_invalidos:
            print("  fila {:>4}: {!r}".format(numero, valor))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
