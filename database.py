import sqlite3
import json

class Database:
    def __init__(self, db_path='data/database.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Usuario (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    rut TEXT UNIQUE NOT NULL,
                    telefono TEXT NOT NULL
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Avistamiento (
                    id INTEGER PRIMARY KEY,
                    confirmado_autoridades BOOLEAN,
                    ubicacion TEXT NOT NULL,  -- This will store JSON data
                    fecha TEXT NOT NULL,
                    adulto BOOLEAN,
                    usuario_id INTEGER,
                    FOREIGN KEY(usuario_id) REFERENCES Usuario(id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS Imagen (
                    id INTEGER PRIMARY KEY,
                    archivo TEXT NOT NULL,
                    miniatura TEXT NOT NULL,
                    avistamiento_id INTEGER,
                    FOREIGN KEY(avistamiento_id) REFERENCES Avistamiento(id)
                )
            ''')

    def insert_user(self, nombre, apellido, rut, telefono):
        with self.conn:
            self.conn.execute('INSERT INTO Usuario (nombre, apellido, rut, telefono) VALUES (?, ?, ?, ?)', 
                              (nombre, apellido, rut, telefono))

    def get_user(self, rut):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM Usuario WHERE rut = ?', (rut,))
            return cursor.fetchone()

    def insert_avistamiento(self, confirmado_autoridades, ubicacion, fecha, adulto, usuario_id):
        with self.conn:
            self.conn.execute('INSERT INTO Avistamiento (confirmado_autoridades, ubicacion, fecha, adulto, usuario_id) VALUES (?, ?, ?, ?, ?)', 
                              (confirmado_autoridades, json.dumps(ubicacion), fecha, adulto, usuario_id))

    def insert_imagen(self, archivo, miniatura, avistamiento_id):
        with self.conn:
            self.conn.execute('INSERT INTO Imagen (archivo, miniatura, avistamiento_id) VALUES (?, ?, ?)', 
                              (archivo, miniatura, avistamiento_id))

    def fetch_avistamientos(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM Avistamiento')
            return cursor.fetchall()

    def fetch_images(self):
        with self.conn:
            cursor = self.conn.execute('SELECT * FROM Imagen')
            return cursor.fetchall()



### Database