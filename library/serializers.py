from rest_framework import serializers
from .models import Author, Book, Category

# ── 1. Base serializer with dynamic field filtering ───────────
class DynamicFieldSerializer(serializers.ModelSerializer):
    '''
    A base serializer that allows you to pass a `fields` kwarg
    to limit which fields are returned. Uses set intersection to
    filter only the requested fields that actually exist.

    Example:
        AuthorSerializer(author, fields=["id", "full_name"])
    '''
    def __init__(self, *args, **kwargs):
        requested_fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        
        if requested_fields is not None:
            allowed = set(requested_fields)
            existing = set(self.fields)
            # Set intersection: only keep fields that were both requested AND exist
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
                
# ── 2. Author serializer ──────────────
class AuthorSerializer(DynamicFieldSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "full_name", "bio", 
                  "created_at"]


# ── 3. Category serializer ─────────────
class CategorySerializer(DynamicFieldSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


# ── 4. Full book serializer ────────────────
class BookSerializer(DynamicFieldSerializer):
    author_name = serializers.ReadOnlyField(source="author.full_name")
    available_copies = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "author",
            "author_name",
            "category",
            "genres",
            "status",
            "total_copies",
            "borrowed_copies",
            "available_copies",
            "is_available",
            "created_at",
        ]


    def validate_isbn(self, value):
        # Strip Whitespace from both ends
        value = value.strip()
        # ISBN-13 must be exactly 13 digits
        if len(value) != 13:
            raise serializers.ValidationError("ISBN-13 must be "
                                                "exactly 13 digits.")
        if not value.isdigit():
            raise serializers.ValidationError("ISBN-13 must contain "
                                                "only digits.")           
        return value


# ── 5. Lightweight serializer for list views (OOP polymorphism) ─────
class BookListSerializer(BookSerializer):
    """
    Inherits BookSerializer but returns fewer fields.
    Used for GET /api/books/ to keep list responses light.
    """
    
    class Meta(BookSerializer.Meta):
        fields = [
            "id",
            "title",
            "author_name",
            "genres",
            "status",
            "is_available"
        ]