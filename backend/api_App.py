from flask import Flask, request, jsonify
#pip install Flask

#pip install flask-cors
from flask_cors import CORS

#pip install mysql-connector-python

import mysql.connector

#no es necesario instalar
import os
import time, datetime


#-------------------------------------------------
app = Flask(__name__)

#permitir acceso desde cualquier origen
CORS(app, resources={r"/*": {"origins": "*"}})

#creo la class Mensaje que conecta con la base de datos

class Mensaje:
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        # El atributo .conn pertenece al objeto que se está instanciando. 
        # Representa la conexión a la base de datos MySQL. 
        # permite realizar operaciones como ejecutar consultas SQL, realizar transacciones, etc.
        # El atributo .cursor es un objeto de cursor que se utiliza para ejecutar comandos SQL en la base de datos conectada (self.conn). 
        # El cursor actúa como un "puntero" a un resultado específico en la base de datos, y se usa para ejecutar consultas y recuperar resultados.
        self.cursor = self.conn.cursor()
        # En resumen, self.conn representa la conexión a la base de datos MySQL, mientras que self.cursor representa 
        # el objeto que se utiliza para ejecutar comandos y consultas en esa conexión. 
        # Estos dos objetos son esenciales para interactuar con la base de datos desde Python mediante la librería mysql.connector.

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, Python arrojará un error de excepción que queda capturado en esta parte. 
            # Entonces creamos la base de datos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS mensajes (
            id int(11) NOT NULL AUTO_INCREMENT,
            nombre varchar(30) NOT NULL,
            apellido varchar(30) NOT NULL,
            telefono varchar(15) NOT NULL,
            email varchar(60) NOT NULL,
            mensaje varchar(500) NOT NULL,
            fecha_envio datetime NOT NULL,
            leido tinyint(1) NOT NULL,
            gestion varchar(500) DEFAULT NULL,
            fecha_gestion datetime DEFAULT NULL,
            PRIMARY KEY(`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_spanish_ci;
            ''')
        # Confirma la transacción en la base de datos.
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def enviar_mensaje(self, nombre, apellido, telefono, email, consulta):
         sql = "INSERT INTO mensajes(nombre, apellido, telefono, email, mensaje, fecha_envio) VALUES (%s, %s, %s, %s, %s, %s)"
         fecha_envio = datetime.datetime.now()
         valores = (nombre, apellido, telefono, email, consulta, fecha_envio)
         self.cursor.execute(sql, valores)        
         self.conn.commit()
         return True

    #----------------------------------------------------------------
    def listar_mensajes(self):
        self.cursor.execute("SELECT * FROM mensajes")
        mensajes = self.cursor.fetchall()
        return mensajes

    #----------------------------------------------------------------
    def responder_mensaje(self, id, gestion):
        fecha_gestion = datetime.datetime.now()
        sql = "UPDATE mensajes SET leido = 1, gestion = %s, fecha_gestion = %s WHERE id = %s"
        valores = (gestion, fecha_gestion, id)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def eliminar_mensaje(self, id):
        # Eliminamos un mensaje de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM mensajes WHERE id = {id}")
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def mostrar_mensaje(self, id):
         sql = f"SELECT id, nombre, apellido, telefono, email, mensaje, fecha_envio, leido, gestion, fecha_gestion FROM mensajes WHERE id = {id}"
         self.cursor.execute(sql)
         return self.cursor.fetchone()


mensaje = Mensaje(host='sveliz02.mysql.pythonanywhere-services.com', user='sveliz02', password='sxntxv970802', database='sveliz02$clientes')


#-------------------------------------------

@app.route("/mensajes", methods = ["GET"])
def listar_mensajes():
    mensajes = mensaje.listar_mensajes()
    return jsonify(mensajes)
#crea un json que contiene los datos de la base de datos, para poder ser enviado al front

#-----------------------------------------

#recojo los datos del form
@app.route("/mensajes", methods=["POST"])
def agregar_producto():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    email = request.form['email']
    consulta = request.form['mensaje']
    
    if mensaje.enviar_mensaje(nombre,apellido,telefono,email,consulta):
        return jsonify({"mensaje": "Producto agregado"}), 201
    else:
        return jsonify({"mensaje":"no fue posible reguistrar el mensaje"}), 400

#-----------------------------------------

@app.route("/mensajes/<int:id>", methods=["PUT"])
def responder_mensaje(id):
    gestion = request.form.get("gestion")

    if mensaje.responder_mensaje(id, gestion):
        return jsonify({"mensaje":"Mensaje modificado"}),200
    else:
        return jsonify({"mensaje":"Mensaje no encontrado"}),403


if __name__ == "__main__":
    app.run(debug=True)

