import pytest
from library.models import Book, Author
from library.utils import (
    get_genre_stats,
    deduplicate_genres,
    format_book_titles,
    build_author_summary,
    validate_isbn,
)


@pytest.fixture
def author():
    return Author.objects.create(first_name="John", last_name="Doe")


@pytest.fixture
def book(author):
    return Book.objects.create(
        title="1984",
        isbn="9780451524935",
        author=author,
        genre="fiction",
        total_copies=2,
        borrowed_copies=0,
    )


# ── get_genre_stats ──────────
@pytest.mark.django_db
def test_get_genre_stats_return_all_genres(book):
    stats = get_genre_stats()
    print(f"Genre stats: {stats}")
    assert set(stats.keys()) == {
        "fiction",
        "non-fiction",
        "science",
        "history",
        "biography",
        "technology",
    }


@pytest.mark.django_db
def test_genre_stats_count_correctly(book):
    stats = get_genre_stats()
    assert stats["fiction"] == 1
    assert stats["science"] == 0


# ── deduplicate_genres ─────────
def test_deduplicate_removes_duplicates():
    result = deduplicate_genres(["fiction", "fiction", "science"])
    assert result == {"fiction", "science"}


def test_deduplicate_removes_invalid_genres():
    result = deduplicate_genres(["fiction", "unknown", "fake"])
    assert result == {"fiction"}


def test_deduplicate_empty_input():
    result = deduplicate_genres([])
    assert result == set()


# ── format_book_titles ──────────
@pytest.mark.django_db
def test_format_book_titles(book):
    queryset = Book.objects.all()
    result = format_book_titles(queryset)
    assert result == ["FICTION: 1984"]


@pytest.mark.django_db
def test_format_book_titles_empty_queryset():
    queryset = Book.objects.none()
    assert format_book_titles(queryset) == []


# ── build_author_summary ─────────
def test_build_author_sumamry_default_seprator():
    result = build_author_summary("John Doe", "J.K. Rowling")
    assert result == "John Doe, J.K. Rowling"


def test_build_author_summary_custom_separator():
    result = build_author_summary("John Doe", "J.K. Rowling", separator=" | ")
    assert result == "John Doe | J.K. Rowling"


def test_build_author_summary_uppercase():
    result = build_author_summary("John Doe", "J.K. Rowling", uppercase=True)
    assert result == "JOHN DOE, J.K. ROWLING"


def test_build_author_summary_no_authors():
    result = build_author_summary()
    assert result == ""


# ── validate_isbn ───────
def test_validate_isbn():
    valid, result = validate_isbn("9780451524935")
    assert valid is True
    assert result == "9780451524935"


def test_isbn_strip_whitespce():
    valid, result = validate_isbn(" 9780451524935 ")
    assert valid is True
    assert result == "9780451524935"


def test_isbn_too_short():
    valid, message = validate_isbn("123456789")
    assert valid is False
    assert "13 digits" in message


def test_isbn_non_digits():
    valid, msg = validate_isbn("97804515249AB")
    assert valid is False
    assert "digits" in msg


def test_isbn_invalid_checksum():
    valid, message = validate_isbn("9780451524936")
    assert valid is False
    assert "checksum" in message
