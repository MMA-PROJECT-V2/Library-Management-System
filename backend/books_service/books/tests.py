
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book

class BookCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Données de test
        self.book_data = {
            "isbn": "1234567890123",
            "title": "Livre Test",
            "author": "Auteur Test",
            "publisher": "Editeur Test",
            "publication_year": 2025,
            "category": "FICTION",
            "description": "Description du livre test",
            "cover_image_url": "http://example.com/cover.jpg",
            "language": "Français",
            "pages": 100,
            "total_copies": 5,
            "available_copies": 5
        }
        self.updated_data = {
            "isbn": "1234567890123",
            "title": "Livre Test Modifié",
            "author": "Auteur Test",
            "publisher": "Editeur Modifié",
            "publication_year": 2025,
            "category": "FICTION",
            "description": "Description modifiée",
            "cover_image_url": "http://example.com/newcover.jpg",
            "language": "Français",
            "pages": 120,
            "total_copies": 10,
            "available_copies": 10
        }

    def test_create_book(self):
        response = self.client.post('/api/books/create/', self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, "Livre Test")

    def test_list_books(self):
        Book.objects.create(**self.book_data)
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_book_detail(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.get(f'/api/books/{book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Livre Test")

    def test_update_book(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.put(f'/api/books/update/{book.id}/', self.updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, "Livre Test Modifié")
        self.assertEqual(book.total_copies, 10)

    def test_delete_book(self):
        book = Book.objects.create(**self.book_data)
        response = self.client.delete(f'/api/books/delete/{book.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
