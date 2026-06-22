from .models import Book

# ── 1. Genre stats dict from tuple choices ──────
def get_genre_stats():
    """
    Iterates over GENRE_CHOICES tuple and builds a dict
    of genre -> count of books in that genre.
    """
    return {
        genre: Book.objects.filter(genre=genre).count()
        for genre, _ in Book.GENRE_CHOICES
    }

# ── 2. Genre deduplication using sets ─────────
def deduplicate_genres(genres):
    """
    Takes a list of genre strings, returns only the valid unique ones.
    Uses set intersection against allowed choices.

    Example:
        deduplicate_genres(["fiction", "fiction", "unknown"])
        → {"fiction"}
    """
    allowed = {genre for genre, _ in Book.GENRE_CHOICES}
    return set(genres) & allowed

# ── 3. Format book titles using map() ──────
def format_book_titles(queryset):
    """
    Takes a Book queryset, returns a list of formatted title strings.
    Demonstrates map() with a lambda over a queryset.

    Example:
        ["FICTION: 1984", "FICTION: Animal Farm"]
    """
    return list(
        map(lambda book: f"{book.genre.upper()}: {book.title}", queryset)
    )
    
    
# ── 4. Build author summary using *args and **kwargs ────
def build_anthor_summary(*args, **kwargs):
    """
    *args   → author full names (positional)
    **kwargs → options like separator, uppercase

    Example:
        build_author_summary("George Orwell", "J.K. Rowling", separator=" | ")
        → "George Orwell | J.K. Rowling"
    """
    separator = kwargs.get("separator", ", ")
    uppercase = kwargs.get("uppercase", False)
    
    names = list(args)
    
    if uppercase:
        names = [name.upper() for name in names]
        
    return separator.join(names)

# ── 5. ISBN validation with string processing ──────────
def validate_isbn(isbn):
    """
    Validates an ISBN-13:
    - Strip whitespace
    - Must be exactly 13 characters
    - Must be all digits
    - Checksum: alternating weights 1 and 3, sum % 10 == 0

    Returns (True, isbn) on success or (False, error_message) on failure.
    """
    isbn = isbn.strip()
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 characters."
    
    if not isbn.isdigit():
        return False, "ISBN must contain only digits."
    
    # ISBN-13 checksum: multiply each digit by 1 or 3 alternating
    digits = [int(d) for d in isbn]
    weights = [1 if i % 2 == 0 else 3 for i in range(13)]
    total = sum(d * w for d, w in zip(digits, weights))
    
    if total % 10 != 0:
        return False, "ISBN checksum is invalid"
    
    return True, isbn

