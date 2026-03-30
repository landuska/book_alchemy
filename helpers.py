import requests

def get_book_cover(isbn):
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