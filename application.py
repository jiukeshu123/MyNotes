import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///piggy.db")

@app.route("/")
@login_required
def index():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'magic.jpg')
    """ display the notes list on the left side, a piggy bag of total saving """
    row = db.execute("SELECT * FROM notes WHERE id = :id", id = session["user_id"])
    user = db.execute("SELECT username FROM users WHERE id = :id", id = session["user_id"])
    name = user[0]['username']
    if len(row) == 0:
        return render_template("intro.html", name = name, magic = full_filename)

    else:
        notelist = db.execute("SELECT Tag, Title, Category, Context FROM notes WHERE id = :id ORDER BY Category DESC", id = session["user_id"])
        return render_template("index.html", notelist = notelist)

@app.route("/filter", methods=["GET", "POST"])
@login_required
def filer():
    if request.method == "POST":
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'devil.jpg')
        notelist = db.execute("SELECT * FROM notes WHERE id = :id AND Title = :Title", id = session["user_id"], Title = request.form.get("filter"))
        if len(notelist) == 0:
            return render_template("Apology.html", error = "Not such title exist!", devil = full_filename)

        else:
            return render_template("filter.html", notelist = notelist)

    else:
        notelist = db.execute("SELECT Tag, Title, Category, Context FROM notes WHERE id = :id ORDER BY Category DESC", id = session["user_id"])
        return render_template("index.html", notelist = notelist)


@app.route("/addnotes", methods=["GET", "POST"])
@login_required
def addnotes():
    """ adding notes """
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'devil.jpg')
    if request.method == "POST":

        if not request.form.get("category"):
            return render_template("Apology.html", error = "Please select a category!", devil = full_filename)


        elif not request.form.get("context"):
            return render_template("Apology.html", error = "context can not be empty!", devil = full_filename)


        row = db.execute("SELECT * FROM notes WHERE id = :id", id = session["user_id"])

        if len(row) == 0:
            db.execute("INSERT INTO notes(id, Tag, Title, Category, Context) VALUES (:id, :Tag, :Title, :Category, :Context)",
                      id = session["user_id"], Tag = 1, Title = request.form.get("title"),  Category = request.form.get("category"), Context = request.form.get("context"))
        else:
            tag = len(row) + 1

            db.execute("INSERT INTO notes(id, Tag, Title, Category, Context) VALUES (:id, :Tag, :Title, :Category, :Context)",
                       id = session["user_id"], Tag = tag, Title = request.form.get("title"), Category = request.form.get("category"), Context = request.form.get("context"))
        flash("Added")
        return redirect("/")

    else:
        return render_template("addnotes.html")

@app.route("/delnotes", methods=["GET", "POST"])
@login_required
def delnotes():
    """ adding notes """
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'devil.jpg')
    if request.method == "POST":

        if not request.form.get("tag.1") and not request.form.get("tag.2") and not request.form.get("tag.3"):
            return render_template("Apology.html", error = "Enter at least one tag!", devil = full_filename)

        if request.form.get("tag.1"):
            db.execute("DELETE FROM notes WHERE id = :id AND Tag = :tag", id = session["user_id"], tag = request.form.get("tag.1"))

        if request.form.get("tag.2"):
            db.execute("DELETE FROM notes WHERE id = :id AND Tag = :tag", id = session["user_id"], tag = request.form.get("tag.2"))

        if request.form.get("tag.3"):
            db.execute("DELETE FROM notes WHERE id = :id and Tag = :tag", id = session["user_id"], tag = request.form.get("tag.3"))
        flash("Deleted")
        return redirect("/")

    else:
        return render_template("delnotes.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'devil.jpg')
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("Apology.html", error = "must provide username!", devil = full_filename)


        # Ensure password was submitted
        elif not request.form.get("password"):
             return render_template("Apology.html", error = "must provide password!", devil = full_filename)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("Apology.html", error = "invalid username and/or password!", devil = full_filename)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'devil.jpg')

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("Apology.html", error = "must provide username!", devil = full_filename)

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("Apology.html", error = "must provide password!", devil = full_filename)

        # Ensure second password was submitted
        elif not request.form.get("confirmation"):
            return render_template("Apology.html", error = "must reconfirm password!", devil = full_filename)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username is validate
        if len(rows) != 0:
            return render_template("Apology.html", error = "username already exist!", devil = full_filename)

        #ensure password is validate
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("Apology.html", error = "passwords are not match!", devil = full_filename)


        #hash password
        else:
            password_hash = generate_password_hash(request.form.get("password"))


        db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = request.form.get("username"), hash = password_hash)

        # Redirect user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)







