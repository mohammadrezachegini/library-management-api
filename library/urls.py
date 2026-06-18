from django.urls import path
from . import views


urlpatterns = [
    # Book endpoints
    path("books/", views.BookListCreateView.as_view(), 
         name="book-list-create"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), 
         name="book-detail"),
    path("books/<int:pk>/borrow/", views.borrow_book, 
         name="book-borrow"),
    
    # Author endpoints
    path("authors/", views.AuthorListCreateView.as_view(), 
         name="author-list-create"),
    path("authors/<int:pk>/", views.AuthorDetailView.as_view(), 
         ame="author-detail"),
    
    # Category endpoints
    path("categories/", views.CategoryListCreateView.as_view(), 
         name="category-list-create"),
    
    #stats endpoints
    path("stats/", views.library_stats, name="library-stats"),
]