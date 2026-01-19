from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

rutas_bp = Blueprint('rutas', __name__, url_prefix='/rutas')

@rutas_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Seleccionamos también el valor_base para mostrarlo en la tabla
    cursor.execute("SELECT id_ruta, nombre_ruta, origen, destino, valor_base FROM RUTAS ORDER BY id_ruta DESC")
    rutas = cursor.fetchall()
    conn.close()
    return render_template('rutas.html', rutas=rutas)

@rutas_bp.route('/crear', methods=['POST'])
def crear():
    try:
        nombre = request.form['nombre']
        origen = request.form['origen']
        destino = request.form['destino']
        # NUEVO: Capturamos el precio base desde el formulario
        valor_base = float(request.form['valor']) 
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # NUEVO: Actualizamos el INSERT para incluir el valor_base
        sql = "INSERT INTO RUTAS (nombre_ruta, origen, destino, valor_base) VALUES (:1, :2, :3, :4)"
        cursor.execute(sql, [nombre, origen, destino, valor_base])
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al crear ruta: {e}")
        
    return redirect(url_for('rutas.index'))

@rutas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            origen = request.form['origen']
            destino = request.form['destino']
            valor = float(request.form['valor'])
            
            sql = """UPDATE RUTAS SET nombre_ruta=:1, origen=:2, destino=:3, valor_base=:4 
                     WHERE id_ruta=:5"""
            cursor.execute(sql, [nombre, origen, destino, valor, id])
            conn.commit()
            return redirect(url_for('rutas.index'))
        except Exception as e:
            print(f"Error al editar ruta: {e}")
        finally:
            conn.close()

    # Método GET: Cargar datos actuales
    cursor.execute("SELECT * FROM RUTAS WHERE id_ruta = :1", [id])
    ruta = cursor.fetchone()
    conn.close()
    return render_template('editar_ruta.html', ruta=ruta)

@rutas_bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM RUTAS WHERE id_ruta = :1", [id])
        conn.commit()
    except Exception as e:
        # Es muy probable que falle si ya hay pasajes vendidos en esta ruta (Integridad Referencial)
        print(f"No se puede eliminar la ruta porque tiene pasajes asociados: {e}")
    finally:
        conn.close()
    return redirect(url_for('rutas.index'))