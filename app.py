from flask import Flask, render_template, session, redirect, url_for, request, g
from flask_session import Session
from database import get_db, close_db
from forms import registerForm, loginForm, transactionForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import calendar
import time

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.before_request
def logged_in_user():
    g.user = session.get("user_id", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = registerForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        db = get_db()
        clashing_user = db.execute("""  SELECT * FROM users WHERE user_id = ? ; """, (user_id,)).fetchone()
        if clashing_user is not None:
            form.user_id.errors.append("The user id you typed is already in use. Please type another one!")
        else:
            db.execute("""  INSERT INTO users (user_id, password) VALUES(?,?); """, (user_id, generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        clashing_user = db.execute(""" SELECT * FROM users WHERE user_id = ?; """, (user_id,)).fetchone()
        if clashing_user is None:
            form.user_id.errors.append("This user does not exist")
        elif not check_password_hash(clashing_user["password"], password):
            form.password.errors.append("Password incorrect!")
        else:
            session.clear()
            session["user_id"] = user_id
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(url_for("index"))
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/add", methods = ["GET", "POST"])
@login_required 
def add():
    this_month = datetime.now().strftime('%B')
    form = transactionForm()
    if form.validate_on_submit():
        category = form.category.data
        date = form.date.data
        amount = form.amount.data
        input_year = datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d").year
        input_month = datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d").month
        db = get_db()
        if date > datetime.now().date():
            form.date.errors.append("The date you selected is in the future. Please only insert past transactions!")
            return render_template("add.html", form=form)
        elif input_year < datetime.now().date().year:
            form.date.errors.append("The date you selected is from last year. Please only input transactions from the current year!")
            return render_template("add.html", form=form)
        elif input_month < datetime.now().date().month:
            form.date.errors.append("You can only add transactions from this month, to keep track of your monthly expenses.")
            return render_template("add.html", form=form)
        elif amount <= 0:
            form.amount.errors.append("Please type a valid amount.")
            return render_template("add.html", form=form)
        else:
            if category == "Groceries":
                db.execute("""  INSERT INTO groceries_expenses (user_id, date, amount) VALUES (?, ?, ?); """, (g.user, date, amount))
                db.commit()
            elif category == "Healthcare":
                db.execute("""  INSERT INTO healthcare_expenses (user_id, date, amount) VALUES (?, ?, ?); """, (g.user, date, amount))
                db.commit()
            elif category == "Restaurants":
                db.execute("""  INSERT INTO restaurants_expenses (user_id, date, amount) VALUES (?, ?, ?); """, (g.user, date, amount))
                db.commit()
            elif category == "Beauty":
                db.execute("""  INSERT INTO beauty_expenses (user_id, date, amount) VALUES (?, ?, ?); """, (g.user, date, amount))
                db.commit()
            elif category == "Transport":
                db.execute(""" INSERT INTO transport_expenses(user_id, date, amount) VALUES (?,?,?) """, (g.user, date, amount))
                db.commit()
            else:
                db.execute("""  INSERT INTO other_expenses (user_id, date, amount) VALUES (?, ?, ?); """, (g.user, date, amount))
                db.commit()
            return redirect(url_for("profile"))
    return render_template("add.html", form=form, this_month=this_month)

@app.route("/profile")
@login_required
def profile():
    current_month = datetime.now().strftime('%B')
    db = get_db()
    #Initializing this month total expenses in each category:
    total_groceries_expenses = 0
    total_healthcare_expenses = 0
    total_restaurants_expenses = 0
    total_beauty_expenses = 0
    total_transport_expenses = 0
    total_other_expenses = 0
    #Initializing last month total expenses in each category:
    total_g_expenses_last_month = 0
    total_h_expenses_last_month = 0
    total_r_expenses_last_month = 0
    total_b_expenses_last_month = 0
    total_t_expenses_last_month = 0
    total_o_expenses_last_month = 0
    #This month expenses:
    #Display groceries expenses:
    g_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM groceries_expenses  
                            WHERE user_id = ?; """, (g.user,)).fetchall()
    #Calculate total groceries expenses:
    for expense in g_expense:
        total_g_expenses = db.execute(""" SELECT amount FROM groceries_expenses; """).fetchall()
        total_groceries_expenses = round(total_groceries_expenses + expense["amount"], 2)
    #Display healthcare expenses:
    h_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM healthcare_expenses 
                            WHERE user_id = ?; """, (g.user,)).fetchall()
    #Total healthcare expenses:
    for expense in h_expense:
        total_h_expenses = db.execute(""" SELECT amount FROM healthcare_expenses; """).fetchall()
        total_healthcare_expenses = round(total_healthcare_expenses + expense["amount"], 2)
    #Display restaurants expenses:
    r_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM restaurants_expenses  
                            WHERE user_id = ?; """, (g.user,)).fetchall()
    #Total restaurants expenses:
    for expense in r_expense:
        total_r_expenses = db.execute(""" SELECT amount FROM restaurants_expenses; """).fetchall()
        total_restaurants_expenses = round(total_restaurants_expenses + expense["amount"], 2)
    #Display beauty expenses:
    b_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM beauty_expenses
                            WHERE user_id = ?;  """, (g.user,)).fetchall()
    #Total beauty expenses:
    for expense in b_expense:
        total_b_expenses = db.execute(""" SELECT amount FROM beauty_expenses; """).fetchall()
        total_beauty_expenses = round(total_beauty_expenses + expense["amount"], 2)
    #Display transport expenses:
    t_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM transport_expenses 
                            WHERE user_id = ?;  """, (g.user,)).fetchall()
    #Calculate total transport expenses:
    for expense in t_expense:
        total_t_expenses = db.execute(""" SELECT amount FROM beauty_expenses; """).fetchall()
        total_transport_expenses = round(total_transport_expenses + expense["amount"], 2)
    #Display other expenses:
    o_expense = db.execute(""" SELECT transaction_id, date, amount 
                            FROM other_expenses 
                            WHERE user_id = ?; """, (g.user,)).fetchall()
    #Total other expenses:
    for expense in o_expense:
        total_o_expenses = db.execute(""" SELECT amount FROM other_expenses; """).fetchall()
        total_other_expenses = round(total_other_expenses + expense["amount"], 2)
    #Last month expenses:
    #Last month groceries expenses + total:
    last_month_g_expense = db.execute(""" SELECT date,amount FROM last_month_groceries WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_g_expense:
        g_last_month_total = db.execute(""" SELECT amount FROM last_month_groceries; """).fetchall()
        total_g_expenses_last_month = round(total_g_expenses_last_month + expense["amount"], 2)
    #Last month healthcare expenses + total:
    last_month_h_expense = db.execute(""" SELECT date,amount FROM last_month_healthcare WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_h_expense:
        h_last_month_total = db.execute(""" SELECT amount FROM last_month_healthcare; """).fetchall()
        total_h_expenses_last_month = round(total_h_expenses_last_month + expense["amount"], 2)
    #Last month restaurants expenses + total:
    last_month_r_expense = db.execute(""" SELECT date,amount FROM last_month_restaurants WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_r_expense:
        r_last_month_total = db.execute(""" SELECT amount FROM last_month_restaurants; """).fetchall()
        total_r_expenses_last_month = round(total_r_expenses_last_month + expense["amount"], 2)
    #Last month beauty expenses + total:
    last_month_b_expense = db.execute(""" SELECT date,amount FROM last_month_beauty WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_b_expense:
        b_last_month_total = db.execute(""" SELECT amount FROM last_month_beauty; """).fetchall()
        total_b_expenses_last_month = round(total_b_expenses_last_month + expense["amount"], 2)
    #Last month transport expenses + total:
    last_month_t_expense = db.execute(""" SELECT date,amount FROM last_month_transport WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_t_expense:
        t_last_month_total = db.execute(""" SELECT amount FROM last_month_transport; """).fetchall()
        total_t_expenses_last_month = round(total_t_expenses_last_month + expense["amount"], 2)
    #Last month other expenses + total:
    last_month_o_expense = db.execute(""" SELECT date,amount FROM last_month_other WHERE user_id = ?; """, (g.user,)).fetchall()
    for expense in last_month_o_expense:
        o_last_month_total = db.execute(""" SELECT amount FROM last_month_other; """).fetchall()
        total_o_expenses_last_month = round(total_o_expenses_last_month + expense["amount"], 2)

    return render_template("profile.html", g_expense=g_expense, h_expense=h_expense, r_expense=r_expense, b_expense=b_expense, t_expense=t_expense, o_expense=o_expense, 
                           total_groceries_expenses=total_groceries_expenses, total_healthcare_expenses=total_healthcare_expenses, 
                           total_restaurants_expenses=total_restaurants_expenses, total_beauty_expenses=total_beauty_expenses, 
                           total_other_expenses=total_other_expenses, total_transport_expenses=total_transport_expenses,
                           current_month=current_month,
                           last_month_g_expense=last_month_g_expense, last_month_h_expense=last_month_h_expense, last_month_r_expense=last_month_r_expense, 
                           last_month_b_expense=last_month_b_expense, last_month_t_expense=last_month_t_expense, last_month_o_expense=last_month_o_expense,
                           total_g_expenses_last_month=total_g_expenses_last_month, total_h_expenses_last_month=total_h_expenses_last_month, 
                           total_r_expenses_last_month=total_r_expenses_last_month, total_b_expenses_last_month=total_b_expenses_last_month, 
                           total_t_expenses_last_month=total_t_expenses_last_month, total_o_expenses_last_month=total_o_expenses_last_month)


#Routes to reset the databases
@app.route("/g_reset")
def g_reset():
    db = get_db()
    db.execute(""" DELETE FROM groceries_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/h_reset")
def h_reset():
    db = get_db()
    db.execute(""" DELETE FROM healthcare_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/r_reset")
def r_reset():
    db = get_db()
    db.execute(""" DELETE FROM restaurants_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/b_reset")
def b_reset():
    db = get_db()
    db.execute(""" DELETE FROM beauty_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/t_reset")
def t_reset():
    db = get_db()
    db.execute(""" DELETE FROM transport_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/o_reset")
def o_reset():
    db = get_db()
    db.execute(""" DELETE FROM other_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

@app.route("/reset_all")
def reset_all():
    db = get_db()
    db.execute(""" DELETE FROM groceries_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    db.execute(""" DELETE FROM healthcare_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    db.execute(""" DELETE FROM restaurants_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    db.execute(""" DELETE FROM beauty_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    db.execute(""" DELETE FROM transport_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    db.execute(""" DELETE FROM other_expenses WHERE user_id = ?; """, (g.user,))
    db.commit()
    return render_template("profile.html")

#Routes to remove single lines from databases
@app.route("/remove_g/<transaction_id>")
def remove_g(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM groceries_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/remove_h/<transaction_id>")
def remove_h(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM healthcare_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/remove_r/<transaction_id>")
def remove_r(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM restaurants_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/remove_b/<transaction_id>")
def remove_b(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM beauty_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/remove_t/<transaction_id>")
def remove_t(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM transport_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/remove_o/<transaction_id>")
def remove_o(transaction_id):
    db = get_db()
    db.execute(""" DELETE FROM other_expenses WHERE transaction_id = ? AND user_id = ?; """, (transaction_id, g.user))
    db.commit()
    return redirect(url_for("profile"))

#Routes to end the month: 
@app.route("/change_of_month_g")
def change_of_month_g():
    db = get_db()
    db.execute(""" DELETE FROM last_month_groceries; """)
    this_month_g_data = db.execute(""" SELECT date, amount, user_id FROM groceries_expenses WHERE user_id=?; """, (g.user,)).fetchall()
    for row in this_month_g_data:
        row = dict(row)
        db.execute(""" INSERT INTO last_month_groceries(date, amount, user_id) VALUES(?,?,?); """,(row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM groceries_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/change_of_month_h")
def change_of_month_h():
    db = get_db()
    db.execute(""" DELETE FROM last_month_healthcare; """)
    this_month_h_data = db.execute(""" SELECT date, amount, user_id FROM healthcare_expenses WHERE user_id = ?; """, (g.user,)).fetchall()
    for row in this_month_h_data:
        row = dict(row)
        db.execute(""" INSERT INTO last_month_healthcare(date,amount,user_id) VALUES(?,?,?); """, (row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM healthcare_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/change_of_month_r")
def change_of_month_r():
    db = get_db()
    db.execute(""" DELETE FROM last_month_restaurants; """)
    this_month_r_data = db.execute(""" SELECT date, amount, user_id FROM restaurants_expenses WHERE user_id = ?; """, (g.user,)).fetchall()
    for row in this_month_r_data:
        row = dict(row)
        db.execute(""" INSERT INTO last_month_restaurants(date,amount,user_id) VALUES(?,?,?); """, (row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM restaurants_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/change_of_month_b")
def change_of_month_b():
    db = get_db()
    db.execute(""" DELETE FROM last_month_beauty; """)
    this_month_b_data = db.execute(""" SELECT date, amount, user_id FROM beauty_expenses WHERE user_id = ?; """, (g.user,)).fetchall()
    for row in this_month_b_data:
        row = dict(row)
        db.execute(""" INSERT INTO last_month_beauty(date,amount,user_id) VALUES(?,?,?); """, (row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM beauty_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/change_of_month_t")
def change_of_month_t():
    db = get_db()
    db.execute(""" DELETE FROM last_month_transport; """)
    this_month_t_data = db.execute(""" SELECT date, amount, user_id FROM transport_expenses WHERE user_id = ?; """, (g.user,)).fetchall()
    for row in this_month_t_data:
        row = dict(row)
        db.execute(""" INSERT INTO last_month_transport(date,amount,user_id) VALUES(?,?,?); """, (row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM transport_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))

@app.route("/change_of_month_o")
def change_of_month_o():
    db = get_db()
    db.execute(""" DELETE FROM last_month_other; """)
    this_month_o_data = db.execute(""" SELECT date, amount, user_id FROM other_expenses WHERE user_id = ?; """, (g.user,)).fetchall()
    for row in this_month_o_data:
        db.execute(""" INSERT INTO last_month_other(date,amount,user_id) VALUES(?,?,?); """, (row["date"], row["amount"], row["user_id"]))
    db.execute(""" DELETE FROM other_expenses WHERE user_id =?; """, (g.user,))
    db.commit()
    return redirect(url_for("profile"))
    