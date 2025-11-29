import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def book_attrs():
    return {
        "isbn": "9783161484101",
        "title": "Test Driven Development",
        "author": "Kent Beck",
        "publisher": "Addison-Wesley",
        "publication_year": 2003,
        "category": "TECHNOLOGY",
        "description": "Classic on building software guided by tests.",
        "language": "Français",
        "pages": 220,
        "total_copies": 5,
        "available_copies": 5,
    }


@pytest.fixture
def persisted_book(book_attrs):
    return Book.objects.create(**book_attrs)


@pytest.mark.django_db
def test_list_books_returns_paginated_results(api_client, persisted_book):
    response = api_client.get("/api/books/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == persisted_book.title


@pytest.mark.django_db
def test_get_book_not_found(api_client):
    response = api_client.get("/api/books/999/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "Livre non trouvé"


@pytest.mark.django_db
def test_get_book_returns_payload(api_client, persisted_book):
    response = api_client.get(f"/api/books/{persisted_book.id}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["isbn"] == persisted_book.isbn


@pytest.mark.django_db
def test_create_book_creates_record(api_client, book_attrs):
    payload = {**book_attrs, "isbn": "9783161484102"}

    response = api_client.post("/api/books/create/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert Book.objects.filter(isbn="9783161484102").exists()


@pytest.mark.django_db
def test_update_book_mutates_record(api_client, persisted_book):
    payload = {
        "isbn": persisted_book.isbn,
        "title": "Updated title",
        "author": persisted_book.author,
        "publisher": persisted_book.publisher,
        "publication_year": persisted_book.publication_year,
        "category": persisted_book.category,
        "description": persisted_book.description,
        "language": persisted_book.language,
        "pages": persisted_book.pages,
        "total_copies": persisted_book.total_copies,
        "available_copies": persisted_book.available_copies,
        "times_borrowed": persisted_book.times_borrowed,
        "average_rating": "0.00",
        "is_available": True,
    }

    response = api_client.put(
        f"/api/books/update/{persisted_book.id}/", payload, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    persisted_book.refresh_from_db()
    assert persisted_book.title == "Updated title"


@pytest.mark.django_db
def test_delete_book_removes_record(api_client, persisted_book):
    response = api_client.delete(f"/api/books/delete/{persisted_book.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Book.objects.filter(id=persisted_book.id).exists()


@pytest.mark.django_db
def test_search_books_requires_query(api_client):
    response = api_client.get("/api/search/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "q" in response.data["error"]


@pytest.mark.django_db
def test_search_books_filters_results(api_client, persisted_book):
    response = api_client.get("/api/search/", {"q": "kent"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["author"] == persisted_book.author

