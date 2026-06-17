import pytest
from library.models import Author, Category, Book
from library.serializers import (
    AuthorSerializer,
    BookSerializer,
    BookListSerializer
)


@pytest.fixture
def author():
    return Author.objects.create(
        first_name="John",
        last_name="Doe"
    )


@pytest.fixture
def category():
    return Category.objects.create(
        name="Dystopian")


@pytest.fixture
def book(author, category):
    return Book.objects.create(
        title="1984",
        isbn="1234567890123",
        author=author,
        category=category,
        genres="fiction",
        status="available",
        total_copies=5,
        borrowed_copies=2
    )


# ── AuthorSerializer ─────────
@pytest.mark.django_db
def test_author_serializer_contains_full_name(author):
    data = AuthorSerializer(author).data
    assert data["full_name"] == "John Doe"


@pytest.mark.django_db
def test_dynamic_fields(author):
    data = AuthorSerializer(author, fields=["id", "full_name"]).data
    assert set(data.keys()) == {"id", "full_name"}
    assert set(data.values()) == {1, "John Doe"}


# ── BookSerializer: @property fields ─────
@pytest.mark.django_db
def test_book_serializer_available_copies(book):
    data = BookSerializer(book).data
    assert data["available_copies"] == 3


@pytest.mark.django_db
def test_book_serializer_is_available(book):
    data = BookSerializer(book).data
    assert data["is_available"] is True


@pytest.mark.django_db
def test_book_serializer_author_name(book):
    data = BookSerializer(book).data
    assert data["author_name"] == "John Doe"

# ── validate_isbn ────────────
@pytest.mark.django_db
def test_valid_isbn(author, category):
    payload = {
        "title": "Animal Farm",
        "isbn": "9876543210123",
        "author": author.id,
        "category": category.id,
        "genres": "fiction",
        "total_copies": 3,
        "borrowed_copies": 0
    }    
    serializer = BookSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_invalid_isbn_too_short(author, category):
    payload = {
        "title": "Animal Farm",
        "isbn": "12345",
        "author": author.id,
        "category": category.id,
        "genres": "fiction",
        "total_copies": 3,
        "borrowed_copies": 0
    }    
    serializer = BookSerializer(data=payload)
    assert not serializer.is_valid()
    assert "isbn" in serializer.errors


@pytest.mark.django_db
def test_invalid_isbn_non_digits(author, category):
    payload = {
        "title": "Animal Farm",
        "isbn": "ABCDEFGHIJKLM",
        "author": author.id,
        "category": category.id,
        "genres": "fiction",
        "total_copies": 3,
        "borrowed_copies": 0
    }
    serializer = BookSerializer(data=payload)
    assert not serializer.is_valid()
    assert "isbn" in serializer.errors


# ── BookListSerializer ────────
@pytest.mark.django_db
def test_book_list_serializer_limited_fields(book):
    data = BookListSerializer(book).data
    assert set(data.keys()) == {
       "id",
       "title",
       "author_name",
       "genres",
       "status",
       "is_available" 
    }


@pytest.mark.django_db
def test_book_list_serializer_no_isbn(book):
    data = BookListSerializer(book).data
    assert "isbn" not in data