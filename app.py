

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


                    flash(f"Sold {shares} shares of {symbol} for {usd(total_sale)}!")
                    return redirect("/")

        return apology("Symbol not found")
    else:
        return render_template("sell.html", stocks = stocks)
