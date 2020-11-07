# Imports the Flask framework
from flask import Flask, render_template
# Imports the data from data.py
from data import todos

# Create an instance of the flask Class
app = Flask(__name__)

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

# Runs the flask application, debug parameter auto-retarts the server after changes
if __name__ == "__main__":
    app.run(debug=True)