from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from datetime import datetime

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
total=0.0#total en pesos de la compra

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
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    return render_template("buscar.html", contactos=data, sumas=suma, total=total)




@app.route("/buscarc", methods= ["POST"])
def busccod():
    if request.method == "POST":
        codigo = request.form["codigo"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
        data = cur.fetchall()
        return render_template("buscar.html", contactos=data)



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
    temp=data1[0]
    temp1=list(temp)
    temp1.append(1)
    temp=tuple(temp1)
    suma.append(temp)
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
        stock = stock - int(sum[4])
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("""
                     UPDATE PRODUCTOS
                     SET CANTIDAD = %s
                      WHERE CODIGO=%s
            """,(stock,codigo)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
    total=0




    ##########################################################################
    ######################AGREGO VENTA A REGISTRO DE VENTAS###################
    ##########################################################################
    k=len(suma)
    now = datetime.now()
    fecha = now.strftime('%d-%m-%Y')
    hora = now.strftime("%H:%M")
    i=0
    while(i < k):
        print("HOLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(i)
        temp=list(suma[i])
        temp1=float(temp[4])*float(temp[3])
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("INSERT INTO ventas (PRODUCTO,CODIGO,CANTIDAD,PRECIO,HORA,FECHA) VALUES (%s, %s, %s,%s,%s,%s)", 
        (temp[0], temp[1], temp[4],temp1,hora,fecha)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
        i=i+1


    #eliminio lista parcial perro!!!!!!!
    for sum in suma:
        suma.pop()
    if(len(suma) >= 1):
        suma.pop() #el for no me borra el primer elemento (itera desde 1)


    flash("VENTA REALIZADA!") #envia mesajes entre vistas
    return redirect(url_for("index"))


@app.route("/aumentar/<precio>/<i>", methods=["POST"])
def aumentar(precio,i):
    global total
    cantidad = request.form["aumentar2"]
    print(cantidad)
    print("esta es la cantidad")
    #multiplico cantidad vieja por precio y resto al total
    temp=suma[int(i)]
    temp1=list(temp)
    precioparcial=float(temp1[4])*float(precio)
    total=total-precioparcial
    #multiplico cantidad nueva por precio y sumo al total
    tem=int(cantidad)
    tem2=float(tem)*float(precio)
    total=total + tem2
    #modifico cantidad en suma parcial para mostrar

    temp1[4]=cantidad
    suma[int(i)]=tuple(temp1)


    return render_template("buscar.html", sumas=suma, total=total)


@app.route("/ventas", methods=["POST"])
def Ventas():
    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM ventas")
        data = cur.fetchall()#resultado de la busqueda en la base de datos
        return render_template("ventas.html", contactos=data)







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