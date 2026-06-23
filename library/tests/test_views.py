import pytest
from rest_framework.test import APIClient
from library.models import Author, Book, Category


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def author():
    return Author.objects.create(first_name="John", last_name="Doe")


@pytest.fixture
def category():
    return Category.objects.create(name="Dystopian")


@pytest.fixture
def book(author, category):
    return Book.objects.create(
        title="1984",
        isbn="9780451524935",
        author=author,
        category=category,
        genre="fiction",
        total_copies=3,
        borrowed_copies=1,
    )
    
    
# ── GET /api/books/ ───────────
@pytest.mark.django_db
def test_list_books_return_200(client, book):
    response = client.get("/api/books/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_books_returns_lightweight_data(client, book):
    response = client.get("/api/books/")
    data = response.json()
    assert "isbn" not in data[0]
    assert "title" in data[0]


@pytest.mark.django_db
def test_filter_books_by_genre(client, book):
    response = client.get("/api/books/?genre=fiction")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_filter_books_by_genre_no_match(client, book):
    response = client.get("/api/books/?genre=science")
    assert response.json() == []
    

@pytest.mark.django_db
def test_filter_books_by_status(client, book):
    response = client.get("/api/books/?status=available")
    assert response.status_code == 200
    assert len(response.json()) == 1
    

@pytest.mark.django_db
def test_filter_books_by_status_no_match(client, book):
    response = client.get("/api/books/?status=borrowed")
    assert response.json() == []


@pytest.mark.django_db
def test_filter_books_by_author(client, book):
    response = client.get("/api/books/?author=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_filter_books_by_author_no_match(client, book):
    response = client.get("/api/books/?author=2")
    assert response.json() == []
    

# ── POST /api/books/ ─────────────
@pytest.mark.django_db
def test_create_book_return_201(client, author, category):
    payload = {
        "title": "Brave New World",
        "isbn": "9780060850524",
        "author": author.id,
        "category": category.id,
        "genre": "fiction",
        "total_copies": 2,
        "borrowed_copies": 0,
    }
    response = client.post("/api/books/", payload, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_book_invalid_isbn_returns_400(client, author, category):
    payload = {
        "title": "Brave New World",
        "isbn": "123",
        "author": author.id,
        "genre": "fiction",
        "total_copies": 2,
        "borrowed_copies": 0,
    }
    response = client.post("/api/books/", payload, format="json")
    assert response.status_code == 400
    assert "isbn" in response.json()


# ── POST /api/books/{id}/borrow/ ────────
@pytest.mark.django_db
def test_borrow_book_decrement_copies(client, book):
    response = client.post(f"/api/books/{book.id}/borrow/")
    assert response.status_code == 200
    data = response.json()
    assert "available_copies" in data
    assert data["available_copies"] == 1
    
@pytest.mark.django_db
def test_borrow_book_unavailable_returns_400(client, author, category):
    fully_borrowed = Book.objects.create(
        title="Fully Borrowed",
        isbn="9781234567890",
        author=author,
        total_copies=1,
        borrowed_copies=1,
    )
    response = client.post(f"/api/books/{fully_borrowed.id}/borrow/")
    assert response.status_code == 400


# ── GET /api/authors/{id}/ ───────
@pytest.mark.django_db
def test_author_detail_returns_200(client, author):
    response = client.get(f"/api/authors/{author.id}/")
    assert response.status_code == 200
    assert response.json()["full_name"] == "John Doe"

# ── DELETE /api/books/{id}/ ────────
@pytest.mark.django_db
def test_delete_book_returns_204(client, book):
    response = client.delete(f"/api/books/{book.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_deleted_book_not_on_the_list(client, book):
    client.delete(f"/api/books/{book.id}/")
    response = client.get("/api/books/")
    assert response.json() == []
    

# ── GET /api/stats/ ──────
@pytest.mark.django_db
def test_state_return_correct_keys(client, book):
    response = client.get("/api/stats/")
    data = response.json()
    assert "total_books" in data
    assert "by_genre" in data
    assert "by_status" in data
    
    
@pytest.mark.django_db
def test_stats_total_books(client, book):
    response = client.get("/api/stats/")
    assert response.json()["total_books"] == 1