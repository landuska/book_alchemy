from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import Author, Book, db
from datetime import datetime
import os
from helpers import get_book_cover

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(project_root, 'data/library.sqlite')}"
db.init_app(app)
app.secret_key = 'flashkey'

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def home():
    """
    Displays the homepage with a list of all books and their authors.

    Supports searching for books by title via the 'search' query parameter.

    Returns:
        Rendered HTML template 'home.html' with a list of (Book, Author) tuples.
    """
    keyword = request.args.get('search')
    query = db.session.query(Book, Author).join(Author, Book.author_id == Author.id)

    if keyword:
        query = query.filter(Book.title.ilike(f"%{keyword}%"))

    books_with_authors = query.all()
    return render_template('home.html', books=books_with_authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handles displaying the form and adding a new author to the database.

    GET: Displays a page with an empty form.
    POST: Accepts form data (name, birthdate, date of death),
          validates them, and creates a new Author record.

    Returns:
        GET: Rendered template 'add_author.html'.
        POST: Redirect back to '/add_author' with a flash message.
    """
    if request.method == 'POST':
        input_name = request.form.get('name')
        input_birth_date_str = request.form.get('birthdate','').strip()
        input_date_of_death_str = request.form.get('date_of_death','').strip()

        try:
            birth_date = datetime.strptime(input_birth_date_str, '%Y-%m-%d').date() if input_birth_date_str else None
            date_of_death = datetime.strptime(input_date_of_death_str, '%Y-%m-%d').date() if input_date_of_death_str else None
        except ValueError:
            flash("error: date format should be DD-MM-YYYY")
            return redirect(url_for("add_author"))

        name_does_exist = db.session.query(Author).filter_by(name=input_name).first()
        if name_does_exist:
            flash(f"Author {input_name} already exists in DB")
            return redirect(url_for("add_author"))

        try:
            new_author = Author(
                name=input_name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )
            db.session.add(new_author)
            db.session.commit()
            flash(f"Author {input_name} added successfully")

        except ValueError as e:
            db.session.rollback()
            flash(f"error: {e}")
            return redirect(url_for("add_author"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}")
            return redirect(url_for("add_author"))

        return redirect(url_for("add_author"))

    elif request.method == "GET":
        return render_template("add_author.html")

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Handles displaying the form and adding a new book to the database.

    GET: Displays a page with the book creation form and author list.
    POST: Accepts form data (title, ISBN, publication year, author),
          fetches the book cover via Google Books API, and saves the book.

    Returns:
        GET: Rendered template 'add_book.html' with Author objects for the dropdown.
        POST: Redirect back to '/add_book' with a flash message.
    """
    authors = db.session.query(Author).all()

    if request.method == 'POST':
        input_title = request.form.get('title')
        input_isbn = request.form.get('isbn')
        input_publication_year = request.form.get('publication_year')
        input_author_id = request.form.get('author_id')
        input_rating = request.form.get('rating')

        isbn = input_isbn.replace('-', '').strip()

        if len(isbn) < 10 or not isbn.isdigit():
            flash("ISBN of book should have at least 10 digits")
            return redirect(url_for("add_book"))

        book_does_exist = db.session.query(Book).filter_by(isbn=isbn).first()

        if book_does_exist:
            flash(f"Book {input_title} already exists in DB")
            return redirect(url_for("add_book"))

        try:
            new_book = Book(
                title=input_title,
                isbn=input_isbn,
                publication_year=input_publication_year,
                author_id=input_author_id,
                rating=input_rating
            )

            try:
                new_book.cover_url = get_book_cover(input_isbn)
            except Exception:
                flash("Could not fetch book cover from API.")

            db.session.add(new_book)
            db.session.commit()
            flash(f"Book '{input_title}' added successfully")
        except ValueError as e:
            db.session.rollback()
            flash(f"error: {e}")
            return redirect(url_for("add_book"))

        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {e}")
            return redirect(url_for("add_book"))

        return redirect(url_for("add_book"))

    elif request.method == 'GET':
        return render_template('add_book.html', authors=authors)

@app.route('/sort', methods=['GET'])
def sort():
    """
    Displays a sorted list of books on a separate page.

    Accepts the 'sort' query parameter:
    - 'publication_year': Sorts by publication year (ascending).
    - 'author': Sorts by author's name (alphabetically).
    - Any other value (or none): No specific sorting applied.

    Returns:
        Rendered HTML template 'sort.html' with the sorted data.
    """
    sort_by = request.args.get('sort')
    query = db.session.query(Book, Author).join(Author, Book.author_id == Author.id)

    if sort_by == 'publication_year':
        books = query.order_by(Book.publication_year).all()
    elif sort_by == 'author':
        books = query.order_by(Author.name).all()
    else:
        books = query.all()

    return render_template('sort.html', books=books)


@app.route("/book/<int:book_id>/delete", methods=['POST'])
def delete_book(book_id):
    """
    Deletes a book from the database by its ID.

    If the author has no other books left in the database after the deletion,
    that author is also automatically removed.

    Args:
        book_id (int): The unique identifier of the book to be deleted.

    Returns:
        Redirect to the homepage (home).
    """
    book = db.session.get(Book, book_id)

    if book:
        author_id = book.author_id
        db.session.delete(book)
        flash(f"Book {book.title} deleted successfully")

        other_books_of_this_author_exist = db.session.query(Book).filter(Book.author_id == author_id).first()

        if not other_books_of_this_author_exist:
            author = db.session.get(Author, author_id)
            if author:
                db.session.delete(author)
                flash(f"Author {author.name} deleted successfully")
    try:
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        flash(f"error: {e}")
        return redirect(url_for("delete_book"))

    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {e}")
        return redirect(url_for("delete_book"))

    return redirect(url_for('home'))


@app.route("/book/<int:book_id>", methods=['GET'])
def get_book_info(book_id):
    """
    Displays detailed information about a specific book.

    Fetches the book and its associated author based on the book's ID.

    Args:
        book_id (int): The unique identifier of the book to retrieve.

    Returns:
        Rendered HTML template 'book_info.html' with the book and author objects.
        If the book is not found, redirects to the homepage with a flash message.
    """
    book = db.session.get(Book, book_id)

    if not book:
        flash("Error: Book not found")
        return redirect(url_for('home'))

    author = db.session.get(Author, book.author_id)
    return render_template("book_info.html", book=book, author=author)


@app.route("/authors", methods=['GET'])
def show_authors():
    """
    Displays a list of all authors and the titles of books they have written.

    Returns:
        Rendered HTML template 'authors.html' containing a list of dictionaries,
        where each dictionary has an 'author' object and a list of 'books' titles.
    """
    all_data = db.session.query(Book, Author).join(Author, Book.author_id == Author.id).all()
    authors_dict = {}

    for book, author in all_data:
        if author.id not in authors_dict:
            authors_dict[author.id] = {
                "author": author,
                "books": []
            }
        authors_dict[author.id]["books"].append(book.title)
    authors_books = list(authors_dict.values())
    return render_template("authors.html", authors=authors_books)


@app.route("/book/<int:book_id>/rate", methods=['POST'])
def rate_book(book_id):
    """
    Updates the rating of a specific book in the database.

    Accepts form data containing the numerical 'rating'.
    If valid, updates the database. If the model validation fails (e.g.,
    rating out of range), catches the error and displays the message.

    Args:
        book_id (int): The unique identifier of the book to rate.

    Returns:
        Redirects back to the previous page (or homepage) with a flash message.
    """
    book = db.session.get(Book, book_id)
    if not book:
        flash("error: Book not found")
        return redirect(url_for('home'))

    input_rating = request.form.get('rating')

    if not input_rating:
        flash("error: Please enter a rating")
        return redirect(url_for('home'))

    try:
        book.rating = int(input_rating)
        db.session.commit()
        flash(f"Rated '{book.title}' as {input_rating}/10")
    except ValueError as e:
        db.session.rollback()
        flash(f"error: {e}")

    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {e}")
        return redirect(url_for("delete_book"))

    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    """Custom error handler for 404 (Page Not Found) errors."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    """Custom error handler for 500 (Internal Server Error) errors."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

