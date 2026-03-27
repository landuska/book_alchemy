from flask import Flask, render_template, request, redirect, url_for
from data_models import Author, Book, db
from datetime import datetime
import os
import requests

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(project_root, 'data/library.sqlite')}"
db.init_app(app)

with app.app_context():
    db.create_all()

def get_book_cover(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    book_info = response.json()

    if "items" in book_info:
        volume_info = book_info["items"][0]["volumeInfo"]
        if "imageLinks" in volume_info:
            return volume_info["imageLinks"].get("Thumbnail")

@app.route('/', methods=['GET'])
def home():
    books_with_authors = db.session.query(Book.title, Book.isbn, Book.cover_url, Author.name)\
                         .join(Author)\
                         .all()

    return render_template('home.html', books=books_with_authors)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
        date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        return redirect(url_for('add_author', message=f"Author {new_author.name} was added successfully"))


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

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            cover_url=cover_url
        )

        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('add_book', message=f"Book '{new_book.title}' was added successfully"))

    elif request.method == 'GET':
        return render_template('add_book.html', authors=authors)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

