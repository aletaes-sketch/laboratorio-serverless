import json
import uuid
import hashlib
import platform
import socket
from datetime import datetime, timezone
from urllib.parse import parse_qs
from html import escape


def handle(event, context):

    if event.method == "GET":
        formulario = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Registro Serverless</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f1f5f9;
                    padding: 50px 20px;
                }
                .contenedor {
                    max-width: 450px;
                    margin: auto;
                    padding: 30px;
                    background: white;
                    border-radius: 10px;
                }
                input, button {
                    width: 100%;
                    padding: 12px;
                    margin: 8px 0 16px;
                    box-sizing: border-box;
                }
                button {
                    background: #1769aa;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="contenedor">
                <h2>Registro de Ejecución Serverless</h2>
                <p>Introducción al Cómputo de la Nube</p>

                <form method="POST">
                    <label>Nombre</label>
                    <input name="nombre" required maxlength="100">

                    <label>Apellido</label>
                    <input name="apellido" required maxlength="100">

                    <label>Correo del aula virtual</label>
                    <input name="email" type="email"
                           required maxlength="254">

                    <button type="submit">
                        Generar archivo JSON
                    </button>
                </form>
            </div>
        </body>
        </html>
        """

        return {
            "statusCode": 200,
            "body": formulario,
            "headers": {
                "Content-Type": "text/html; charset=utf-8"
            }
        }

    if event.method == "POST":

        datos = parse_qs(
            event.body.decode("utf-8"),
            keep_blank_values=True
        )

        nombre = datos.get("nombre", [""])[0].strip()
        apellido = datos.get("apellido", [""])[0].strip()
        email = datos.get("email", [""])[0].strip()

        if not nombre or not apellido or not email or "@" not in email:
            return {
                "statusCode": 400,
                "body": "Datos incompletos o correo inválido"
            }

        token = str(uuid.uuid4())

        registro = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "token": token,
            "fecha_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "sistema_operativo": platform.system(),
            "version_so": platform.release(),
            "arquitectura": platform.machine(),
            "procesador": platform.processor(),
            "version_python": platform.python_version(),
            "hostname_contenedor": socket.gethostname(),
            "plataforma": "OpenFaaS",
            "funcion": "registro-serverless",
            "estado": "Ejecucion exitosa"
        }

        contenido = json.dumps(
            registro,
            sort_keys=True,
            ensure_ascii=False
        )

        firma = hashlib.sha256(
            contenido.encode("utf-8")
        ).hexdigest()

        registro["firma_sha256"] = firma

        archivo = json.dumps(
            registro,
            indent=4,
            ensure_ascii=False
        )

        return {
            "statusCode": 200,
            "body": archivo,
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "Content-Disposition":
                    f'attachment; filename="registro_{token}.json"'
            }
        }

    return {
        "statusCode": 405,
        "body": "Método HTTP no permitido"
    }
