import re
from validate_email import validate_email
from functools import wraps
from flask import redirect, render_template, request, session
import urllib.request

pass_reguex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^\W_]{8,}$"
user_reguex = "^[a-zA-Z0-9_.-]+$"

def isEmpty(string):
    
    return string == "",  "Debe ingresar un usuario y contraseña para iniciar sesión"

def validateUser(username, password):

    # Aquí pondremos la validación con la base de datos

    if username == "usuario" and password == "123":

        return True
    
    else:
        return False

def Equals(a,b):

    return  a == b, "Los campos no coinciden" 


def isEmailValid(email):
    is_valid = validate_email(email)

    return is_valid, "Correo inválido"

def isUsernameValid(user):
    if re.search(user_reguex, user):
        return True, ""
    else:
        return False, "Usuario inválido"

def isPasswordValid(password):

    # Confirmar que la contraseña t
    if re.search(pass_reguex, password):
        return True, ""
    else:
        return False, "Contraseña inválida, necesita mínimo 8 caracteres, una mayúscula y un número"

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function