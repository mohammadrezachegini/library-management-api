from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Author, Book, Category
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    BookListSerializer,
    CategorySerializer
)


# ── Book views ────────────────
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.select_related("author", "category").all()
    
    def get_serializer_class(self):
        if self.request.method == "GET":
            return BookListSerializer
        return BookSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        genres = self.request.query_params.get("genres")
        status_filter = self.request.query_params.get("status")
        author = self.request.query_params.get("author")
        
        if genres:
            queryset = queryset.filter(genres=genres)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if author:
            queryset = queryset.filter(author__id=author)
        
        return queryset


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.select_related("author", "category").all()
    serializer_class = BookSerializer


# ── Borrow a book (functional view) ─────────
@api_view(["POST"])
def borrow_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({
            "error": "Book not found."
        }, status=status.HTTP_404_NOT_FOUND)
        
    if not book.is_available:
        return Response({
            "error": "Book is not available for borrowing."
        }, status=status.HTTP_400_BAD_REQUEST)
        
    book.borrowed_copies += 1
    book.save()
    return Response(
        {
            "message": f"You borrowed '{book.title}'.",
            "available_copies": book.available_copies,
        },
        status=status.HTTP_200_OK,
    )


# ── Author views ────────────
class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.prefetch_related("books").all()
    serializer_class = AuthorSerializer


# ── Category views ──────────
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ── Stats (functional view) ──────
@api_view(["GET"])
def library_stats(request):
    # Build genre breakdown dict from tuple choices
    genres_stats = {
        genres: Book.objects.filter(genres=genres).count()
        for genres, _ in Book.GENRE_CHOICES
    }
    # Build status breakdown dict from tuple choices
    status_stats = {
        s: Book.objects.filter(status=s).count()
        for s, _ in Book.STATUS_CHOICES
    }
    
    data = {
        "total_books": Book.objects.count(),
        "total_authors": Author.objects.count(),
        "total_categories": Category.objects.count(),
        "by_genre": genres_stats,
        "by_status": status_stats
    }
    
    return Response(data, status=status.HTTP_200_OK)