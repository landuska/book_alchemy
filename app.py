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
app.secret_key = 'key'

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def home():
    keyword = request.args.get('search')
    query = db.session.query(Book, Author).join(Author, Book.author_id == Author.id)

    if keyword:
        query = query.filter(Book.title.ilike(f"%{keyword}%"))

    books_with_authors = query.all()
    return render_template('home.html', books=books_with_authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        input_name = request.form.get('name')
        input_birth_date_str = request.form.get('birthdate','').strip()
        input_date_of_death_str = request.form.get('date_of_death','').strip()

        try:
            birth_date = datetime.strptime(input_birth_date_str, '%Y-%m-%d').date() if input_birth_date_str else None
            date_of_death = datetime.strptime(input_date_of_death_str, '%Y-%m-%d').date() if input_date_of_death_str else None
        except ValueError:
            flash("Invalid date format")
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

        return redirect(url_for("add_author"))

    elif request.method == "GET":
        return render_template("add_author.html")

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = db.session.query(Author).all()

    if request.method == 'POST':
        input_title = request.form.get('title')
        input_isbn = request.form.get('isbn')
        input_publication_year = int(request.form.get('publication_year')) if request.form.get('publication_year') else None
        input_author_id = int(request.form.get('author_id'))

        book_does_exist = db.session.query(Book).filter_by(title=input_title).first()
        if book_does_exist:
            flash(f"Book {input_title} already exists in DB")
            return redirect(url_for("add_book"))

        try:
            new_book = Book(
                title=input_title,
                isbn=input_isbn,
                publication_year=input_publication_year,
                author_id=input_author_id
            )

            new_book.cover_url = get_book_cover(input_isbn)

            db.session.add(new_book)
            db.session.commit()
            flash(f"Book '{input_title}' added successfully")
        except ValueError as e:
            db.session.rollback()
            flash(f"error: {e}")
            return redirect(url_for("add_book"))

        return redirect(url_for("add_book"))

    elif request.method == 'GET':
        return render_template('add_book.html', authors=authors)

@app.route('/sort', methods=['GET'])
def sort():
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

    db.session.commit()

    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

