from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from tempfile import mkdtemp
from utils import validateUser, Equals, isEmailValid, isUsernameValid, isPasswordValid, isEmpty, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL 
from datetime import date
import sqlite3
from datetime import date
from flask_mail import Mail#-------------*R
from flask_mail import Message#-------------*R
import secrets#-------------*R

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

#Configurando servidor SMTP#-------------*R
app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'misionticgrupob@gmail.com'
app.config['MAIL_USE_TLS'] = True                                    
app.config['MAIL_PASSWORD'] = 'Clavefalsa1234' #-------------*R
app.config['SECRET_KEY'] = 'H{va#rM!&P!8BAinVO/L!?t:g~dv1'  
Session(app)
mail = Mail(app)#-------------*R

# Configurar librería CS50 para trabajar con la base de datos
db = SQL("sqlite:///BLOG_B.db")

# Añado la ruta por defecto (Index)
@app.route("/", methods = ["GET", "POST"])
def index():

    session.clear()

    if request.method =="GET":
        
        return render_template("index.html", visible = False, mensaje = "")

    else:
        
        search = request.form.get("barra_busqueda")
        username = request.form.get("usuario")
        password = request.form.get("pass")
        boton = request.form.get("boton")

        # Pregunto si el botón que hace el submit es el de buscar, sino lo hizo el de iniciar sesión
        if boton == "Buscar":

            # Hacer select de la base de datos segun lo que esté en la barra de busqueda
            # pasar un diccionario con los resultados
            # Valor del campo 

            blogs = db.execute(f"SELECT * FROM publicacion WHERE es_publico = 1 and (titulo LIKE '%%{search}%%' or cuerpo LIKE '%%{search}%%')")
            cant = len(blogs)

            for blog in blogs:
                blog["usuario"] = db.execute("SELECT nombre FROM usuario WHERE id_usuario = :idUser",idUser= blog["id_usuarioPub"])[0]["nombre"]

            return render_template("resultados_sinsesion.html", blogs = blogs, cant = cant)

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
                token = secrets.token_urlsafe()#-------------*R
                guadarTokenBD(token, correo, username)
                enviarMail(correo, crearURL(token,username))#-------------*R
                return redirect("/RegistroExitoso")
        except :
            con.rollback()

        return redirect("/")

# Ruta para que el usuario sepa que se ecuentra registrado
@app.route("/RegistroExitoso", methods = ["GET", "POST"])
def RegistroExitoso():
    return render_template("usuarioRegistrado.html")



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

        #Se revisa que exista el correo en la base de datos#-------------*R
        try:
            with sqlite3.connect("BLOG_B.db") as con:
                cur = con.cursor() #Manipula la conexión a la bd
                print('Entreeeee')
                cur.execute("SELECT * FROM usuario WHERE correo=?", [correo])
                print('buscoooo')
                #con.commit() #confirma la sentencia
                row = cur.fetchone()
                print('traje esto', row)
                if row is None:
                    flash("Correo no se encuentra registrado en la BD")
                    print("Correo no se encuentra registrado en la BD")
                    return render_template("recuperacion1.html", visible = True, mensaje= mensaje)
                else:
                    print('ENTRE AL ELSE')
                    cur.execute("SELECT * FROM token WHERE correo_usuario=?", [correo])
                    row2 = cur.fetchone()
                    print('traje esto otro de token', row2)
                    print(row2[1])
                    enviarMailRecup(correo, crearURLRecup(row2[1],row2[3]))
                    #enviarMail(correo, crearURL(token,username))
        except :
            con.rollback()
        return redirect("/verificacion")
    return redirect("/")#-------------*R

# Ruta para la segunda página de recuperación de contraseña (donde se avisa al usuario que se ha enviado un correo)
@app.route("/verificacion", methods = ["GET", "POST"])
def verificacion():

    if request.method == "GET":
        return render_template("paginaVerificacionCorreo.html")


# Ruta para la tercera página de recuperación de contraseña (donde se hace cambio de contraseña)
@app.route("/Recuperar2/<string:usuario>", methods = ["GET", "POST"])#-------------*R
def Recuperar2(usuario):

    if request.method =="GET":
        return render_template("recuperacion2.html", visible = False, mensaje = "", usuario = usuario)
    
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
        
        hash_pass = generate_password_hash(newpass)
        db.execute('UPDATE usuario SET contrasena=? WHERE nombre=?', hash_pass, usuario)


        # Si las contraseñas coinciden redirijo al usuario a la pagina de inicio para que se loguee
        return redirect("/")#-------------*R


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

        if clave == "" or clave == None:
            mensaje = "Ingresar al menos una palabra clave para la búsqueda"
            return render_template("paginaBusqueda copy.html", visible = True, mensaje = mensaje)

        blogs = db.execute(f"SELECT * FROM publicacion WHERE (titulo LIKE '%%{clave}%%' or cuerpo LIKE '%%{clave}%%')")
        cant = len(blogs)

        for blog in blogs:
            blog["usuario"] = db.execute("SELECT nombre FROM usuario WHERE id_usuario = :idUser",idUser= blog["id_usuarioPub"])[0]["nombre"]

        return render_template("resultados.html", blogs = blogs, cant = cant)


# Página de los blogs del usuario logueado
@app.route("/MisBlogs", methods = ["GET", "POST"])
@login_required
def MisBlogs():

    if request.method == "GET":

        # Query a la base de datos para obtener los blogs del usuario
        usuario = session["user_id"]

        userBlogs = db.execute("SELECT * FROM publicacion WHERE id_usuarioPub = :idUser",
                          idUser=usuario)
        
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
            return redirect(f"/Editar_b/{blogId}")

        else:
            
            blogId = btnEliminar.split(",")[1]
            # Hacer delete a la base de datos
            try:
                with sqlite3.connect("BLOG_B.db") as con:
                    cur = con.cursor() #Manipula la conexión a la bd
                    cur.execute("DELETE FROM publicacion WHERE id_publicacion = ?", blogId)
                    con.commit() #confirma la sentencia
                    return redirect("/MisBlogs")
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
        blog = {"titulo": "abc", "cuerpo": "cuerpo axc"}
        render_template("detalleBlog.html", blog = blog)
    else:
        return render_template("detalleBlog.html")

@app.route('/blog/<int:id>', methods = ["GET", "POST"] )
@login_required
def DetalleBlog(id):

    if request.method == "GET":
        blog = db.execute("SELECT * FROM publicacion WHERE id_publicacion = :id_publicacionCom", id_publicacionCom=id)
        blog = blog[0]

        comentarios = db.execute("SELECT * FROM comentario WHERE id_publicacionCom = :id", id=id)


        for comentario in comentarios: 

            comentario["usuario"] = db.execute("SELECT user_name FROM usuario WHERE id_usuario = :id_user", id_user=comentario["id_usuarioCom"])[0]["user_name"]

        
        return render_template("detalleBlog.html", blog = blog, comentarios = comentarios)

    else:
        comentarioN = request.form.get("nuevoComentario")
        usuario = session["user_id"]
        id_publicacionCom = id
        today = date.today()
        dt_string = today.strftime("%Y/%m/%d")
        try:
            with sqlite3.connect("BLOG_B.db") as con:
                cur = con.cursor() #Manipula la conexión a la bd
                cur.execute("INSERT INTO comentario (id_usuarioCom, fecha_publicacionCom, cuerpo_cometario, id_publicacionCom) VALUES (?,?,?,?)",
                            (usuario, dt_string, comentarioN, id_publicacionCom))
                con.commit() #confirma la sentencia
                return redirect('/blog/' + str(id))
        except :
            con.rollback()       

        return redirect('/blog/' + str(id))


@app.route('/blog_sinsesion/<int:id>', methods = ["GET", "POST"])
def DetalleBlog_sinsesion(id):

        if request.method == "GET":

            blog = db.execute("SELECT * FROM publicacion WHERE id_publicacion = :id_publicacionCom", id_publicacionCom=id)
            blog = blog[0]

            return render_template("detalleBlog_SinSesion.html", blog = blog)

@app.route('/blog_consesion/<int:id>', methods = ["GET", "POST"])
@login_required
def DetalleBlog_consesion(id):

        blog = db.execute("SELECT * FROM publicacion WHERE id_publicacion = :id_publicacionCom", id_publicacionCom=id)
        blog = blog[0]

        return render_template("detalleBlog.html", blog = blog)


@app.route("/Editar_b/<int:id>", methods = ["GET", "POST"])
@login_required
def Editar_b(id):

    if request.method == "GET":
        blog = db.execute("SELECT * FROM publicacion WHERE id_publicacion = :id_publicacionCom", id_publicacionCom=id)[0]

        return render_template("edicionBlog.html", blog = blog)

    else:
        # Pregunto si el botón de request es el de guardar o el de cancelar
        btnGuardar = request.form.get("Guardar")
        btnCancelar = request.form.get("Cancelar")

        if btnCancelar == "Cancelar":
            return redirect("/MisBlogs")

        if btnGuardar == "Guardar":
            # Hacer update en la base de datos ## debe ser la misma de crear blog
            titulo = request.form.get("titulo")
            contenido = request.form.get("contenido")
            today = date.today()
            fecha = today.strftime("%Y/%m/%d")
            publico = 1 if request.form.get("publico") == 'on' else 0

            db.execute("UPDATE publicacion SET titulo = ?, cuerpo = ?, es_publico = ?, fecha_publicacion = ?  WHERE id_publicacion = ?", titulo, contenido, publico, fecha, id)
            
            return redirect("/MisBlogs")


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

            ## AQUI FALTA OBTENER EL ID DEL BOTON
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
        btnCancelar = request.form.get("Cancelar")
        btnGuardar = request.form.get("Guardar")

        if btnGuardar == "" or btnGuardar == None:

            return redirect("/MisBlogs")
        else:
            #Obtengo todos los campos necesarios para insertar un nuevo blog
            titulo = request.form.get("titulo")
            encabezado = request.form.get("encabezado")
            contenido = request.form.get("contenido")
            publico = request.form.get("publico")
            publico = publico == 'on'
            today = date.today()
            dt_string = today.strftime("%Y/%m/%d")
            categoria = 1
            usuario = session["user_id"]
        
            db.execute("INSERT INTO publicacion (titulo, cuerpo, es_publico, fecha_publicacion, \
                id_categoriaPub, id_usuarioPub) VALUES (:titulo,:cuerpo, :publico, :fecha, \
                    :categoria, :usuario)", titulo = titulo, cuerpo = contenido, publico = publico,
                    fecha = dt_string, categoria = categoria, usuario = usuario)
        
            return redirect("/MisBlogs")

        return render_template("nuevoBlog.html")

# Cerrar sesión
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

#-------------*R
#http://127.0.0.1:8000/confirmacion/jaaviles@uninorte.edu.co?token=TGWWVTJUEVDAcddIPzHkUQgA5u1t_NUYqiL5WKayXNc
@app.route("/confirmacion/<string:usuario>")
def confirmar(usuario):
    try:
        with sqlite3.connect("BLOG_B.db") as con:
            cur = con.cursor() #Manipula la conexión a la bd
            cur.execute("UPDATE usuario SET estado_activacion = ? WHERE user_name=?", (True, usuario))
            con.commit() #confirma la sentencia
    except :
        con.rollback()
    return render_template("cuentaActivada.html")

def enviarMail(correo, url):
    msg = Message("Activa tu cuenta!",
                  sender='misionticgrupob@gmail.com',
                  recipients=[correo])
    #msg.body = f'Para activar tu cuenta por favor sigue el siguiente link {url}'
    msg.html = render_template("mail_newUSer.html", visible = True, mensaje = url)
    mail.send(msg)
    return msg.html

def crearURL(token,usuario):
    url = f'http://ec2-54-167-130-1.compute-1.amazonaws.com/confirmacion/{usuario}?token={token}'
    print('si cree la URL')
    return url

def guadarTokenBD(token,correo, usuario):
    try:
        with sqlite3.connect("BLOG_B.db") as con:
            cur = con.cursor() #Manipula la conexión a la bd
            cur.execute("INSERT INTO token (token, correo_usuario, usuario) VALUES (?,?,?)",
                        (token, correo, usuario))
            con.commit() #confirma la sentencia
    except :
        con.rollback()

def enviarMailRecup(correo, url):
    msg = Message("Recupera tu cuenta!",
                  sender='misionticgrupob@gmail.com',
                  recipients=[correo])
    #msg.body = f'Para activar tu cuenta por favor sigue el siguiente link {url}'
    msg.html = render_template("mail_recuperaCont.html", visible = True, mensaje = url)
    mail.send(msg)
    return msg.html


def crearURLRecup(token,usuario):
    url = f'http://ec2-54-167-130-1.compute-1.amazonaws.com/Recuperar2/{usuario}'
    print('si cree la URL')
    return url



@app.route("/testEmail")
def testEmail():
    return enviarMail('ruthy9403@gmail.com', crearURL('QYcIBzoUhrgiicMP7EuXOYF5I68ooLPP0rJEfBVE6hI','alcohol'))
#-------------*R


if __name__ == "__main__":
    app.run(debug = True, port=8000)











    
