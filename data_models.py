from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    birth_date: Mapped[date] = mapped_column(Date)
    date_of_death: Mapped[date] = mapped_column(Date, nullable=True)

    @validates('name')
    def validate_name(self, key, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value.strip()

    @validates('birth_date', 'date_of_death')
    def validate_dates(self, key, value):
        if value and value > date.today():
            raise ValueError("Birthdate or deathdate cannot be in the future")
        return value

    def __repr__(self):
        return f"Author (id={self.id}, name={self.name}, birth_date={self.birth_date}, date_of_death={self.date_of_death})"

    def __str__(self):
        if self.date_of_death is None:
            return f"{self.name} ({self.birth_date})"
        else:
            return f"{self.name} ({self.birth_date} - {self.date_of_death})"


class Book(db.Model):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String, unique=True)
    publication_year: Mapped[int] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'))
    cover_url: Mapped[str] = mapped_column(String, nullable=True)

    @validates('title')
    def validate_title(self, key, value):
        if not value:
            raise ValueError("Title of book cannot be empty")
        return value.strip()

    @validates('isbn')
    def validate_isbn(self, key, value):
        if not value or len(value.replace('-', '')) < 10:
            raise ValueError("ISBN of book should have at least 10 digits")
        return value.strip()

    @validates('publication_year')
    def validate_publication_year(self, key, value):
        if value == '' or value is None or len(value) < 4:
            return None
        try:
            int_value = int(value)
        except ValueError:
            raise ValueError("Publication year must be a valid number")

        if int_value > date.today().year:
            raise ValueError("Publication year cannot be in the future")
        return int_value

    @validates('author_id')
    def validate_author_id(self, key, value):
        if value == '' or value is None:
            raise ValueError("Please select an author for the book")
        try:
            return int(value)
        except ValueError:
            raise ValueError("Invalid author selected")

    @validates('cover_url')
    def validate_cover_url(self, key, value):
        if value and not ((value.startswith('http://') or value.startswith('https://'))):
            raise ValueError("URL of cover url should start with http:// or https://")
        return value.strip() if value else None

    def __repr__(self):
        return f"Book (id={self.id}, isbn={self.isbn}, title={self.title}, publication_year={self.publication_year}, author_id={self.author_id})"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"

