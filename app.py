# Imports
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Create an instance of the flask Class
app = Flask(__name__)


# Configure applicaiton for MySQL DB
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "as123456"
app.config["MYSQL_DB"] = "todoapp"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


"""
ROUTES
"""
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
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Todos
    results = cur.execute("SELECT * FROM todos")

    todos = cur.fetchall()

    if results > 0:
        return render_template("todos.html", todos=todos)
    else:
        msg = "No To-Dos Fount"
        return render_template("todos.html", msg=msg)

    cur.close()


# Individial todo route
@app.route("/todo/<string:id>/")
def todo(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Todos
    results = cur.execute("SELECT * FROM todos WHERE id = %s", [id])

    todos = cur.fetchone()

    return render_template("todo.html", todos=todos)


# Registration form schema
class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match")
    ])
    confirm = PasswordField("Confirm Password")


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Add to-do into DB
        cur.execute("INSERT INTO users(name, username, password) VALUES(%s, %s, %s)",
                    (name, username, password))

        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("You are now registered!", "success")

        return redirect(url_for("login"))

    return render_template("register.html", form=form)


# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form fields
        username = request.form["username"]
        passwords = request.form["password"]

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute(
            "SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data["password"]

            # Compare passwords
            if sha256_crypt.verify(passwords, password):
                # app.logger.info("PASSWORD MATCHED")
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))

            else:
                error = "Invalid Username and/or Password"
                return render_template("login.html", error=error)

            # Close connection
            cur.close()

        else:
            error = "Username not found"
            return render_template("login.html", error=error)

    return render_template("login.html")


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Need to be logged in", "danger")
            return redirect(url_for("login"))
    return wrap

# Lougout route
@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out!", "success")
    return redirect(url_for("login"))

# Dashboard route
@app.route("/dashboard")
@is_logged_in
def dashboard():

    # Create cursor
    cur = mysql.connection.cursor()

    # Get Todos
    results = cur.execute("SELECT * FROM todos")

    todos = cur.fetchall()

    if results > 0:
        return render_template("dashboard.html", todos=todos)
    else:
        msg = "No To-Dos Fount"
        return render_template("dashboard.html", msg=msg)

    cur.close()


class ToDoForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=4)])


# Add a to-do route
@app.route("/add_todo", methods=["GET", "POST"])
@is_logged_in
def add_todo():
    form = ToDoForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO todos(title, body, author) VALUES(%s, %s, %s)",
                    (title, body, session["username"]))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("To-Do Created!", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_todo.html", form=form)


# Edit a todo route
@app.route("/edit_todo/<string:id>", methods=["GET", "POST"])
@is_logged_in
def edit_todo(id):

    # Create cursor
    cur = mysql.connection.cursor()

    # Get to-do by id
    result = cur.execute("SELECT * FROM todos WHERE id = %s", [id])

    todo = cur.fetchone()

    # Get form
    form = ToDoForm(request.form)

    # Populate article form fields
    form.title.data = todo["title"]
    form.body.data = todo["body"]

    app.logger.info(form.title.data)

    if request.method == "POST" and form.validate():
        title = request.form["title"]
        body = request.form["body"]

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "UPDATE todos SET title=%s, body=%s WHERE ID = %s", (title, body, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("To-Do Created!", "success")

        return redirect(url_for("dashboard"))

    return render_template("edit_todo.html", form=form)


# Delete To-do
@app.route("/delete_todo/<string:id>", methods=["POST"])
@is_logged_in
def delete_todo(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM todos WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    # Close connection
    cur.close()

    flash("To-do Deleted!", "success")

    return redirect(url_for("dashboard"))


# Runs the flask application, debug parameter auto-retarts the server after changes
if __name__ == "__main__":
    app.secret_key = "secrets"
    app.run(debug=True)
