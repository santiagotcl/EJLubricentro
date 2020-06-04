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

##########################################################################
############BUSQUEDA POR NOMBRE Y CODIGO PARPANTALLA BUSCAR###############
##########################################################################

@app.route("/buscarn", methods=["POST"])
def busc():
    nombre = request.form["nombre"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE PRODUCTO LIKE '"+nombre+" %' OR PRODUCTO LIKE '% "+nombre+" %' OR PRODUCTO LIKE '% "+nombre+"' ")
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    if (len(data)==0):
        cur.execute("SELECT * FROM PRODUCTOS WHERE PRODUCTO=%s",(nombre,))
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
            total=total-(float(sum[3])*float(sum[4]))
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
    temp=suma[int(i)]
    temp1=list(temp)
    if(int(cantidad) > int(temp1[2])):
        flash("NO HAY SUFICIENTE STOCK!!!") #envia mesajes entre vistas
        return render_template("buscar.html", sumas=suma, total=total)
    else:
        print(i)
        #multiplico cantidad vieja por precio y resto al total
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

@app.route("/devolver/<id>")#disulve ventas realizadas y vuelve a sumar stock en caso de error
def devolver(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ventas WHERE ID = "+id+"")#saco cantidad y codigo del articulo
    data = cur.fetchall()
    data1=list(data[0])
    cur.execute("""SELECT * FROM PRODUCTOS WHERE CODIGO=%s""",(data1[2],)) #saco stock actual para sumar el que se debe reintegrar
    data = cur.fetchall()
    data=list(data[0])
    stock=int(data[2])+int(data1[3])
    cur.execute("""
                     UPDATE PRODUCTOS
                     SET CANTIDAD = %s
                      WHERE CODIGO=%s
            """,(stock,data1[2])) #hago la consulta SQL

    cur.execute("DELETE FROM ventas WHERE ID = "+id+"")
    mysql.connection.commit() #guardo los cambios
    cur.execute("SELECT * FROM ventas")
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    flash("ARTICULO REINCORPORADO!!!")
    return render_template("ventas.html", contactos=data)
    

@app.route("/a_clientes", methods=["POST"])
def a_clientes():
    return render_template("clientes.html")


@app.route("/add_client", methods=["POST"])
def add_client():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        telefono = request.form["telefono"]
        patente = request.form["patente"]
        kilometros = request.form["kilometros"]
        auto=request.form["auto"]

        now = datetime.now()
        fecha = now.strftime('%d-%m-%Y')
        hora = now.strftime("%H:%M")
        print(int(telefono))
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("INSERT INTO clientes (NOMBRE,APELLIDO,TELEFONO,PATENTE,HORA,FECHA,KILOMETROS,AUTO) VALUES (%s, %s, %s,%s, %s, %s,%s, %s)", 
        (nombre, apellido, int(telefono), patente, hora, fecha, kilometros, auto)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
        flash("cliente agregado satifactoriamente") #envia mesajes entre vistas
        return redirect(url_for("index")) #hago que se vuelva a cargar index.html al agregar un contacto


@app.route("/buscln", methods=["POST"])
def buscln():
    nombre = request.form["nombre"]
    print(nombre)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CLIENTES WHERE NOMBRE = %s", (nombre,))
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    return render_template("clientes.html", contactos=data)


@app.route("/busclp", methods=["POST"])
def busclp():
    patente = request.form["codigo"]
    print(patente)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CLIENTES WHERE PATENTE = %s", (patente,))
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    return render_template("clientes.html", contactos=data)

@app.route("/buscla", methods=["POST"])
def buscla():
    auto = request.form["codigo"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM CLIENTES WHERE AUTO = %s", (auto,))
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    return render_template("clientes.html", contactos=data)


@app.route("/elimclient/<string:id>")#recibo un parametro tipo string
def elimclient(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM CLIENTES WHERE id = %s", (id,))
    mysql.connection.commit() #guardo los cambios
    flash("cliente eliminado satifactoriamente") #envia mesajes entre vistas
    return redirect(url_for("index"))


##########################################################################
######################REDIRIGE A PANTALLA DE STOCK########################
##########################################################################


@app.route("/a_stock", methods=["POST"])
def a_stock():
    return render_template("stock.html")


##########################################################################
######################BUSQUEDA POR NOMBRE PARPANTALLA STOCK###############
##########################################################################


@app.route("/buscarns", methods=["POST"])
def buscs():
    nombre = request.form["nombre"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE PRODUCTO LIKE '"+nombre+" %' OR PRODUCTO LIKE '% "+nombre+" %' OR PRODUCTO LIKE '% "+nombre+"' ")
    data = cur.fetchall()#resultado de la busqueda en la base de datos
    return render_template("stock.html", contactos=data)


##########################################################################
######################BUSQUEDA POR CODIGO PARPANTALLA STOCK###############
##########################################################################

@app.route("/buscarcs", methods= ["POST"])
def busccods():
    if request.method == "POST":
        codigo = request.form["codigo"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
        data = cur.fetchall()
        return render_template("stock.html", contactos=data)


##########################################################################
######################CAMBIAR CANTIDAD EN STOCK DE UN ARTICULO############
##########################################################################

@app.route("/masstock/<codigo>", methods=["POST"])
def aumentars(codigo):
    aumstock = request.form["aumstock"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM PRODUCTOS WHERE CODIGO like '" +codigo+ "'")
    data = cur.fetchall()
    data=list(data[0])
    stock_nuevo=int(data[2])+int(aumstock)
    cur.execute("""
                    UPDATE PRODUCTOS
                    SET CANTIDAD = %s
                    WHERE CODIGO=%s
        """,(stock_nuevo, codigo,)) #hago la consulta SQL
    mysql.connection.commit() #guardo los cambios
    flash("STOCK MODIFICADO!!!!!!") #envia mesajes entre vistas
    return render_template("stock.html")


    ##########################################################################
    ######################CAMBIO DE PRECIO DE UN ARTICULO#####################
    ##########################################################################


##########################################################################
######################CAMBIA PRECIO A UN ARTICULO#########################
##########################################################################

@app.route("/camprecio/<codigo>", methods=["POST"])
def camprecio(codigo):
    price = request.form["price"]
    cur = mysql.connection.cursor()
    cur.execute("""
                    UPDATE PRODUCTOS
                    SET PRECIO = %s
                    WHERE CODIGO=%s
        """,(float(price), codigo,)) #hago la consulta SQL
    mysql.connection.commit() #guardo los cambios
    flash("PRECIO MODIFICADO!!!!!!") #envia mesajes entre vistas
    return render_template("stock.html")


##########################################################################
###############################AGREGA UN ARTICULO#########################
##########################################################################

@app.route("/Aarticulo")
def Aarticulo():
    return render_template("Aarticulo.html")

@app.route("/add_product", methods=['POST'])
def add_producto():
    if request.method == "POST":
        producto = request.form["producto"]
        codigo = request.form["codigo"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]
        cur = mysql.connection.cursor() #me conecto con la BDD
        cur.execute("INSERT INTO PRODUCTOS (PRODUCTO,CODIGO,CANTIDAD,PRECIO) VALUES (%s, %s, %s,%s)", 
        (producto, codigo, cantidad, precio)) #hago la consulta SQL
        mysql.connection.commit() #guardo los cambios
        flash("Producto agregado satifactoriamente") #envia mesajes entre vistas
        return redirect(url_for("Aarticulo")) #hago que se vuelva a cargar index.html al agregar un contacto

    
if __name__ == "__main__":
    app.run(port = 3000, debug = True) #hacemos que se refresque solo
