from flask import Blueprint, render_template, request, redirect, url_for
from db import get_db_connection

tipos_bp = Blueprint('tipos', __name__, url_prefix='/tipos')

@tipos_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TIPOS_PASAJE ORDER BY id_tipo ASC")
    tipos = cursor.fetchall()
    conn.close()
    return render_template('tipos.html', tipos=tipos)

@tipos_bp.route('/crear', methods=['POST'])
def crear():
    descripcion = request.form['descripcion']
    descuento = request.form['descuento']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO TIPOS_PASAJE (descripcion, descuento) VALUES (:1, :2)"
    cursor.execute(sql, [descripcion, descuento])
    conn.commit()
    conn.close()
    return redirect(url_for('tipos.index'))

@tipos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        descuento = float(request.form['descuento'])
        
        cursor.execute("UPDATE TIPOS_PASAJE SET descripcion=:1, descuento=:2 WHERE id_tipo=:3", 
                       [descripcion, descuento, id])
        conn.commit()
        conn.close()
        return redirect(url_for('tipos.index'))

    cursor.execute("SELECT * FROM TIPOS_PASAJE WHERE id_tipo = :1", [id])
    tipo = cursor.fetchone()
    conn.close()
    return render_template('editar_tipo.html', tipo=tipo)

@tipos_bp.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM TIPOS_PASAJE WHERE id_tipo = :1", [id])
        conn.commit()
    except Exception as e:
        print(f"Error al eliminar tipo: {e}")
    finally:
        conn.close()
    return redirect(url_for('tipos.index'))