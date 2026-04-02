# 📚 Flask Library Management System

A web application built with Flask and SQLAlchemy to manage a personal library of books and authors. The project features clean architecture with defensive programming, strict database integrity, and integration with the Google Books API.

## ✨ Features

* **Author Management:** Add authors with birth and death dates. Automated cleanup deletes authors when they have no books left.
* **Book Management:** Add books with title, ISBN, publication year, cover image and rating.
* **Defensive Validation:** Strict data validation on the model level (`@validates`) and the view level (`try/except`) ensures zero corrupted data.
* **API Integration:** Automatically fetches book cover images from the Google Books API using the ISBN.
* **Search & Sort:** Search books by title and sort them by author name or publication year.
* **Rating System:** Rate books on a scale from 1 to 10.

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask 3.1.3
* **Database & ORM:** SQLite, SQLAlchemy 2.0.48 (with strict `Mapped` typing)
* **API:** Google Books API (for cover fetching)

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have Python 3.x installed on your machine.

### 2. Installation & Setup

Install the required dependencies:

</>bash
pip install flask flask-sqlalchemy requests

### 2. Running the Application
To start the local development server, run:

</>bash
python code.py

Open your web browser and go to http://localhost:5000. 
The SQLite database will be created automatically on the first run.

## 📂 Project Structure
* **app.py** - The main Flask application containing routes, views, and error handlers.
* **data_models.py** - SQLAlchemy models with strict data validation rules.
* **helpers.py** - Helper functions (e.g., fetching book covers via external API).
* **data/** - Directory where the SQLite database file (library.sqlite) is stored.
* **templates/** - HTML templates for rendering the web pages.
* **static/** - Folder for static files like CSS, JS, and images.
* **config** - Configuration settings for Flask app and database.

## 🛡️ Architecture & Validation
This project follows the "Skinny Controller, Fat Model" principle and defensive programming:
* **Model Level (data_models.py):** -  Uses SQLAlchemy @validates to enforce data types, check for empty fields, and prevent illogical dates (like future dates or death before birth).
* **Controller Level (app.py):** -  Uses strict try/except ValueError blocks to catch validation errors and safely display them to the user using Flask's flash messages without crashing the application or corrupting the database.

## 📄 License
This project is an Education / Student Project and is open for learning and non-commercial use.
