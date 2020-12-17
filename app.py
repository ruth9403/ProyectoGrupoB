from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from tempfile import mkdtemp
from utils import validateUser, Equals, isEmailValid, isUsernameValid, isPasswordValid, isEmpty, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL 
from datetime import date
import sqlite3
from datetime import date


app = Flask(__name__)

# Asegurarse de Recargar templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Asegúrese de que las respuestas no se almacenen en caché
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configurar la sesión para usar el sistema de archivos (en lugar de cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configurar librería CS50 para trabajar con la base de datos
db = SQL("sqlite:///BLOG_B.db")

# Añado la ruta por defecto (Index)
@app.route("/", methods = ["GET", "POST"])
def index():

    session.clear()

    if request.method =="GET":
        
        return render_template("index.html", visible = False, mensaje = "")

    else:
        
        textBuscar = request.form.get("barra_busqueda")
        username = request.form.get("usuario")
        password = request.form.get("pass")

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
        # la persona esté registrada.

        # Query a la base de datos para verificar username
        rows = db.execute("SELECT * FROM usuario WHERE user_name = :username",
                          username=username)

        if len(rows) != 1 or not check_password_hash(rows[0]["contrasena"], password):
            mensaje = "Usuario no registrado"
            return render_template("index.html", visible = True, mensaje= mensaje)
        else:
            session["user_id"] = rows[0]["id_usuario"]
            return redirect("/MisBlogs")


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
        
        today = date.today()
        dt_string = today.strftime("%Y/%m/%d")

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

        hash_pass = generate_password_hash(password)
        try:
            with sqlite3.connect("BLOG_B.db") as con:
                cur = con.cursor() #Manipula la conexión a la bd
                cur.execute("INSERT INTO usuario (nombre, apellido, user_name, contrasena, correo, fecha_ingreso) VALUES (?,?,?,?,?,?)",
                            (username, username, username, hash_pass, correo, dt_string))
                con.commit() #confirma la sentencia
                return redirect("/")
        except :
            con.rollback()

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

        #Se revisa que exista el correo en la base de datos
        try:
            with sqlite3.connect("BLOG_B.db") as con:
                cur = con.cursor() #Manipula la conexión a la bd
                cur.execute("SELECT * FROM usuario WHERE correo = ?", correo)
                con.commit() #confirma la sentencia
                row = cur.fetchone()
                if row is None:
                    flash("Correo no se encuentra registrado en la BD")
                    print("Correo no se encuentra registrado en la BD")
                return render_template("recuperacion1.html", visible = True, mensaje= mensaje)
        except :
            con.rollback()
    return redirect("/")

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
@login_required
def resultados():

    return render_template("resultados.html")

# Página para hacer búsquedas cuando se ha iniciado sesión
@app.route("/buscar", methods = ["GET", "POST"])
@login_required
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
@login_required
def MisBlogs():

    if request.method == "GET":

        # Query a la base de datos para obtener los blogs del usuario
        usuario = session["user_id"]

        userBlogs = db.execute("SELECT * FROM publicacion WHERE id_usuarioPub = :idUser",
                          idUser=usuario)

        print(userBlogs)
        
        if len(userBlogs) == 0:
            mensaje = "No tienes ningún blog asociado a tu cuenta"
            return render_template("MisBlogs.html", userBlogs = userBlogs)

        else:
            return render_template("MisBlogs.html", userBlogs = userBlogs)
    
    else:

        # Pregunto qué botón hizo el request, eliminar o editar
        btnEditar = request.form.get("Editar")
        btnEliminar = request.form.get("Eliminar")
        btnAgregar = request.form.get("agregar")

        if btnAgregar != "" and btnAgregar != None:
            return redirect("/nuevoBlog")

        if btnEliminar == "" or btnEliminar == None:
            blogId = btnEditar.split(",")[1]
            return redirect("/Editar", blogId = blogId)

        else:
            
            blogId = btnEliminar.split(",")[1]
            # Hacer delete a la base de datos
            try:
                with sqlite3.connect("BLOG_B.db") as con:
                    cur = con.cursor() #Manipula la conexión a la bd
                    cur.execute("DELETE FROM publicacion WHERE id_publicacion = ?", blogId)
                    con.commit() #confirma la sentencia
                    return "Blog Borrado"
            except :
                con.rollback()       
            
            return redirect("/MisBlogs")




# Página para mostrar el detalle de un blog, los titulos son un anchor
# y al darles click nos envían acá, enviando el ID específico del blog
# al que el usuario ha dado click
@app.route("/blog", methods = ["GET", "POST"])
@login_required
def header():
    if request.method == "GET":
        return render_template("detalleBlog.html")
    else:

        comentario = request.form.get("nuevoComentario")
        usuario = session["user_id"]
        id_publicacionCom = 1
        today = date.today()
        dt_string = today.strftime("%Y/%m/%d")
        try:
            with sqlite3.connect("BLOG_B.db") as con:
                cur = con.cursor() #Manipula la conexión a la bd
                cur.execute("INSERT INTO comentario (fecha_publicacionCom, cuerpo_comentario) VALUES (?,?)",
                            ("", comentario))
                con.commit() #confirma la sentencia
                return "Comentario publicado"
        except :
            con.rollback()       


        return render_template("detalleBlog.html")

@app.route("/blog_sinSesion")
def blog_sinsesion():
    return render_template("detalleBlog_SinSesion.html")

# Página para edición de un blog particular
@app.route("/Editar", methods = ["GET", "POST"])
@login_required
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
            # Hacer update en la base de datos ## debe ser la misma de crear blog
            editblog = session["id_publicacion"]
            try:
                with sqlite3.connect("BLOG_B.db") as con:
                    cur = con.cursor() #Manipula la conexión a la bd
                    cur.execute("UPDATE FROM publicacion WHERE id_publicacion = ?", editblog)
                    con.commit() #confirma la sentencia
                    return "Blog Actualizado"
            except :
                con.rollback()       
            return redirect("/MisBlogs")

# Ruta para agregar un nuevo blog
@app.route("/nuevoBlog", methods = ["GET", "POST"])
@login_required
def nuevoBlog():
    if request.method == "GET":
        return render_template("nuevoBlog.html")
    else:
        return render_template("nuevoBlog.html")

# Cerrar sesión
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True, port=8000)











    
