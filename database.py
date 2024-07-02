import mysql.connector


class Database:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = mysql.connector.connect(**self.config)

    def close(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def insert_user(
        self, nombre, cedula, telefono, estatura, edad, peso, genero, imagen
    ):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre,cedula,telefono,estatura,edad,peso,genero,imagen) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)",
            (nombre, cedula, telefono, estatura, edad, peso, genero, imagen),
        )
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def fetch_users(self):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return users

    def delete_user(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_cliente,))
        self.connection.commit()
        cursor.close()
        self.connection.close()
