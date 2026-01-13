from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

rutas_bp = Blueprint('rutas', __name__, url_prefix='/rutas')

@rutas_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RUTAS ORDER BY id_ruta DESC")
    rutas = cursor.fetchall()
    conn.close()
    return render_template('rutas.html', rutas=rutas)

@rutas_bp.route('/crear', methods=['POST'])
def crear():
    nombre = request.form['nombre']
    origen = request.form['origen']
    destino = request.form['destino']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO RUTAS (nombre_ruta, origen, destino) VALUES (:1, :2, :3)"
    cursor.execute(sql, [nombre, origen, destino])
    conn.commit()
    conn.close()
    return redirect(url_for('rutas.index'))

@rutas_bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM RUTAS WHERE id_ruta = :1", [id])
        conn.commit()
    except Exception as e:
        print(f"No se puede eliminar: {e}")
    finally:
        conn.close()
    return redirect(url_for('rutas.index'))