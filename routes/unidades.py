from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection

unidades_bp = Blueprint('unidades', __name__, url_prefix='/unidades')

@unidades_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UNIDADES ORDER BY numero_disco ASC")
    unidades = cursor.fetchall()
    conn.close()
    return render_template('unidades.html', unidades=unidades)

@unidades_bp.route('/crear', methods=['POST'])
def crear():
    placa = request.form['placa']
    disco = request.form['disco']
    capacidad = request.form['capacidad']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO UNIDADES (placa, numero_disco, capacidad) VALUES (:1, :2, :3)"
        cursor.execute(sql, [placa, disco, capacidad])
        conn.commit()
    except Exception as e:
        print(f"Error al crear unidad: {e}")
    finally:
        conn.close()
    return redirect(url_for('unidades.index'))

@unidades_bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM UNIDADES WHERE id_unidad = :1", [id])
        conn.commit()
    except Exception as e:
        print(f"No se puede eliminar (probablemente tenga pasajes asociados): {e}")
    finally:
        conn.close()
    return redirect(url_for('unidades.index'))