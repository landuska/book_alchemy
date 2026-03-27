from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    birth_date: Mapped[date] = mapped_column(Date)
    date_of_death: Mapped[date] = mapped_column(Date, nullable=True)

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

    def __repr__(self):
        return f"Book (id={self.id}, isbn={self.isbn}, title={self.title}, publication_year={self.publication_year}, author_id={self.author_id})"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"

