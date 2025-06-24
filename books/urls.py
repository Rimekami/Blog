# books/urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('add/', views.BookCreateView.as_view(), name='add'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='delete'),
    path('<int:pk>/update-status/', views.update_book_status, name='update_status'),
    
    # API endpoints
    path('api/search/', views.search_books_api, name='api_search'),
    path('api/isbn/', views.get_book_by_isbn_api, name='api_isbn'),
    path('api/title-author/', views.search_by_title_author_api, name='api_title_author'),
]