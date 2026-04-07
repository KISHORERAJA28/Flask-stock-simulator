

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        if not quote:
            return apology("Invalid symbol", 400)
        else:
            return render_template("quote.html", quote = quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # clear previous session
    session.clear()

    if request.method == "POST":
        # credentials
        if not request.form.get("username"):
            return apology("Username is required", 400)
        elif not request.form.get("password"):
            return apology("Password is required", 400)
        elif not request.form.get("confirmation"):
            return apology("You must confirm your password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match", 400)

        # search database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # checking for duplicates
        if len(rows) != 0:
            return apology("Username already exists", 400)

        # register new valid user
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # search for the newly registered user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # create a new session for the user
        session["user_id"] = rows[0]["id"]

        # back to home
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # get user's stocks
    stocks = db.execute(
        "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0",
        user_id = session["user_id"]
    )

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        if not symbol:
            return apology("Symbol is required")
        elif not shares or not shares.isdigit() or int(shares) <= 0:
            return apology("Must be a positive number of shares")
        else:
            shares = int(shares)

        for stock in stocks:
            if stock["symbol"] == symbol:
                if stock["total_shares"] < shares:
                    return apology("You don't have enough shares")
                else:
                    quote = lookup(symbol)
                    if quote is None:
                        return apology("Symbol not found")
                    price = quote["price"]
                    total_sale = shares * price

                    # update user
                    db.execute(
                        "UPDATE users SET cash = cash + :total_sale WHERE id = :user_id",
                        total_sale = total_sale,
                        user_id = session["user_id"]
                    )

                    # update history
                    db.execute(
                        "INSERT INTO transactions (user_id, symbol, shares, price) VALUES (:user_id, :symbol, :shares, :price)",
                        user_id = session["user_id"],
                        symbol = symbol,
                        shares = -shares,
                        price = price
                    )

                    flash(f"Sold {shares} shares of {symbol} for {usd(total_sale)}!")
                    return redirect("/")

        return apology("Symbol not found")
    else:
        return render_template("sell.html", stocks = stocks)
