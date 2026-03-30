from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import Author, Book, db
from datetime import datetime
import os
import requests

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(project_root, 'data/library.sqlite')}"
db.init_app(app)
app.secret_key = 'mykey_123'

app.secret_key = 'key'

with app.app_context():
    db.create_all()

def get_book_cover(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    book_info = response.json()

    if "items" in book_info:
        volume_info = book_info["items"][0]["volumeInfo"]
        if "imageLinks" in volume_info:
            return volume_info["imageLinks"].get("thumbnail")


@app.route('/', methods=['GET'])
def home():
    keyword = request.args.get('search')
    query = db.session.query(Book, Author).join(Author, Book.author_id == Author.id)

    if keyword:
        query = query.filter(Book.title.like(f"%{keyword}%"))

    books_with_authors = query.all()
    return render_template('home.html', books=books_with_authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birthdate','').strip()
        date_of_death_str = request.form.get('date_of_death','').strip()

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        name_does_exist = db.session.query(Author).filter_by(name=name).first()
        if name_does_exist:
            return f"Author {name} already exists in DB", 400

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        flash(f"Author {name} added successfully")
        return redirect(url_for('add_author'))


    elif request.method == 'GET':
        return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = int(request.form.get('publication_year')) if request.form.get('publication_year') else None
        author_id = int(request.form.get('author_id'))
        cover_url = get_book_cover(isbn)

        book_does_exist = db.session.query(Book).filter_by(title=title).first()
        if book_does_exist:
            return f"Book {title} already exists in DB", 400

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            cover_url=cover_url
        )

        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' added successfully")
        return redirect(url_for('add_book'))

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

