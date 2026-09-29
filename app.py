"""Servidor Flask de Cumbre Digital Peru 2026: registro de asistentes con Supabase (PostgreSQL)."""

import os
import re

import psycopg
from dotenv import load_dotenv
from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for
from psycopg.rows import dict_row

# ===== Configuración =====
# En local se lee el archivo .env; en Render se define DATABASE_URL en el panel
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta la variable de entorno DATABASE_URL con la cadena de conexión de Supabase. "
        "Cópiala desde Supabase → Connect → Session pooler y guárdala en el archivo .env."
    )

AREAS = ["Tecnología", "Marketing", "Negocios", "Emprendimiento"]
REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")

app = Flask(__name__)


# ===== Base de datos =====
def obtener_bd():
    """Devuelve la conexión a Supabase de la petición actual (una por petición)."""
    if "bd" not in g:
        g.bd = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.bd


@app.teardown_appcontext
def cerrar_bd(_error):
    """Cierra la conexión al terminar cada petición."""
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


def numero_registro(id_asistente):
    """Convierte el id en el código visible, p. ej. 7 → REG-0007."""
    return f"REG-{id_asistente:04d}"


def formato_fecha(fecha):
    """Muestra la fecha de registro como 2026-09-28 14:30."""
    return fecha.strftime("%Y-%m-%d %H:%M") if fecha else ""


app.jinja_env.filters["formato_fecha"] = formato_fecha


# ===== Validación =====
def validar(datos):
    """Devuelve un diccionario {campo: mensaje} con los errores encontrados."""
    errores = {}

    if not datos["nombre"]:
        errores["nombre"] = "Por favor, ingresa tu nombre completo."
    elif len(datos["nombre"]) < 3:
        errores["nombre"] = "El nombre debe tener al menos 3 caracteres."

    if not datos["email"]:
        errores["email"] = "Por favor, ingresa tu correo electrónico."
    elif not REGEX_EMAIL.match(datos["email"]):
        errores["email"] = "El formato del correo no es válido (ej. nombre@empresa.com)."

    if not datos["empresa"]:
        errores["empresa"] = "Por favor, ingresa el nombre de tu empresa u organización."

    if not datos["area"]:
        errores["area"] = "Por favor, selecciona un área de interés."
    elif datos["area"] not in AREAS:
        errores["area"] = "El área seleccionada no es válida."

    return errores


# ===== Rutas =====
@app.route("/")
def inicio():
    return render_template("index.html", areas=AREAS, datos={}, errores={})


@app.route("/registrar", methods=["POST"])
def registrar():
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "empresa": request.form.get("empresa", "").strip(),
        "area": request.form.get("area", "").strip(),
    }

    errores = validar(datos)
    if not errores:
        bd = obtener_bd()
        try:
            # Se reserva el id primero para poder guardar su número de registro en la misma fila
            id_asistente = bd.execute(
                "SELECT nextval(pg_get_serial_sequence('asistentes', 'id')) AS id"
            ).fetchone()["id"]
            bd.execute(
                """INSERT INTO asistentes (id, nombre, email, empresa, area_interes, numero_registro)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (id_asistente, datos["nombre"], datos["email"], datos["empresa"],
                 datos["area"], numero_registro(id_asistente)),
            )
            bd.commit()
            # Patrón POST → redirección → GET para evitar registros duplicados al recargar
            return redirect(url_for("confirmacion", id_asistente=id_asistente))
        except psycopg.errors.UniqueViolation:
            bd.rollback()
            errores["email"] = "Este correo ya está registrado."

    return render_template("index.html", areas=AREAS, datos=datos, errores=errores), 400


@app.route("/confirmacion/<int:id_asistente>")
def confirmacion(id_asistente):
    asistente = obtener_bd().execute(
        "SELECT * FROM asistentes WHERE id = %s", (id_asistente,)
    ).fetchone()
    if asistente is None:
        abort(404)
    return render_template("confirmacion.html", asistente=asistente)


@app.route("/admin")
def admin():
    bd = obtener_bd()
    asistentes = bd.execute("SELECT * FROM asistentes ORDER BY id DESC").fetchall()
    conteo = {area: 0 for area in AREAS}
    for fila in bd.execute(
        "SELECT area_interes, COUNT(*) AS total FROM asistentes GROUP BY area_interes"
    ):
        conteo[fila["area_interes"]] = fila["total"]
    return render_template("admin.html", asistentes=asistentes, conteo=conteo)


@app.route("/api/asistentes")
def api_asistentes():
    filas = obtener_bd().execute("SELECT * FROM asistentes ORDER BY id").fetchall()
    return jsonify(filas)


@app.errorhandler(404)
def no_encontrado(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
