#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera messy_customers.csv: datos de clientes 100% sintéticos y deliberadamente sucios.

Ningún dato es real: nombres, emails, teléfonos y ciudades inventados con la
suciedad típica de CRMs y listas exportadas a mano:

  - emails en mayúsculas, con espacios alrededor o internos, dobles comas
    (dos emails pegados), sin "@", "(at)", dominios sin punto, punto final;
  - teléfonos en formatos caóticos: "+34 600 123 456", "600-123-456",
    "600123456", "0034...", "(+34) ...", letras coladas, prefijos inválidos;
  - nombres TODO EN MAYÚSCULAS, todo en minúsculas, mezcla aleatoria,
    dobles espacios, con partículas ("de la Fuente");
  - ciudades sin acentos ("Malaga"), en mayúsculas, con espacios, alias
    ("la coruna" por "A Coruña");
  - filas duplicadas: idénticas y con variantes de formato (misma persona,
    distinta suciedad) para que la deduplicación tenga que normalizar;
  - filas completamente vacías (o solo espacios).

Semilla fija (42) → generación reproducible. Solo stdlib (Python 3).

Uso:
    python3 gen_messy_customers.py   # escribe messy_customers.csv junto al script
"""
import csv
import random
import unicodedata
from pathlib import Path

SEED = 42
AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "messy_customers.csv"

N_PERSONAS = 180        # personas únicas
N_DUP_EXACTAS = 7       # copias idénticas de filas ya existentes
N_DUP_VARIANTES = 7     # misma persona con otra combinación de suciedad
N_VACIAS = 6            # filas vacías (algunas solo con espacios)
# Total: 180 + 7 + 7 + 6 = 200 filas de datos

NOMBRES = [
    "María", "Carmen", "Ana", "Laura", "Marta", "Lucía", "Elena", "Isabel",
    "Rosa", "Pilar", "Cristina", "Sara", "Beatriz", "Nuria", "Andrea",
    "José", "Juan", "Antonio", "Carlos", "Javier", "Manuel", "Francisco",
    "David", "Pedro", "Ángel", "Luis", "Miguel", "Rafael", "Sergio",
    "Fernando", "Pablo", "Alejandro", "Daniel",
]
APELLIDOS = [
    "García", "Rodríguez", "López", "Martínez", "Sánchez", "Pérez", "Gómez",
    "Fernández", "Moreno", "Jiménez", "Ruiz", "Hernández", "Díaz", "Álvarez",
    "Torres", "Romero", "Navarro", "Ramírez", "Domínguez", "Gil", "Vázquez",
    "Serrano", "Ramos", "Molina", "Castro", "Ortega", "Rubio", "Delgado",
    "Iglesias", "Medina",
]
APELLIDOS_COMPUESTOS = ["de la Fuente", "del Olmo", "de la Torre", "de la Cruz", "de los Ríos"]
PARTICULAS = {"de", "del", "la", "las", "los", "el"}

DOMINIOS = ["gmail.com", "hotmail.com", "yahoo.es", "outlook.com", "icloud.com",
            "telefonica.net", "correo.es"]

# Misma lista canónica que usa clean_customers.py para normalizar.
CIUDADES = [
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


def quitar_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto)
                   if unicodedata.category(c) != "Mn")


def nueva_persona(rng):
    nombre = "{} {} {}".format(
        rng.choice(NOMBRES),
        rng.choice(APELLIDOS),
        rng.choice(APELLIDOS + APELLIDOS_COMPUESTOS),
    )
    return {
        "nombre": nombre,
        "email": email_base(nombre, rng),
        "telefono": telefono_base(rng),
        "ciudad": rng.choice(CIUDADES),
    }


def email_base(nombre, rng):
    palabras = [p for p in quitar_acentos(nombre).lower().split() if p not in PARTICULAS]
    nombre_p, ap1 = palabras[0], palabras[1]
    ap2 = palabras[2] if len(palabras) > 2 else None
    dom = rng.choice(DOMINIOS)
    estilos = [
        "{}.{}@{}".format(nombre_p, ap1, dom),
        "{}{}@{}".format(nombre_p, ap1, dom),
        "{}{}@{}".format(nombre_p[0], ap1, dom),
        "{}.{}.{}@{}".format(nombre_p, ap1, ap2, dom) if ap2 else "{}.{}@{}".format(nombre_p, ap1, dom),
        "{}_{}@{}".format(nombre_p, ap1, dom),
        "{}{}{}@{}".format(nombre_p, ap1, rng.randint(1, 99), dom),
    ]
    return rng.choice(estilos)


def telefono_base(rng):
    # Móviles (6xx/7xx) mayoritarios; algunos fijos (8xx/9xx).
    prefijo = rng.choice(["6", "7", "6", "6", "9", "8"])
    return prefijo + "".join(rng.choice("0123456789") for _ in range(8))


def ensuciar_nombre(nombre, rng):
    r = rng.random()
    if r < 0.35:
        return nombre
    if r < 0.50:
        return nombre.upper()
    if r < 0.62:
        return nombre.lower()
    if r < 0.72:  # mayúsculas/minúsculas aleatorias por palabra
        return " ".join(p.upper() if rng.random() < 0.5 else p.lower()
                        for p in nombre.split())
    if r < 0.82:  # doble espacio
        return nombre.replace(" ", "  ", 1)
    if r < 0.90:  # espacios alrededor
        return " {} ".format(nombre)
    return nombre.upper().replace(" ", "  ")


def ensuciar_email(email, rng, forzar_valido=False):
    """Devuelve (email_sucio, seguira_valido_tras_limpieza)."""
    if forzar_valido:
        return rng.choice([email, email.upper(), "  {} ".format(email)]), True
    r = rng.random()
    if r < 0.55:
        return email, True
    if r < 0.62:
        return email.upper(), True
    if r < 0.68:
        return "  {} ".format(email), True
    if r < 0.72:
        return "{} ".format(email.upper()), True
    local, _, dom = email.partition("@")
    if len(local) > 3:
        mitad = len(local) // 2
        con_espacio = "{} {}@{}".format(local[:mitad], local[mitad:], dom)
    else:
        con_espacio = "{} @{}".format(local, dom)
    opciones = [
        ("{}{}".format(local, dom), False),                            # sin @
        ("{}(at){}".format(local, dom), False),                        # (at)
        ("{}@{}".format(local, dom.replace(".", "", 1)), False),       # dominio sin punto
        ("{}.".format(email), False),                                  # punto final
        ("{}@{}".format(local.replace(".", "..", 1), dom) if "." in local else con_espacio, False),
        (con_espacio, False),                                          # espacio interno
        ("{}@".format(local), False),                                  # truncado
        ("{},{}.backup@{}".format(email, local, dom), True),           # dos emails pegados (rescatable)
    ]
    return rng.choice(opciones)


def ensuciar_telefono(digitos, rng, forzar_valido=False):
    """Devuelve (telefono_sucio, es_normalizable)."""
    if not forzar_valido and rng.random() < 0.05:
        return rng.choice([
            "12345",
            "5" + digitos[1:],                    # prefijo inválido en España
            "+34 {} {}".format(digitos[:3], digitos[3:5]),  # incompleto
            digitos[:6],                          # incompleto
        ]), False
    d1, d2, d3 = digitos[:3], digitos[3:6], digitos[6:]
    estilos = [
        "+34 {} {} {}".format(d1, d2, d3),
        "+34{}".format(digitos),
        "{}-{}-{}".format(d1, d2, d3),
        "{}.{}.{}".format(d1, d2, d3),
        digitos,
        "(+34) {} {} {}".format(d1, d2, d3),
        "0034{}".format(digitos),
        "0034 {} {} {}".format(d1, d2, d3),
        "{} {} {}".format(d1, d2, d3),
        " {} ".format(digitos),
        "Tel. {} {} {}".format(d1, d2, d3),
        "{}x{}".format(digitos[:5], digitos[5:]),  # letra colada (recuperable)
        "{}/{}/{}".format(d1, d2, d3),
    ]
    return rng.choice(estilos), True


def ensuciar_ciudad(ciudad, rng):
    r = rng.random()
    if r < 0.30:
        return ciudad
    if r < 0.42:
        return ciudad.upper()
    if r < 0.54:
        return ciudad.lower()
    if r < 0.64:
        return quitar_acentos(ciudad)              # "Malaga", "Caceres"
    if r < 0.72:
        return quitar_acentos(ciudad).upper()
    if r < 0.80:
        return quitar_acentos(ciudad).lower()
    if r < 0.88:
        return " {} ".format(ciudad)
    if ciudad == "A Coruña" and r < 0.94:
        return rng.choice(["la coruna", "La Coruna", "A Coruna"])
    return quitar_acentos(ciudad).capitalize()     # "San sebastian"


def fila_sucia(persona, rng, forzar_validos=False):
    email, email_ok = ensuciar_email(persona["email"], rng, forzar_valido=forzar_validos)
    telefono, telefono_ok = ensuciar_telefono(persona["telefono"], rng, forzar_valido=forzar_validos)
    fila = [
        ensuciar_nombre(persona["nombre"], rng),
        email,
        telefono,
        ensuciar_ciudad(persona["ciudad"], rng),
    ]
    return fila, email_ok and telefono_ok


def main():
    rng = random.Random(SEED)
    personas = [nueva_persona(rng) for _ in range(N_PERSONAS)]

    # (fila, util_como_origen_de_duplicado, persona)
    registros = []
    for persona in personas:
        fila, util = fila_sucia(persona, rng)
        registros.append((fila, util, persona))

    # Duplicadas exactas: copia literal de una fila ya existente.
    for _ in range(N_DUP_EXACTAS):
        fila, _, _ = rng.choice(registros)
        registros.append((list(fila), False, None))

    # Duplicadas con variantes de formato: misma persona, otra suciedad.
    # El origen debe tener email y teléfono recuperables para que la copia
    # normalice a la misma clave y la deduplicación la detecte.
    utiles = [r for r in registros if r[1] and r[2] is not None]
    for _ in range(N_DUP_VARIANTES):
        _, _, persona = rng.choice(utiles)
        fila, _ = fila_sucia(persona, rng, forzar_validos=True)
        registros.append((fila, False, None))

    # Filas vacías: totalmente vacías o solo con espacios.
    for i in range(N_VACIAS):
        registros.append((["  ", "", " ", ""] if i % 2 else ["", "", "", ""], False, None))

    rng.shuffle(registros)

    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["nombre", "email", "telefono", "ciudad"])
        for fila, _, _ in registros:
            escritor.writerow(fila)

    print("Escrito {}: {} filas de datos + cabecera ({} personas únicas, "
          "{} exactas + {} variantes duplicadas, {} vacías)".format(
              SALIDA.name, len(registros), N_PERSONAS,
              N_DUP_EXACTAS, N_DUP_VARIANTES, N_VACIAS))


if __name__ == "__main__":
    main()
