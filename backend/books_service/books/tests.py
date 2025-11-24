import pytest
from rest_framework.test import APIClient
from books.models import Book


# ----------------------------
# FIXTURES
# ----------------------------

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def book_data():
    return {
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


@pytest.fixture
def updated_data():
    return {
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


# ----------------------------
# TESTS CRUD COMPLETS
# ----------------------------

def test_create_book(client, book_data):
    """Test de création d'un livre"""
    response = client.post('/api/books/create/', book_data, format='json')
    assert response.status_code == 201
    assert Book.objects.count() == 1
    assert Book.objects.first().title == "Livre Test"


def test_list_books(client, book_data):
    """Test d'affichage de la liste des livres"""
    Book.objects.create(**book_data)

    response = client.get('/api/books/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1


def test_get_book_detail(client, book_data):
    """Test détail d'un livre"""
    book = Book.objects.create(**book_data)

    response = client.get(f'/api/books/{book.id}/')
    assert response.status_code == 200
    assert response.data['title'] == "Livre Test"


def test_update_book(client, book_data, updated_data):
    """Test modification d'un livre"""
    book = Book.objects.create(**book_data)

    response = client.put(f'/api/books/update/{book.id}/', updated_data, format='json')
    assert response.status_code == 200

    book.refresh_from_db()
    assert book.title == "Livre Test Modifié"
    assert book.total_copies == 10


def test_delete_book(client, book_data):
    """Test suppression d'un livre"""
    book = Book.objects.create(**book_data)

    response = client.delete(f'/api/books/delete/{book.id}/')
    assert response.status_code == 204
    assert Book.objects.count() == 0
