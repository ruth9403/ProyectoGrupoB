from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from utils import validateUser

app = Flask(__name__)

# Añado la ruta por defecto
@app.route("/", methods = ["GET", "POST"])
def index():

    if request.method =="GET":
        
        return render_template("index.html", visible = False)

    else:
        username = request.form.get("usuario")
        password = request.form.get("pass")

        print(username, password)

        validUser = validateUser(username, password)

        if validUser:
            return redirect("/MisBlogs")
        else:

            mensaje = "Usuario no registrado"

            if username == "":
                mensaje = "Ingrese un nombre de usuario válido"
            
            elif password == "":
                mensaje = "Ingrese una contraseña válida"

            return render_template("index.html", visible = True, mensaje= mensaje)



@app.route("/Recuperar")
def Recuperar():

    if request.method =="GET":
        return render_template("recuperacion1.html")
    
    else: 

        correo = request.form.get("correo")

        # Enviar correo de validación

        return redirect("/Recuperar2")

@app.route("/MisBlogs")
def MisBlogs():
    
    return render_template("MisBlogs.html")

@app.route("/Recuperar2", methods = ["GET", "POST"])
def Recuperar2():

    if request.method =="GET":
        return render_template("recuperacion2.html")
    
    else:

        newpass = request.form.get("password")
        confirmpass = request.form.get("password2")

        # Validación de que ambas contraseñas sen las mismas

        if newpass == confirmpass:

            # Hacer un update a la base de datos

            # Si las contraseñas coinciden redirijo al usuario a la pagina de inicio para que se loguee
            return redirect("/")
        
        #else:

            # Alarm con Js o label en rojo




@app.route("/header")
def header():

    return render_template("header.html")

@app.route("/registro", methods = ["GET", "POST"])
def registro():

    if request.method == "GET":
        return render_template("registro.html")
    
    else:

        username = request.form.get("username")
        correo = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("passCheck")

        # Insertar validaciones de la profesora
        # Verificar que la contraseña y su confirmación sean iguales
        if password == confirm:

            # Estos datos deben usarse para hacer un insert en la tabla de usuarios en la base de datos

            # Llamar un alert de js para avisar que ha sido registrado

            return redirect("/")
        
        #else: 
            # Alert o label para avisar que las contraseñas no coincideno que alguna
            # de las validaciones no paso


@app.route("/resultados")
def resultados():

    return render_template("resultados.html")

    




