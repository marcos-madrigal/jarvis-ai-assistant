import sqlite3

class GestorMemoria:
    def __init__(self, db_name='jarvis_memoria.db'):
        # Aquí añadimos el parámetro para permitir hilos múltiples
        self.conexion = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conexion.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rol TEXT,
                mensaje TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conexion.commit()

    def guardar(self, rol, mensaje):
        self.cursor.execute('INSERT INTO conversaciones (rol, mensaje) VALUES (?, ?)', (rol, mensaje))
        self.conexion.commit()

    def cargar_ultimos(self, limite=10):
        try:
            self.cursor.execute('SELECT rol, mensaje FROM conversaciones ORDER BY id DESC LIMIT ?', (limite,))
            registros = self.cursor.fetchall()
            return list(reversed(registros))
        except Exception as e:
            print(f"Error al cargar la memoria a largo plazo: {e}")
            return []