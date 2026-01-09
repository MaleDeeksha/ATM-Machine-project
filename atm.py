from flask import Flask, render_template, request,redirect,url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = "atm_secret_key"

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        card_no = request.form["card_no"]
        pin = request.form["pin"]
        balance = request.form["balance"]

        db = pymysql.connect(
            host="localhost",
            user="root",
            password="Deekshamale@123",
            database="atm_db",
            
        auth_plugin_map={"mysql_clear_password":None}
            
        )

        cursor = db.cursor()

        try:
            sql = "INSERT INTO users (name, card_no, pin, balance) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, card_no, pin, balance))
            db.commit()
            msg = "Registration Successful"
        except:
            msg = "Card number already exists"
        finally:
            db.close()

        return msg

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        card_no = request.form["card_no"]
        pin = request.form["pin"]

        db = pymysql.connect(
            host="localhost",
            user="root",
            password="Deekshamale@123",
            database="atm_db"
        )
        cursor = db.cursor()

        sql = "SELECT * FROM users WHERE card_no=%s AND pin=%s"
        cursor.execute(sql, (card_no, pin))
        user = cursor.fetchone()
        db.close()

        if user:
            session["card_no"] = card_no   # ⭐ VERY IMPORTANT
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Card Number or PIN"

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    # For now, simple dashboard page
    return render_template("dashboard.html")
@app.route("/check_balance")
def check_balance():
    if "card_no" not in session:
        return redirect(url_for("login"))

    card_no = session["card_no"]

    db = pymysql.connect(
        host="localhost",
        user="root",
        password="Deekshamale@123",
        database="atm_db"
    )
    cursor = db.cursor()

    sql = "SELECT balance FROM users WHERE card_no=%s"
    cursor.execute(sql, (card_no,))
    balance = cursor.fetchone()[0]
    db.close()

    return f"Your Current Balance is: ₹ {balance}"

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "card_no" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = int(request.form["amount"])
        card_no = session["card_no"]

        db = pymysql.connect(
            host="localhost",
            user="root",
            password="Deekshamale@123",
            database="atm_db"
        )
        cursor = db.cursor()

        # update balance
        cursor.execute(
            "UPDATE users SET balance = balance + %s WHERE card_no=%s",
            (amount, card_no)
        )

        # insert transaction history
        cursor.execute(
            "INSERT INTO transactions (card_no, type, amount) VALUES (%s, %s, %s)",
            (card_no, "Deposit", amount)
        )

        db.commit()
        db.close()

        return redirect(url_for("check_balance"))

    return render_template("deposit.html")

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "card_no" not in session:
        return redirect(url_for("login"))

    message = ""
    card_no = session["card_no"]

    if request.method == "POST":
        amount = int(request.form["amount"])

        db = pymysql.connect(
            host="localhost",
            user="root",
            password="Deekshamale@123",
            database="atm_db"
        )
        cursor = db.cursor()

        cursor.execute(
            "SELECT balance FROM users WHERE card_no=%s",
            (card_no,)
        )
        balance = cursor.fetchone()[0]

        if amount <= balance:
            cursor.execute(
                "UPDATE users SET balance = balance - %s WHERE card_no=%s",
                (amount, card_no)
            )

            # insert transaction history
            cursor.execute(
                "INSERT INTO transactions (card_no, type, amount) VALUES (%s, %s, %s)",
                (card_no, "Withdraw", amount)
            )

            db.commit()
            message = "Withdraw successful"
        else:
            message = "Insufficient balance"

        db.close()

    return render_template("withdraw.html", message=message)

@app.route("/transactions")
def transactions():
    if "card_no" not in session:
        return redirect(url_for("login"))

    card_no = session["card_no"]

    db = pymysql.connect(
        host="localhost",
        user="root",
        password="Deekshamale@123",
        database="atm_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()

    cursor.execute(
        "SELECT type, amount, date FROM transactions WHERE card_no=%s ORDER BY date DESC",
        (card_no,)
    )
    records = cursor.fetchall()
    db.close()

    return render_template("transactions.html", records=records)

@app.route("/change_pin", methods=["GET", "POST"])
def change_pin():
    if "card_no" not in session:
        return redirect(url_for("login"))

    message = ""
    card_no = session["card_no"]

    if request.method == "POST":
        old_pin = request.form["old_pin"]
        new_pin = request.form["new_pin"]
        confirm_pin = request.form["confirm_pin"]

        if new_pin != confirm_pin:
            message = "New PIN and Confirm PIN do not match"
        else:
            db = pymysql.connect(
                host="localhost",
                user="root",
                password="Deekshamale@123",
                database="atm_db"
            )
            cursor = db.cursor()

            cursor.execute(
                "SELECT pin FROM users WHERE card_no=%s",
                (card_no,)
            )
            current_pin = cursor.fetchone()[0]

            if old_pin == current_pin:
                cursor.execute(
                    "UPDATE users SET pin=%s WHERE card_no=%s",
                    (new_pin, card_no)
                )
                db.commit()
                message = "PIN changed successfully"
            else:
                message = "Old PIN is incorrect"

            db.close()

    return render_template("change_pin.html", message=message)

@app.route("/logout")
def logout():
    session.clear()   
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)