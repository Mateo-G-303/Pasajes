import oracledb

DB_CONFIG = {
    'user': 'mlga01',       
    'password': 'mlga01', 
    'dsn': 'localhost:1521/xe'
}

def get_db_connection():
    try:
        conn = oracledb.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None