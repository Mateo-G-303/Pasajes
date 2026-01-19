from flask import Blueprint, render_template, request, redirect, url_for, Response
from db import get_db_connection
import oracledb
import csv
import io

pasajes_bp = Blueprint('pasajes', __name__, url_prefix='/pasajes')

@pasajes_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    filtro_ruta = request.args.get('id_ruta')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # CALCULAMOS EL VALOR AL VUELO: (valor_base de ruta) * (1 - descuento/100)
    sql = """
        SELECT 
            p.id_pasaje, 
            r.nombre_ruta, 
            u.numero_disco, 
            tp.descripcion, 
            (r.valor_base * (1 - (tp.descuento / 100))) as valor_calculado, 
            p.fecha_viaje 
        FROM PASAJES p
        JOIN RUTAS r ON p.id_ruta = r.id_ruta
        JOIN UNIDADES u ON p.id_unidad = u.id_unidad
        JOIN TIPOS_PASAJE tp ON p.id_tipo = tp.id_tipo
        WHERE 1=1 
    """
    
    params = []
    
    if filtro_ruta and filtro_ruta != "":
        sql += " AND p.id_ruta = :ruta"
        params.append(filtro_ruta)
        
    if fecha_inicio and fecha_fin:
        sql += " AND TRUNC(p.fecha_viaje) BETWEEN TO_DATE(:inicio, 'YYYY-MM-DD') AND TO_DATE(:fin, 'YYYY-MM-DD')"
        params.append(fecha_inicio)
        params.append(fecha_fin)
    
    sql += " ORDER BY p.id_pasaje DESC"
    
    cursor.execute(sql, params)
    pasajes = cursor.fetchall()

    cursor.execute("SELECT id_ruta, nombre_ruta FROM RUTAS")
    rutas = cursor.fetchall()
    cursor.execute("SELECT id_unidad, numero_disco FROM UNIDADES")
    unidades = cursor.fetchall()
    cursor.execute("SELECT id_tipo, descripcion FROM TIPOS_PASAJE")
    tipos = cursor.fetchall()

    conn.close()
    
    return render_template('pasajes.html', 
                           pasajes=pasajes, 
                           rutas=rutas, 
                           unidades=unidades, 
                           tipos=tipos,
                           filtro_ruta=filtro_ruta,
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin)

@pasajes_bp.route('/crear', methods=['POST'])
def crear():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        id_ruta = int(request.form['id_ruta'])
        id_unidad = int(request.form['id_unidad'])
        id_tipo = int(request.form['id_tipo'])
        
        # EL INSERT ES MÁS LIMPIO: Ya no guardamos el valor_pasaje físicamente
        sql = """INSERT INTO PASAJES (id_ruta, id_unidad, id_tipo, fecha_viaje) 
                 VALUES (:1, :2, :3, SYSDATE)"""
        cursor.execute(sql, [id_ruta, id_unidad, id_tipo])
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al registrar pasaje: {e}")
        
    return redirect(url_for('pasajes.index'))

@pasajes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            id_ruta = int(request.form['id_ruta'])
            id_unidad = int(request.form['id_unidad'])
            id_tipo = int(request.form['id_tipo'])
            
            # SOLO ACTUALIZAMOS LAS RELACIONES: El precio se recalcula solo en el SELECT
            sql = """UPDATE PASAJES SET id_ruta=:1, id_unidad=:2, id_tipo=:3 
                     WHERE id_pasaje=:4"""
            cursor.execute(sql, [id_ruta, id_unidad, id_tipo, id])
            
            conn.commit()
            conn.close()
            return redirect(url_for('pasajes.index'))
            
        except Exception as e:
            print(f"Error al editar: {e}")
            if conn: conn.close()
            return redirect(url_for('pasajes.index')) 

    # Bloque GET para cargar el formulario de edición
    cursor.execute("SELECT id_pasaje, id_ruta, id_unidad, id_tipo FROM PASAJES WHERE id_pasaje = :1", [id])
    pasaje = cursor.fetchone()
    
    cursor.execute("SELECT id_ruta, nombre_ruta FROM RUTAS")
    rutas = cursor.fetchall()
    cursor.execute("SELECT id_unidad, numero_disco FROM UNIDADES")
    unidades = cursor.fetchall()
    cursor.execute("SELECT id_tipo, descripcion FROM TIPOS_PASAJE")
    tipos = cursor.fetchall()
    
    conn.close()
    
    return render_template('editar_pasaje.html', 
                           pasaje=pasaje, 
                           rutas=rutas, 
                           unidades=unidades, 
                           tipos=tipos)

@pasajes_bp.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PASAJES WHERE id_pasaje = :1", [id])
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al eliminar: {e}")
    return redirect(url_for('pasajes.index'))

@pasajes_bp.route('/exportar')
def exportar_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    out_cursor = cursor.var(oracledb.CURSOR)
    # Asegúrate de que tu SP_EXPORTAR_CSV_PASAJES también se actualice para no buscar la columna borrada
    cursor.callproc('SP_EXPORTAR_CSV_PASAJES', [out_cursor])
    
    filas = out_cursor.getvalue().fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Ruta', 'Tipo', 'Valor', 'Fecha', 'Hora'])
    
    for fila in filas:
        writer.writerow(fila[0].split(','))
        
    conn.close()
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=reporte_pasajes.csv"})