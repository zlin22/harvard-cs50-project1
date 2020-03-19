import os
import requests

from flask import Flask, session, request, render_template, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():

    if "user_id" not in session:
       username = "not logged in"
    else:
       username = session["user_id"]

    return render_template("index.html", username=username)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register-result", methods=["POST"])
def registerResult():
    username = request.form.get("username")
    password = request.form.get("password")

    if len(username) == 0 or len(password) == 0:
        return render_template("register-result.html", resultMessage="fail", errorMessage="Error: username or password can not be blank")
    elif db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
        return render_template("register-result.html", resultMessage="fail", errorMessage="Error: username is already taken")
    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        return render_template("register-result.html", resultMessage="success", username=username)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
               {"username": username, "password": password}).rowcount > 0:
       session["user_id"] = username
       return render_template("search.html")
    else:
        return render_template("login-failed.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return render_template("logout-success.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
       return "You must be logged in to use this site!"

    searchText = request.form.get("searchText")

    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        books = db.execute("SELECT * FROM books WHERE lower(isbn) like '%' || lower(:searchText) || '%' or  lower(title) like '%' || lower(:searchText) || '%' or lower(author) like '%' || lower(:searchText) || '%' or cast(year as varchar) like '%' || :searchText || '%'", {"searchText": searchText}).fetchall()
        return render_template("search.html", books=books)

@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def bookDetails(isbn):
    if "user_id" not in session:
       return "You must be logged in to use this site!"

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_isbn = :isbn", {"isbn": book.isbn}).fetchall()

    # goodreads data from api
    goodreadsBookData = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "D2V9DlXvchAGi99LgUDojQ", "isbns":isbn})
    goodreadsBookJson = goodreadsBookData.json()

    return render_template("book.html", book=book, reviews=reviews, goodreadsBookJson=goodreadsBookJson)

@app.route("/book/<string:isbn>/submit-review", methods=["POST"])
def submitReview(isbn):
    if "user_id" not in session:
       return "You must be logged in to use this site!"

    rating = request.form.get("rating")
    comment = request.form.get("comment")
    book_isbn = isbn
    username = session["user_id"]

    if len(rating) == 0 or int(rating) < 1 or int(rating) > 5:
        return render_template("submit-review-fail.html", isbn=isbn)

    else:
        db.execute("DELETE FROM reviews WHERE book_isbn = :book_isbn AND username = :username", {"book_isbn": book_isbn, "username": username})

        db.execute("INSERT INTO reviews (rating, comment, book_isbn, username) VALUES (:rating, :comment, :book_isbn, :username)", {"rating": rating, "comment": comment, "book_isbn": book_isbn, "username": username})
        db.commit()

        return render_template("submit-review-success.html", isbn=isbn)

@app.route("/api/<string:isbn>")
def bookAPI(isbn):
    """return details about a single book"""

    #make sure book exists
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "ISBN not found"}), 404
    else:
        reviewCount = db.execute("SELECT count(*) count FROM reviews WHERE book_isbn = :isbn", {"isbn": isbn}).fetchone().count
        avgScore = float(db.execute("SELECT avg(rating) avg_rating FROM reviews WHERE book_isbn = :isbn", {"isbn": isbn}).fetchone().avg_rating)
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": reviewCount,
            "average_score": avgScore
        })
