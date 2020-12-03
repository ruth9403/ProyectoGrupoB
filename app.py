from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)

# Añado la ruta por defecto
@app.route("/")
def index():

    return render_template("index.html")

@app.route("/Recuperar")
def Recuperar():

    return render_template("recuperacion1.html")
@app.route("/MisBlogs")
def MisBlogs():

    return render_template("MisBlogs.html")

@app.route("/Recuperar2")
def Recuperar2():

    return render_template("recuperacion2.html")
@app.route("/header")
def header():

    return render_template("header.html")

@app.route("/registro")
def registro():

    return render_template("registro.html")




