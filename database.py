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
        cursor.execute("SELECT * FROM usuarios order by id DESC")
        users = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return users

    def get_user_data(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id_cliente,))
        user = cursor.fetchone()
        cursor.close()
        self.connection.close()
        return user

    def get_user_cedula(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT cedula FROM usuarios WHERE id = %s", (id_cliente,))
        user = cursor.fetchone()
        cursor.close()
        self.connection.close()
        if user:
            return user[0]  # Return the cedula as a string

    def delete_user(self, id_cliente):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_cliente,))
        self.connection.commit()
        cursor.close()
        self.connection.close()
