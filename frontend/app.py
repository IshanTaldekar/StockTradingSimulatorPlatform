import os
import re
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd
#app.jinja_env.globals.update(usd=usd, lookup=lookup, int=int)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#   raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    rows = db.execute("SELECT * FROM stock_info WHERE user_id = :user",
                          user=session["user_id"])

    cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=session["user_id"])[0]['cash']

    total = cash
    stock_info = []
    for index, row in enumerate(rows):
        stocks = lookup(row['stock_symbol'])

        # create a list with all the info about the stock and append it to a list of every stock owned by the user
        stock_info.append(list((stocks['symbol'], stocks['name'], row['stock_qty'], stocks['price'], round(stocks['price'] * row['stock_qty'], 2))))
        total += stock_info[index][4]

    return render_template("index.html", stock_info=stock_info, cash=round(cash, 2), total=round(total, 2))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == 'POST':
        sym=request.form.get("symbol").upper()
        stockqty=int(request.form.get("shares"))
        stks=lookup(sym)
        status=True
        # Ensure Symbol was submitted
        if not sym:
            status=False
            return apology("Must provide Symbol")

        # Ensure No of shares was submitted
        if not stockqty:
            status=False
            return apology("Must provide Total shares to be purchased")

        # Ensure No of shares is greater than 0
        if stockqty<=0:
            status=False
            return apology("Must provide a positive number")

        # check if valid stock symbol is provided
        if not stks:
            return apology("Stock symbol is not valid")

        totalcost = float(stockqty) * stks['price']
        money = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"]);
        if(totalcost > float(money[0]["cash"])):
            return apology("You do not have enough Cash")

        # Check if user already has one or more stocks from the same company
        stock = db.execute("SELECT stock_qty FROM stock_info WHERE user_id = :user AND stock_symbol = :symbol",
                          user=session["user_id"], symbol=stks["symbol"])

        # Insert new row into the stock table
        if not stock:
            db.execute("INSERT INTO stock_info(user_id, stock_symbol, stock_qty) VALUES (:user, :symbol, :stock_qty)",
                user=session["user_id"], symbol=stks["symbol"] , stock_qty=stockqty)

        # update row into the stock table
        else:
            stockqty += stock[0]["stock_qty"]

            db.execute("UPDATE stock_info SET stock_qty = :stock_qty WHERE user_id = :user AND stock_symbol = :stock_symbol",
                user=session["user_id"], stock_symbol=stks["symbol"], stock_qty=stockqty)

        # update user's cash
        db.execute("UPDATE users SET cash=cash-:cost WHERE id=:id", cost=totalcost, id=session["user_id"])

        # Update transaction table
        db.execute("INSERT INTO 'transaction'(user_id, stock, quantity, price, total, date) VALUES (:user_id, :stock, :stock_qty, :price, :total, :date)",
                user_id=session["user_id"], stock=stks["symbol"],stock_qty=stockqty, price=stks["price"],total=round(stockqty*float(stks["price"])),date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Redirect user to index page with a success message
        flash("Bought the stocks!")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():

    trans = db.execute("SELECT * FROM 'transaction' WHERE user_id = :user",
                          user=session["user_id"])

    transaction = []
    for row in trans:
        stocks = lookup(row['stock'])

        # create a list with all the info about the transaction and append it to a list of every stock transaction
        transaction.append(list((stocks['symbol'], stocks['name'], row['quantity'], row['total'], row['date'])))

    # redirect user to index page
    return render_template("history.html", transaction=transaction)

@app.route("/news")
@login_required
def news():
    newsum = db.execute("SELECT * FROM 'newsinfo' WHERE user_id = :user",
                          user=session["user_id"])

    transaction = []
    for row in trans:
        #stocks = lookup(row['stock'])

        # create a list with all the info about the transaction and append it to a list of every stock transaction
        transaction.append(list(['index'],['summary'], ['link']))

    # redirect user to index page
    return render_template("news.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logged in successfully!")
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

@app.route("/changepaswd" ,methods=["GET", "POST"])
@login_required
def changepaswd():
    """Change Password"""

    if request.method == 'POST':
        newpaswd=request.form.get("newpaswd")
        confirmpaswd=request.form.get("confirmpaswd")
        status=True
        # Ensure password was submitted
        if not request.form.get("newpaswd") or not request.form.get("confirmpaswd"):
            status=False
            flash("Please enter Password")
            return redirect("/changepaswd")

        #Ensure password matches confirm password
        elif  request.form.get("newpaswd")!=request.form.get("confirmpaswd"):
            status=False
            flash("Password confirmation did not match")
            return redirect("/changepaswd")

        if status:
            rows = db.execute("UPDATE users SET hash = :hash WHERE id = :uid",uid=session["user_id"], hash=generate_password_hash(newpaswd))
            #session["user_id"] = rows
            flash("Password changed successfully")
            return redirect("/")
        # Redirect user to home page

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepaswd.html")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        r = lookup(request.form.get("symbol"))

        if not r:
            return apology("Could not find the stock")

        return render_template("quote.html", stock=r)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'POST':
        name=request.form.get("username")
        email = request.form.get("emailid")
        mobile = request.form.get("mobile")
        hash=generate_password_hash(request.form.get("password"))
        status=True
        # Ensure username was submitted
        if not request.form.get("username"):
            status=False
            msg="Must provide Username"

        elif not email:
            status = False
            msg = "Must provide Email"

        elif not mobile:
            status = False
            msg = "Must provide Mobile no"

        # Email validation
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            status = False
            msg = "Invalid Email"

        # Mobile number validation
        elif not re.match(r"^[0-9]{10}$", mobile):
            status = False
            msg = "Invalid Mobile No"

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("password_confirm"):
            status=False
            msg="Must provide Password"

        elif  request.form.get("password")!=request.form.get("password_confirm"):
            status=False
            msg="Password confirmation did not match"


        # insert into database
        uname=db.execute("SELECT username from users where username=:username",username=name)
        if(uname):
            status=False
            msg="Username already taken"
        # Ensure username exists and password is correct
        # Remember which user has logged in
        if status:
            #rows = db.execute("INSERT INTO users (username,hash) VALUES (:username,:hash)",username=name, hash=hash)
            rows=db.execute("INSERT INTO users (username, email, mobile, hash) VALUES (:username, :email, :mobile, :hash)",
                       username=name, email=email, mobile=mobile, hash=hash)
            #db.commit()
            flash("Registration is successful")
            session["user_id"] = rows
            return redirect("/")
        # Redirect user to home page
        return apology(msg)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == 'POST':
        sym=request.form.get("symbol").upper()
        stockqty=int(request.form.get("shares"))
        stks=lookup(sym)
        status=True
        # Ensure Symbol was submitted
        if not sym:
            status=False
            return apology("Must provide Symbol")

        # Ensure No of shares was submitted
        if not stockqty:
            status=False
            return apology("Must provide Total shares to be purchased")

        # Ensure No of shares is greater than 0
        if stockqty<=0:
            status=False
            return apology("Must provide a positive number")

        # check if valid stock symbol is provided
        if not stks:
            return apology("Stock symbol is not valid")

        # Update stocks table
        stock_qty_bef = db.execute("SELECT stock_qty FROM stock_info WHERE user_id = :user AND stock_symbol = :symbol",
                          symbol=sym, user=session["user_id"])[0]['stock_qty']
        stock_qty_after = stock_qty_bef - stockqty

        # delete stock from table if we sold every unit
        if stock_qty_after == 0:
            db.execute("DELETE FROM stock_info WHERE user_id = :user AND stock_symbol = :symbol",
                          symbol=sym, user=session["user_id"])

        # stop the transaction if the user does not have enough stocks
        elif stock_qty_after < 0:
            return apology("That's more than the stocks you own")

        # otherwise update with new value
        else:
            db.execute("UPDATE stock_info SET stock_qty = :quantity WHERE user_id = :user AND stock_symbol = :symbol",
                          symbol=sym, user=session["user_id"], quantity=stock_qty_after)

        # calculate and update user's cash
        cash = db.execute("SELECT cash FROM users WHERE id = :user",
                          user=session["user_id"])[0]['cash']
        cash_after = cash + stks["price"] * float(stockqty)

        db.execute("UPDATE users SET cash = :cash WHERE id = :user",
                          cash=cash_after, user=session["user_id"])

        # Update transaction table
        db.execute("INSERT INTO 'transaction'(user_id, stock,quantity,price,total,date) VALUES (:user, :stock, :stockqty, :price,:total,:date)",
                user=session["user_id"], stock=stks["symbol"],stockqty=-stockqty, price=stks["price"],total=round(stockqty*float(stks["price"])),date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Redirect user to home page with success message
        flash("Sold!")
        return redirect("/")
    else:
        return render_template("sell.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
