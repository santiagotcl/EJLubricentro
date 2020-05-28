from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL

app=Flask(__name__)

#MYSQL conexion
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "bbddlub" #le pido que se conecte a la base de datos prueba flask
#cuando pongo el puerto no anda
mysql = MySQL(app)

#iniciamos sesion(guarda datos en una memoria para luego usarlos)
app.secret_key="mysecretkey"

#en templates guardo todo lo que se ve

suma=[]#memoria interna de articulos seleccionados
total=0#total en pesos de la compra

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buscar", methods= ["POST"])
def buscar():
    if request.method == "POST":
        
        return render_template("buscar.html", code=0)



@app.route("/buscarn", methods=["POST"])
def busc():
    nombre = request.form["nombre"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE PRODUCTO LIKE '"+nombre+" %' OR PRODUCTO LIKE '% "+nombre+" %' OR PRODUCTO LIKE '% "+nombre+"' ")
    data = cur.fetchall()
    print(data)
    return render_template("buscar.html", contactos=data, sumas=suma, total=total)




@app.route("/buscarc", methods= ["POST"])
def busccod():
    if request.method == "POST":
        codigo = request.form["codigo"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
        data = cur.fetchall()
        print(data)
        return render_template("buscar.html", contactos=data)



@app.route("/vender/<codigo>")
def vender(codigo):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
    data = cur.fetchall()
    return render_template("vender.html", contactos=data)



@app.route("/vendido/<int:stock>/<string:codigo>")
def vendido(stock,codigo):
    stock = stock - 1
    print(stock)
    cur = mysql.connection.cursor() #me conecto con la BDD
    cur.execute("""
                    UPDATE PRODUCTOS
                    SET CANTIDAD = %s
                    WHERE CODIGO=%s
        """,(stock,codigo)) #hago la consulta SQL
    mysql.connection.commit() #guardo los cambios
    return render_template("index.html")


@app.route("/agregar/<string:codigo>")
def agregar(codigo):
    global total
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
    data1 = cur.fetchall()
    suma.append(data1[0])
    temp=data1[0]
    total = total + temp[3]
    return render_template("buscar.html", sumas=suma, total=total)


@app.route("/eliminar/<string:codigo>")
def eliminar(codigo):
    global total
    for sum in suma:
        if (sum[1] == codigo):
            total=total-sum[3]
            suma.remove(sum)
    return render_template("buscar.html", sumas=suma, total=total)

@app.route("/venta")
def venta():
    global total
    for sum in suma:
        stock=sum[2]
        codigo=sum[1]
        stock = stock - 1
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("""
                     UPDATE PRODUCTOS
                     SET CANTIDAD = %s
                      WHERE CODIGO=%s
            """,(stock,codigo)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
    total=0
    for sum in suma:
        suma.pop()
    suma.pop()
    print(suma)
    flash("VENTA REALIZADA!") #envia mesajes entre vistas
    return redirect(url_for("index"))

#def index():
#    cur = mysql.connection.cursor()
#    cur.execute("SELECT * FROM contacts")
#    data = cur.fetchall()
#    return render_template("index.html", contactos=data) #mando a renderizar una pagina html

@app.route("/add_contact", methods=['POST'])
def add_contact():
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        email = request.form["email"]
        print(nombre)
        print(email)
        print(telefono)
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("INSERT INTO contacts (nombre,telefono,email) VALUES (%s, %s, %s)", 
        (nombre, telefono, email)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
        flash("contacto agregado satifactoriamente") #envia mesajes entre vistas
        return redirect(url_for("index")) #hago que se vuelva a cargar index.html al agregar un contacto


@app.route("/borrar/<string:id>")#recibo un parametro tipo string
def borrar_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contacts WHERE id = " + id )
    mysql.connection.commit() #guardo los cambios
    flash("contacto eliminado satifactoriamente") #envia mesajes entre vistas
    return redirect(url_for("index"))



@app.route("/editar/<id>")
def agregar_contacto(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contacts WHERE ID = " + id )
    data = cur.fetchall()
    print(data[0])
    flash("contacto editado satisfactoriamente") #envia mesajes entre vistas
    return render_template("editar-contacto.html", contacto=data[0])


@app.route("/actualizar/<id>", methods=["POST"])
def act(id):
    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        email = request.form["email"]
        print(nombre)
        print(email)
        print(telefono)
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("""
                    UPDATE contacts
                    SET nombre = %s,
                    telefono = %s,
                    email = %s
                    WHERE id=%s
        """,(nombre, telefono, email,id)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
        flash("contacto modificado satifactoriamente") #envia mesajes entre vistas
        return redirect(url_for("index")) #hago que se vuelva a cargar index.html al agregar un contacto


    
if __name__ == "__main__":
    app.run(port = 3000, debug = True) #hacemos que se refresque solo


    #flask usa un motor de plantilla, no es html puro, tiene otras cosillas