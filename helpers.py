import requests

def get_book_cover(isbn):
    """
    Fetches the cover image URL for a book from the Google Books API using its ISBN.

    Args:
        isbn (str): The International Standard Book Number of the book.

    Returns:
        str or None: The URL of the book's thumbnail image if found,
        None if no image is available, or an error message string if the
        request fails.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        book_info = response.json()

        if "items" in book_info:
            volume_info = book_info["items"][0]["volumeInfo"]
            if "imageLinks" in volume_info:
                return volume_info["imageLinks"].get("thumbnail")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"