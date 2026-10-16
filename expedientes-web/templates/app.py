from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)

RUTA_DB = Path(__file__).resolve().parent / "documentos.db"

# Conectando con Base de Datos
def conectar():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    return conexion

# Consultando datos registrados
@app.route("/empleados")
def listar_empleados():
    conexion = conectar()
    try:
        empleados = conexion.execute("""
            SELECT *
            FROM documentos
            ORDER BY id DESC
        """).fetchall()
    finally:
        conexion.close()

    return render_template(
        "empleados.html",
        empleados=empleados
    )

# MÓDULO INTEGRANTE 3: Registro y validación de nuevos expedientes
@app.route('/empleados/nuevo', methods=['GET', 'POST'])
def nuevo_empleado():
    if request.method == 'POST':
        # Capturamos los datos que el usuario escribe en la pantalla
        nombre = request.form.get('nombre_completo', '').strip()
        dui = request.form.get('dui', '').strip()
        estado_dui = request.form.get('estado_dui', '').strip()
        estado_antecedentes = request.form.get('estado_antecedentes', '').strip()
        estado_carnet_junta = request.form.get('estado_carnet_junta', '').strip()
        observaciones = request.form.get('observaciones', '').strip()

        # Validación: si falta algún dato obligatorio, mostramos un error
        if not nombre or not dui or not estado_dui or not estado_antecedentes or not estado_carnet_junta:
            error = "Todos los campos principales son obligatorios. Por favor, completa el formulario."
            return render_template(
                'nuevo.html', 
                error=error, 
                nombre_completo=nombre, 
                dui=dui, 
                estado_dui=estado_dui, 
                estado_antecedentes=estado_antecedentes, 
                estado_carnet_junta=estado_carnet_junta, 
                observaciones=observaciones
            )

        try:
            # Guardamos los datos de forma segura en la base de datos
            conexion = conectar()
            conexion.execute(
                """
                INSERT INTO documentos (nombre_completo, dui, estado_dui, estado_antecedentes, estado_carnet_junta, observaciones) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nombre, dui, estado_dui, estado_antecedentes, estado_carnet_junta, observaciones)
            )
            conexion.commit()
            conexion.close()
            
            # Si todo sale bien, volvemos a la lista principal
            return redirect(url_for('listar_empleados'))
            
        except Exception as e:
            error = f"Ocurrió un error al registrar (posible DUI duplicado): {e}"
            return render_template(
                'nuevo.html', 
                error=error, 
                nombre_completo=nombre, 
                dui=dui, 
                estado_dui=estado_dui, 
                estado_antecedentes=estado_antecedentes, 
                estado_carnet_junta=estado_carnet_junta, 
                observaciones=observaciones
            )

    # Si entramos por primera vez, mostramos el formulario en blanco
    return render_template('nuevo.html')

# Verificando el __name__ para correr
if __name__ == "__main__":
    app.run(debug=True)