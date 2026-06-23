from django.db import models

# Create your models here.

class TimeStampModels(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # No database table will be created for this model
        
        
class Author(TimeStampModels):
    first_name = models.CharField(max_length=100)
    last_name =  models.CharField(max_length=100)
    bio = models.TextField()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.full_name
    
    
class Category(TimeStampModels):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    

class Book(TimeStampModels):
    
    STATUS_CHOICES = (
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("reserved", "Reserved"),
    )
    
    GENRE_CHOICES = (
        ("fiction", "Fiction"),
        ("non-fiction", "Non-Fiction"),
        ("science", "Science"),
        ("history", "History"),
        ("biography", "Biography"),
        ("technology", "Technology"),
    )
    
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='books'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    genre = models.CharField(
        max_length=20, choices=GENRE_CHOICES, default="fiction"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="available"
    )
    total_copies = models.PositiveIntegerField(default=1)
    borrowed_copies = models.PositiveIntegerField(default=0)
    
    @property
    def available_copies(self):
        return self.total_copies - self.borrowed_copies
    
    @property
    def is_available(self):
        return self.available_copies > 0
    
    def __str__(self):
        return f"{self.title} by {self.author.full_name}"
    