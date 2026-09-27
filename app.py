"""Servidor Flask de Cumbre Digital Peru 2026: registro de asistentes con SQLite."""

import os
import re
import sqlite3

from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for

# ===== Configuración =====
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
# En Render se puede apuntar a un disco persistente con la variable DATABASE_PATH
RUTA_BD = os.environ.get("DATABASE_PATH", os.path.join(DIRECTORIO_BASE, "evento.db"))

AREAS = ["Tecnología", "Marketing", "Negocios", "Emprendimiento"]
REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS asistentes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    empresa        TEXT NOT NULL,
    area           TEXT NOT NULL CHECK (area IN ('Tecnología', 'Marketing', 'Negocios', 'Emprendimiento')),
    fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

app = Flask(__name__)


# ===== Base de datos =====
def obtener_bd():
    """Devuelve la conexión a SQLite de la petición actual (una por petición)."""
    if "bd" not in g:
        g.bd = sqlite3.connect(RUTA_BD)
        g.bd.row_factory = sqlite3.Row
    return g.bd


@app.teardown_appcontext
def cerrar_bd(_error):
    """Cierra la conexión al terminar cada petición."""
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


def inicializar_bd():
    """Crea la tabla de asistentes si todavía no existe."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.executescript(ESQUEMA)


def numero_registro(id_asistente):
    """Convierte el id en el código visible, p. ej. 7 → REG-0007."""
    return f"REG-{id_asistente:04d}"


app.jinja_env.filters["numero_registro"] = numero_registro


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
        try:
            bd = obtener_bd()
            cursor = bd.execute(
                "INSERT INTO asistentes (nombre, email, empresa, area) VALUES (?, ?, ?, ?)",
                (datos["nombre"], datos["email"], datos["empresa"], datos["area"]),
            )
            bd.commit()
            # Patrón POST → redirección → GET para evitar registros duplicados al recargar
            return redirect(url_for("confirmacion", id_asistente=cursor.lastrowid))
        except sqlite3.IntegrityError:
            errores["email"] = "Este correo ya está registrado."

    return render_template("index.html", areas=AREAS, datos=datos, errores=errores), 400


@app.route("/confirmacion/<int:id_asistente>")
def confirmacion(id_asistente):
    asistente = obtener_bd().execute(
        "SELECT * FROM asistentes WHERE id = ?", (id_asistente,)
    ).fetchone()
    if asistente is None:
        abort(404)
    return render_template("confirmacion.html", asistente=asistente)


@app.route("/admin")
def admin():
    bd = obtener_bd()
    asistentes = bd.execute("SELECT * FROM asistentes ORDER BY id DESC").fetchall()
    conteo = {area: 0 for area in AREAS}
    for fila in bd.execute("SELECT area, COUNT(*) AS total FROM asistentes GROUP BY area"):
        conteo[fila["area"]] = fila["total"]
    return render_template("admin.html", asistentes=asistentes, conteo=conteo)


@app.route("/api/asistentes")
def api_asistentes():
    filas = obtener_bd().execute("SELECT * FROM asistentes ORDER BY id").fetchall()
    return jsonify([dict(fila, numero_registro=numero_registro(fila["id"])) for fila in filas])


@app.errorhandler(404)
def no_encontrado(_error):
    return render_template("404.html"), 404


# La tabla se crea al importar el módulo (sirve tanto para `flask run` como para gunicorn)
inicializar_bd()

if __name__ == "__main__":
    app.run(debug=True)
