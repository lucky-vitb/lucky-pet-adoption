from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "luckypetsecret"

DATABASE = "lucky_new.db"


# ---------------- DATABASE CONNECTION ---------------- #

def get_connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con


# ---------------- DATABASE SETUP ---------------- #

def setup_database():

    con = get_connection()
    cursor = con.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        password TEXT
    )
    """)

    # PETS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pets (
        Pet_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Pet_Name TEXT,
        Breed TEXT,
        Age INTEGER,
        Gender TEXT,
        Status TEXT DEFAULT 'Available'
    )
    """)

    # ADOPTERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Adopters (
        Adopter_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Adopter_Name TEXT,
        Phone TEXT,
        City TEXT
    )
    """)

    # ADOPTION TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Adoption (
        Adoption_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Pet_ID INTEGER,
        Adopter_ID INTEGER,
        Adoption_Date TEXT
    )
    """)

    con.commit()
    con.close()


setup_database()


# ---------------- HOME PAGE ---------------- #

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")


# ---------------- SIGNUP ---------------- #

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()

        try:
            con.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
            """, (username, email, password))

            con.commit()

        except:
            return "Username already exists!"

        finally:
            con.close()

        return redirect("/login")

    return render_template("signup.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        con = get_connection()

        user = con.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
        """, (username, password)).fetchone()

        con.close()

        if user:
            session["user"] = username
            return redirect("/")

        else:
            return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- ADD PET ---------------- #

@app.route("/add_pet", methods=["GET", "POST"])
def add_pet():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        breed = request.form["breed"]
        age = request.form["age"]
        gender = request.form["gender"]

        con = get_connection()

        con.execute("""
        INSERT INTO Pets (Pet_Name, Breed, Age, Gender)
        VALUES (?, ?, ?, ?)
        """, (name, breed, age, gender))

        con.commit()
        con.close()

        return redirect("/pets")

    return render_template("add_pet.html")


# ---------------- VIEW PETS ---------------- #

@app.route("/pets")
def pets():

    if "user" not in session:
        return redirect("/login")

    con = get_connection()

    pets = con.execute("SELECT * FROM Pets").fetchall()

    con.close()

    return render_template("pets.html", pets=pets)


# ---------------- ADD ADOPTER ---------------- #

@app.route("/add_adopter", methods=["GET", "POST"])
def add_adopter():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        city = request.form["city"]
        district = request.form["district"]

        con = get_connection()

        con.execute("""
       INSERT INTO Adopters (Adopter_Name, Phone, City, District)
       VALUES (?, ?, ?, ?)
        """, (name, phone, district))

        con.commit()
        con.close()

        return redirect("/adopters")

    return render_template("add_adopter.html")


# ---------------- VIEW ADOPTERS ---------------- #

@app.route("/adopters")
def adopters():

    if "user" not in session:
        return redirect("/login")

    con = get_connection()

    adopters = con.execute("SELECT * FROM Adopters").fetchall()

    con.close()

    return render_template("adopters.html", adopters=adopters)


# ---------------- ADOPT PET ---------------- #

@app.route("/adopt_pet", methods=["GET", "POST"])
def adopt_pet():

    if "user" not in session:
        return redirect("/login")

    con = get_connection()

    pets = con.execute("""
    SELECT * FROM Pets
    WHERE Status='Available'
    """).fetchall()

    adopters = con.execute("""
    SELECT * FROM Adopters
    """).fetchall()

    if request.method == "POST":

        pet_id = request.form["pet_id"]
        adopter_id = request.form["adopter_id"]

        con.execute("""
        INSERT INTO Adoption (Pet_ID, Adopter_ID, Adoption_Date)
        VALUES (?, ?, DATE('now'))
        """, (pet_id, adopter_id))

        con.execute("""
        UPDATE Pets
        SET Status='Adopted'
        WHERE Pet_ID=?
        """, (pet_id,))

        con.commit()

        return redirect("/report")

    con.close()

    return render_template(
        "adopt_pet.html",
        pets=pets,
        adopters=adopters
    )


# ---------------- REPORT ---------------- #

@app.route("/report")
def report():

    if "user" not in session:
        return redirect("/login")

    con = get_connection()

    data = con.execute("""
    SELECT
        Pets.Pet_Name,
        Pets.Breed,
        Adopters.Adopter_Name,
        Adopters.City,
        Adoption.Adoption_Date
    FROM Adoption
    JOIN Pets ON Pets.Pet_ID = Adoption.Pet_ID
    JOIN Adopters ON Adopters.Adopter_ID = Adoption.Adopter_ID
    """).fetchall()

    con.close()

    return render_template("report.html", data=data)


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)