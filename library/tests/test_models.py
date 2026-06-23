import pytest
from library.models import Author, Category, Book


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
        isbn="1234567890123",
        author=author,
        category=category,
        genre="fiction",
        total_copies=5,
        borrowed_copies=2
    )


@pytest.mark.django_db
def test_author_full(author):
    assert author.full_name == "John Doe"


@pytest.mark.django_db
def test_author_str(author):
    assert str(author) == "John Doe"   


@pytest.mark.django_db
def test_category_str(category):
    assert str(category) == "Dystopian"


@pytest.mark.django_db
def test_book_default_status(book):
    assert book.status == "available"


@pytest.mark.django_db
def test_book_genre_choices():
    genre = [choice[0] for choice in Book.GENRE_CHOICES]
    assert "fiction" in genre
    assert "technology" in genre


@pytest.mark.django_db
def test_book_status_choices():
    statuses = [choice[0] for choice in Book.STATUS_CHOICES]
    assert set(statuses) == {"available", "borrowed", "reserved"}


@pytest.mark.django_db
def test_is_available_true(book):
    assert book.is_available is True


@pytest.mark.django_db
def test_available_copies(book):
    assert book.available_copies == 3


@pytest.mark.django_db
def test_is_available_false(book):
    book.borrowed_copies = 5
    assert book.is_available is False


@pytest.mark.django_db
def test_author_has_timestamps(author):
    assert author.created_at is not None
    assert author.updated_at is not None


@pytest.mark.django_db
def test_book_has_timestamps(book):
    assert book.created_at is not None


@pytest.mark.django_db
def test_category_has_timestamps(category):
    assert category.created_at is not None
    assert category.updated_at is not None
    