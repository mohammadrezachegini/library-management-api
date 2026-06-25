from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from .models import Author, Category, Book
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    BookSerializer,
    BookListSerializer,
    BorrowBookResponseSerializer,
    LibraryStatsSerializer,
)


# ── Book views ────────────────────────────────
@extend_schema_view(
    get=extend_schema(
        summary="List all books",
        description=(
            "Returns a lightweight list of all books. "
            "Supports filtering by genre, status, and author."
        ),
        parameters=[
            OpenApiParameter(
                name="genre",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by genre (e.g. fiction, science, history)",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by status (available, borrowed, reserved)",
                required=False,
            ),
            OpenApiParameter(
                name="author",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by author ID",
                required=False,
            ),
        ],
    ),
    post=extend_schema(
        summary="Create a book",
        description="Creates a new book. ISBN must be exactly 13 digits.",
        examples=[
            OpenApiExample(
                name="Valid book",
                value={
                    "title": "1984",
                    "isbn": "9780451524935",
                    "author": 1,
                    "category": 1,
                    "genre": "fiction",
                    "total_copies": 3,
                    "borrowed_copies": 0,
                },
            )
        ],
    ),
)
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.select_related("author", "category").all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BookListSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.query_params.get("genre")
        status_filter = self.request.query_params.get("status")
        author = self.request.query_params.get("author")

        if genre:
            queryset = queryset.filter(genre=genre)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if author:
            queryset = queryset.filter(author__id=author)

        return queryset


@extend_schema_view(
    get=extend_schema(summary="Get a book by ID"),
    put=extend_schema(summary="Update a book"),
    patch=extend_schema(summary="Partially update a book"),
    delete=extend_schema(summary="Delete a book"),
)
class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.select_related("author", "category").all()
    serializer_class = BookSerializer


# ── Borrow a book (functional view) ───────────────────
@extend_schema(
    summary="Borrow a book",
    description=(
        "Decrements available copies by 1. "
        "Returns 400 if no copies are available."
    ),
    responses={200: BorrowBookResponseSerializer},
)
@api_view(["POST"])
def borrow_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(
            {"error": "Book not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not book.is_available:
        return Response(
            {"error": "No copies available."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    book.borrowed_copies += 1
    book.save()

    return Response(
        {
            "message": f"You borrowed '{book.title}'.",
            "available_copies": book.available_copies,
        },
        status=status.HTTP_200_OK,
    )


# ── Author views ──────────────────
@extend_schema_view(
    get=extend_schema(summary="List all authors"),
    post=extend_schema(summary="Create an author"),
)
class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


@extend_schema(summary="Get an author by ID with their books")
class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.prefetch_related("books").all()
    serializer_class = AuthorSerializer


# ── Category views ─────────
@extend_schema_view(
    get=extend_schema(summary="List all categories"),
    post=extend_schema(summary="Create a category"),
)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ── Stats (functional view) ────────────
@extend_schema(
    summary="Library statistics",
    description="Returns total counts and a breakdown by genre and status.",
    responses={200: LibraryStatsSerializer},
)
@api_view(["GET"])
def library_stats(request):
    genre_stats = {
        genre: Book.objects.filter(genre=genre).count()
        for genre, _ in Book.GENRE_CHOICES
    }

    status_stats = {
        s: Book.objects.filter(status=s).count()
        for s, _ in Book.STATUS_CHOICES
    }

    data = {
        "total_books": Book.objects.count(),
        "total_authors": Author.objects.count(),
        "total_categories": Category.objects.count(),
        "by_genre": genre_stats,
        "by_status": status_stats,
    }

    return Response(data)
