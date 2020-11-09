# Imports the Flask framework
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# Imports the data from data.py
from data import todos

from flask_mysqldb import MySQL

from wtforms import Form, StringField, TextAreaField, PasswordField, validators

from passlib.hash import sha256_crypt

# Create an instance of the flask Class
app = Flask(__name__)



app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "as123456"
app.config["MYSQL_DB"] = "todoapp"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Var for data in data.py
Todos = todos()

# Default route
@app.route("/")
def index():
    return render_template("home.html")

# About route
@app.route("/about")
def about():
    return render_template("about.html")
# Todos route
@app.route("/todos")
def todos():
    return render_template("todos.html", todos=Todos)

# Individial todo route
@app.route("/todo/<string:id>/")
def todo(id):
    return render_template("todo.html", id=id)

class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    # email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match")
    ])
    confirm = PasswordField("Confirm Password")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        # email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, username, password) VALUES(%s, %s, %s)", (name, username, password))

        mysql.connection.commit()

        cur.close()

        flash("You are now registered!", "success")

        return redirect(url_for("login"))

    return render_template("register.html", form=form)

# Runs the flask application, debug parameter auto-retarts the server after changes
if __name__ == "__main__":
    app.secret_key="secrets"
    app.run(debug=True)