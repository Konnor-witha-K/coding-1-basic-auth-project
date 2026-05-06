from flask import Flask, request, redirect, url_for, render_template, session
from database import get_db, init_db
import bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

init_db()

# ---------- PASSWORD VALIDATION ----------
def is_valid_password(password):
    return (
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[^A-Za-z0-9]", password)
    )

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Incorrect username or password"

    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            error = "Fields cannot be empty"
        elif not is_valid_password(password):
            error = "Password must include uppercase, lowercase, number, and special character"
        else:
            conn = get_db()
            try:
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_pw)
                )
                conn.commit()

                return redirect(url_for("login"))
            except:
                conn.rollback()
                error = "Username already exists or error occurred"
            finally:
                conn.close()

    return render_template("register.html", error=error)

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    entries = conn.execute(
        """
        SELECT MIN(id) AS id, title, content, user
        FROM entries
        WHERE user=? OR user='default'
        GROUP BY title, content, user
        """,
        (session["user"],)
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        entries=entries,
        username=session["user"]
    )


@app.route("/create", methods=["GET", "POST"])
def create():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO entries (title, content, user) VALUES (?, ?, ?)",
                (title, content, session["user"])
            )
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("create.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    entry = conn.execute(
        "SELECT * FROM entries WHERE id=? AND user=?",
        (id, session["user"])
    ).fetchone()
    # This prevents editing other users' data

    if not entry: 
        conn.close()
        return "Not allowed"

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
    
        conn.execute(
            "UPDATE entries SET title=?, content=? WHERE id=? AND user=?",
            (title, content, id, session["user"]) 
        )
        
        conn.commit()
        conn.close

        return redirect(url_for("dashboard"))
    
    conn.close()
    return render_template("edit.html", entry=entry)
    


@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # TODO: Connect to database
        conn = get_db()

        # TODO: Delete entry WHERE id AND user
        try:
            conn.execute(
                "DELETE FROM entries WHERE id=? AND user=?", 
                (id, session["user"])
            )
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("delete.html", id=id)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)