from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.list_books),
    path('books/<int:id>/', views.get_book),
    path('books/create/', views.create_book),
    path('books/update/<int:id>/', views.update_book),
    path('books/delete/<int:id>/', views.delete_book),
  path('books/partial-update/<int:id>/', views.partial_update_book),
  path('books/<int:id>/borrow/', views.borrow_book),
  path('books/<int:id>/return/', views.return_book),
  path('books/<int:id>/reviews/create/', views.create_review),
  path('books/<int:id>/reviews/', views.list_reviews),
  path('search/', views.search_books, name='search_books'),
      
]
