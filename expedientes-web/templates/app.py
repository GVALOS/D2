from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="hospital"
    )

@app.route("/empleados/nuevo", methods=["GET", "POST"])
def registrar_empleado():
    mensaje = None
    
    if request.method == "POST":
        # Capturar y limpiar los datos enviados por el formulario
        nombre = request.form.get("nombre", "").strip()
        dui = request.form.get("dui", "").strip()
        perfil = request.form.get("perfil", "").strip()
        estado_dui = request.form.get("estado_dui", "pendiente")
        observaciones = request.form.get("observaciones", "").strip()

        # Validación básica de campos vacíos en el servidor
        if not nombre or not dui or not perfil:
            mensaje = "Por favor, completa todos los campos obligatorios."
        else:
            conexion = conectar()
            cursor = conexion.cursor(dictionary=True)
            try:
                # Verifica si el DUI ya existe en la base de datos
                cursor.execute("SELECT id FROM empleados WHERE dui = %s", (dui,))
                existente = cursor.fetchone()
                
                if existente:
                    mensaje = "Error: El número de DUI ingresado ya se encuentra registrado en el sistema."
                else:
                    # Inserción parametrizada en la tabla empleados para prevenir inyección SQL
                    cursor.execute(
                        "INSERT INTO empleados (nombre, dui, perfil) VALUES (%s, %s, %s)",
                        (nombre, dui, perfil)
                    )
                    
                    # Obtener el ID del último empleado insertado para relacionarlo con documentos
                    empleado_id = cursor.lastrowid
                    
                    # Inserción en la tabla relacionada documentos
                    cursor.execute(
                        "INSERT INTO documentos (empleado_id, estado_dui, observaciones) VALUES (%s, %s, %s)",
                        (empleado_id, estado_dui, observaciones)
                    )
                    
                    conexion.commit()
                    return redirect(url_for("listar_empleados"))
                    
            except Exception as e:
                conexion.rollback()
                mensaje = f"Error al procesar el registro: {e}"
            finally:
                cursor.close()
                conexion.close()

    return render_template("nuevo.html", mensaje=mensaje)