import os
import re
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, url_for,request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import boto3
from jose import jwt, JWTError
import requests
import urllib
from helpers import apology, login_required, lookup, usd
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.graph_objs as go

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

###################
# AWS Cognito configuration
AWS_REGION = 'us-east-1'
COGNITO_USER_POOL_ID = 'us-east-1_H8EWiqFe2'
COGNITO_CLIENT_ID = '3221bimcrvdpk7s2c3k39qfm3i'

# AWS Cognito client
cognito_client = boto3.client('cognito-idp', region_name=AWS_REGION)
##############################3

def decode_jwt(token, jwks_url):
    jwks = requests.get(jwks_url).json()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            }
    if rsa_key:
        try:
            decoded_token = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=COGNITO_CLIENT_ID,
                issuer=f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}',
            )
            return decoded_token
        except JWTError as e:
            print(e)
    return None

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

    # Assuming your API endpoint is hosted on AWS Lambda, you need to replace the URL with your actual API endpoint
    api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/portfolio/fetch/{username}"  

    # Retrieve username from the Flask session
    username = session.get('username')

    # Make a request to your API
    api_response = requests.get(api_url.format(username=username))

    if api_response.status_code == 200:
        # Parse the JSON response from the API
        api_data = api_response.json()
        return render_template("index.html",api_data=api_data)
    else:
        flash("User has no stocks")
        return render_template("index.html")
    

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/portfolio/fetch/{username}"  

    # Retrieve username from the Flask session
    username = session.get('username')
    if request.method == 'POST':
        sym = request.form.get("symbol").upper()
        stock_qty = int(request.form.get("shares"))
        stks = lookup(sym)
        # Ensure No of shares was submitted
        if not stock_qty:
            return apology("Must provide Total shares to be purchased")

        # Ensure No of shares is greater than 0
        if stock_qty <= 0:
            return apology("Must provide a positive number")

        # Call your buy API here
        user_info_api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/transactions/buy"

            # Call your AWS Lambda function   
        data = {
            'username': session['username'],
            'stockId': stks['symbol'],
            'quantity': str(stock_qty),
        }

        user_info_response = requests.post(user_info_api_url,json=data)

        if user_info_response.status_code == 200:
            # Fetch updated user information after buying stocks
            api_response = requests.get(api_url.format(username=session['username']))
            print(f"API Response: {api_response.text}")  # Add this line for debugging

            if api_response.status_code == 200:
                api_data = api_response.json()
                flash("Bought the stocks!")
                return render_template("index.html", api_data=api_data)
            else:
                flash("User has no stocks")
                return render_template("index.html")
        else:
            return apology(f"Failed to buy stocks: {user_info_response.text}")

    else:
        return render_template("buy.html", stock_symbols=["AAPL", "GOOGL", "MSFT", "AMZN", "F", "TSLA", "NVDA", "NFLX", "INTC", "AMD"])



@app.route("/history")
@login_required
def history():

    api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/transactions/history/{username}"

    # Retrieve username from the Flask session
    username = session.get('username')

    # Make a request to your API for transaction history
    api_response = requests.get(api_url.format(username=username))
    transaction_history = api_response.json()
    return render_template("history.html", transaction_history=transaction_history)
   

@app.route("/news")
@login_required
def news():
    newsum = db.execute("SELECT * FROM 'newsinfo' WHERE user_id = :user",
                          user=session["user_id"])

    newsinfo = []
    for row in newsum:
        #stocks = lookup(row['stock'])

        # create a list with all the info about the transaction and append it to a list of every stock transaction
        newsinfo.append(list(['index'],['summary'], ['link']))

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

        # # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                   username=request.form.get("username"))

        # # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': request.form.get('username'),
                    'PASSWORD': request.form.get('password'),
                }
            )

            # Extract and return the access token, secret key, and session token
            session['AccessToken'] = response['AuthenticationResult']['AccessToken']

            ###########################################
                        # Decode the AccessToken to extract user information
            jwks_url = f'https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json'
            decoded_token = decode_jwt(session['AccessToken'], jwks_url)

            if decoded_token:
                # You can now access user information from the decoded_token
                user_id = decoded_token.get('sub')
                email = decoded_token.get('email')
                username = decoded_token.get('username')

                # Store user information in the session
                session['user_id'] = user_id
                session['email'] = email
                session['username'] = username
            ###############################################
            # Redirect user to home page
            flash("Logged in successfully!")
            return redirect("/")

        except Exception as e:
            print(e)

    # User reached route via GET (as by clicking a link or via redirect)
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


def get_stock_symbols():
    stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "F", "TSLA", "NVDA", "NFLX", "INTC", "AMD"]
    stock_symbols_with_names = []

    for symbol in stock_symbols:
        stock_info = lookup_yahoo_finance_api(symbol)
        if stock_info:
            stock_symbols_with_names.append({"symbol": stock_info["symbol"], "shortName": stock_info["shortName"]})

    return stock_symbols_with_names

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    stock_symbols = get_stock_symbols()

    if request.method == 'POST':
        selected_stock_symbol = request.form.get('stock_symbol')
        stock = next((s for s in stock_symbols if s['symbol'] == selected_stock_symbol), None)

        if stock:
            stock_info = lookup_yahoo_finance_api(selected_stock_symbol)

            if stock_info:
                stock_data = yf.download(selected_stock_symbol, start='2022-01-01', end='2023-01-01', progress=False)

                if not stock_data.empty:
                    candlestick_chart = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                                                        open=stock_data['Open'],
                                                                        high=stock_data['High'],
                                                                        low=stock_data['Low'],
                                                                        close=stock_data['Close'])])
                    candlestick_chart.update_layout(title=f'Candlestick Chart for {stock["shortName"]}',
                                                   xaxis_title='Date', yaxis_title='Stock Price')

                    return render_template("quote.html", stock_symbols=stock_symbols, selected_stock=stock, stock_info=stock_info, candlestick_chart=candlestick_chart.to_html(full_html=False))
                else:
                    return render_template("quote.html", stock_symbols=stock_symbols, error_message="Failed to fetch stock data.")

    return render_template("quote.html", stock_symbols=stock_symbols)



def lookup_yahoo_finance_api(symbol):
        api_url = f"https://query1.finance.yahoo.com/v1/finance/lookup?query={symbol}&type=equity"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)
            data = response.json()

            # Extract relevant information from the API response
            documents = data.get("finance", {}).get("result", [{}])[0].get("documents", [])
            if documents:
                result = documents[0]
                short_name = result.get("shortName") or result.get("longName") or "N/A"
                stock_info = {
                    "shortName": short_name,
                    "symbol": result.get("symbol", "N/A"),
                    "price": result.get("regularMarketPrice", {}).get("raw", "N/A"),
                }
            return stock_info
        except requests.exceptions.RequestException as e:
            # Handle exceptions (e.g., network errors)
            print(f"Error fetching data for {symbol}: {e}")
            return None


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
        print(uname, type(uname))
        if(len(uname) != 0):
            status=False
            msg="Username already taken"
        # Ensure username exists and password is correct
        # Remember which user has logged in
        if status:
            try: 
                response = cognito_client.sign_up(
                    ClientId=COGNITO_CLIENT_ID,
                    Username=request.form.get('username'),
                    Password=request.form.get('password'),
                    UserAttributes=[
                        {
                            'Name': 'phone_number',           
                            'Value': '+1'+request.form.get('mobile')
                        },
                        {
                            'Name': 'email',           
                            'Value': request.form.get('emailid')
                        }
                    ]      
                )
                flash("Registration is successful!! Please check your email for confirmation.")
                return redirect(url_for('confirm'))

            except Exception as e:
                print(e)
        else:
            # Redirect user to home page
            return apology(msg)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        username = request.form['username']
        confirmation_code = request.form['confirmation_code']
        try:
            cognito_client.confirm_sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                ConfirmationCode=confirmation_code
            )
            flash("Confirmation successful! You can now log in.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Confirmation failed: {str(e)}")

    return render_template("confirm.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/portfolio/fetch/{username}"  

    # Retrieve username from the Flask session
    username = session.get('username')
    if request.method == 'POST':
        sym=request.form.get("symbol").upper()
        stockqty=int(request.form.get("shares"))
        stks=lookup(sym)
        status=True

        # Ensure No of shares was submitted
        if not stockqty:
            status=False
            return apology("Must provide Total shares to be purchased")

        # Ensure No of shares is greater than 0
        if stockqty<=0:
            status=False
            return apology("Must provide a positive number")

        # Call your buy API here
        user_info_api_url = "https://pry9rtwz28.execute-api.us-east-1.amazonaws.com/prod/transactions/sell"

            # Call your AWS Lambda function   
        data = {
            'username': session['username'],
            'stockId': stks['symbol'],
            'quantity': str(stockqty),
        }

        user_info_response = requests.post(user_info_api_url,json=data)

        if user_info_response.status_code == 200:
            # Fetch updated user information after buying stocks
            api_response = requests.get(api_url.format(username=session['username']))
            print(f"API Response: {api_response.text}")  # Add this line for debugging

            if api_response.status_code == 200:
                api_data = api_response.json()
                flash("Sold the stocks!")
                return render_template("index.html", api_data=api_data)
            else:
                flash("User has no stocks")
                return render_template("index.html")
        else:
            return apology(f"Failed to sell stocks: {user_info_response.text}")

    else:
        return render_template("sell.html", stock_symbols=["AAPL", "GOOGL", "MSFT", "AMZN", "F", "TSLA", "NVDA", "NFLX", "INTC", "AMD"])


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))