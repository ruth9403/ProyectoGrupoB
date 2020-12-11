from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from utils import validateUser, Equals, isEmailValid, isUsernameValid, isPasswordValid, isEmpty

app = Flask(__name__)

# Añado la ruta por defecto (Index)
@app.route("/", methods = ["GET", "POST"])
def index():

    if request.method =="GET":
        
        return render_template("index.html", visible = False, mensaje = "")

    else:
        
        textBuscar = request.form.get("barra_busqueda")
        username = request.form.get("usuario")
        password = request.form.get("pass")
        print(textBuscar, username, password)

        # Reconocemos que el usuario quiere hacer ubna búsqueda porque
        # el cuadro de búsqueda tiene al menos un caracter
        # mientras que no llega nada por parte del input usuario y el 
        # de contraseña
        if textBuscar != "" and (username == None or username == "") and (password == None or password == ""):

            # Hacer select de la base de datos segun lo que esté en la barra de busqueda
            # pasar un diccionario con los resultados

            return redirect("/resultados_sinsesion")

        # Las validaciones que se hacen para iniciar sesión son:

        # 1. Verificar que no estén vacios los campos (inputs de texto)
        userEmpty, mensaje = isEmpty(username) 
        passEmpty, mensaje = isEmpty(password)

        if userEmpty or passEmpty:
            return render_template("index.html", visible = True, mensaje = mensaje)

        # 2. Si los campos no están vacios se verificará en la base de datos que
        # la persona esté registrada. Por ahora solo validamos el usuario con valores
        # fijos (Usuario = usuario, password = 123)
        validUser = validateUser(username, password)

        # Si es un usuario válido se redirige a sus blogs
        if validUser:
            return redirect("/MisBlogs")
        else:

            mensaje = "Usuario no registrado"
            return render_template("index.html", visible = True, mensaje= mensaje)

# Ruta para la página de registro
@app.route("/registro", methods = ["GET", "POST"])
def registro():

    if request.method == "GET":
        return render_template("registro.html", visible = False, mensaje ="")
    
    else:

        username = request.form.get("username")
        correo = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("passCheck")

        visible = False

        validUsuario, mensaje = isUsernameValid(username)
        if not validUsuario:
            visible = True
            return render_template("registro.html", visible = True, mensaje =mensaje)

        validCorreo, mensaje = isEmailValid(correo)    
        if not validCorreo:
            visible = True
            return render_template("registro.html", visible = True, mensaje =mensaje)

        validpassword, mensaje = isPasswordValid(password)    
        if not validpassword:
            visible = True
            return render_template("registro.html", visible = True, mensaje =mensaje)

        equals, mensaje = Equals(password, confirm)
        if not equals:
            visible = True
            return render_template("registro.html", visible = True, mensaje =mensaje)


        # Estos datos deben usarse para hacer un insert en la tabla de usuarios en la base de datos


        return redirect("/")

# Ruta para la primera página de recuperación de contraseña (donde se pide el correo)
@app.route("/Recuperar", methods = ["GET", "POST"])
def Recuperar():

    if request.method =="GET":
        return render_template("recuperacion1.html", visible = False, mensaje = "")
    
    else: 

        correo = request.form.get("correo")
        validCorreo, mensaje = isEmailValid(correo)

        if not validCorreo:
            return render_template("recuperacion1.html", visible = True, mensaje = mensaje)

        return redirect("/verificacion")


# Ruta para la segunda página de recuperación de contraseña (donde se avisa al usuario que se ha enviado un correo)
@app.route("/verificacion", methods = ["GET", "POST"])
def verificacion():

    if request.method == "GET":
        return render_template("paginaVerificacionCorreo.html")


# Ruta para la tercera página de recuperación de contraseña (donde se hace cambio de contraseña)
@app.route("/Recuperar2", methods = ["GET", "POST"])
def Recuperar2():

    if request.method =="GET":
        return render_template("recuperacion2.html", visible = False, mensaje = "")
    
    else:

        newpass = request.form.get("password")
        confirmpass = request.form.get("password2")

        # Validación 1: La contraseña nueva debe cumplir con las validaciones
        # de contraseña usadas para registro

        validnewPass, mensaje = isPasswordValid(newpass)
        validConfirmPass, mensaje = isPasswordValid(confirmpass)

        if not validnewPass or not validConfirmPass:
            return render_template("recuperacion2.html", visible = True, mensaje = mensaje)

        # Validación 2: Si ambos campos cumplen con las validaciones de contraseña para
        # registro ahora se debe verificar que ambos campos coincidan
        validPass, mensaje = Equals(newpass, confirmpass)

        if not validPass:
            # Debe ir un update a la base de datos
            return render_template("recuperacion2.html", visible = True, mensaje = mensaje)
            
        # Si las contraseñas coinciden redirijo al usuario a la pagina de inicio para que se loguee
        return redirect("/")


# Resultados de búsqueda de blogs cuando no se ha iniciado sesión
@app.route("/resultados_sinsesion", methods = ["GET", "POST"])
def resultados_sinsesion():

    return render_template("resultados_sinsesion.html")

# Resultados de búsqueda de blogs cuando se ha iniciado sesión
@app.route("/resultados", methods = ["GET", "POST"])
def resultados():

    return render_template("resultados.html")

# Página para hacer búsquedas cuando se ha iniciado sesión
@app.route("/buscar", methods = ["GET", "POST"])
def buscar():

    if request.method == "GET":
        return render_template("paginaBusqueda copy.html", visible = False, mensaje = "")

    else:

        clave = request.form.get("clave")

        if clave == "":
            mensaje = "Ingresar al menos una palabra clave para la búsqueda"
            return render_template("paginaBusqueda copy.html", visible = True, mensaje = mensaje)

        # Aquí se haría un select condicionado a la base de datos para traer coincidencias 
        # y se enviaría a la página como diccionario para mostrar los resultados

        return redirect("/resultados")


# Página de los blogs del usuario logueado
@app.route("/MisBlogs", methods = ["GET", "POST"])
def MisBlogs():

    if request.method == "GET":
        return render_template("MisBlogs.html")
    
    else:

        # Pregunto qué botón hizo el request, eliminar o editar
        btnEditar = request.form.get("Editar")
        btnEliminar = request.form.get("Eliminar")
        
        if btnEditar == "Editar":
            return redirect("/Editar")

        if btnEliminar == "Eliminar":
            # Hacer delete a la base de datos
            return redirect("/MisBlogs")


# Página para mostrar el detalle de un blog, los titulos son un anchor
# y al darles click nos envían acá, enviando el ID específico del blog
# al que el usuario ha dado click
@app.route("/blog")
def header():
    return render_template("detalleBlog.html")

@app.route("/blog_sinSesion")
def blog_sinsesion():
    return render_template("detalleBlog_SinSesion.html")

# Página para edición de un blog particular
@app.route("/Editar", methods = ["GET", "POST"])
def Editar():

    if request.method == "GET":
        return render_template("edicionBlog.html")

    else:

        # Pregunto si el botón de request es el de guardar o el de cancelar
        btnGuardar = request.form.get("Guardar")
        btnCancelar = request.form.get("Cancelar")

        if btnCancelar == "Cancelar":
            return redirect("/MisBlogs")
        
        if btnGuardar == "Guardar":
            # Hacer update en la base de datos
            return redirect("/MisBlogs")











    
