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



