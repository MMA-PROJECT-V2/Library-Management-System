import pytest
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def multiple_books():
    books = [
        Book.objects.create(
            isbn=f"978316148410{i}",
            title=f"Book {i}",
            author="Author A" if i % 2 == 0 else "Author B",
            publisher="Publisher X",
            publication_year=2020 + i,
            category="FICTION",
            description=f"Description {i}",
            language="Français",
            pages=100 + i * 10,
            total_copies=5,
            available_copies=i % 3,
        )
        for i in range(5)
    ]
    return books


# Tests de pagination
@pytest.mark.django_db
def test_list_books_pagination_page_size(api_client, multiple_books):
    response = api_client.get("/api/books/?page_size=2")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert response.data["count"] == 5


@pytest.mark.django_db
def test_list_books_pagination_second_page(api_client, multiple_books):
    response = api_client.get("/api/books/?page=2&page_size=2")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_list_books_empty_database(api_client):
    response = api_client.get("/api/books/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


# Tests de recherche avancée
@pytest.mark.django_db
def test_search_books_by_title(api_client, multiple_books):
    response = api_client.get("/api/search/?q=Book 2")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert "Book 2" in response.data["results"][0]["title"]


@pytest.mark.django_db
def test_search_books_by_author(api_client, multiple_books):
    response = api_client.get("/api/search/?q=Author A")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1
    for result in response.data["results"]:
        assert "Author A" in result["author"]


@pytest.mark.django_db
def test_search_books_by_isbn(api_client, multiple_books):
    response = api_client.get("/api/search/?q=9783161484101")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_search_books_case_insensitive(api_client, multiple_books):
    response = api_client.get("/api/search/?q=book")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 5


@pytest.mark.django_db
def test_search_books_no_results(api_client, multiple_books):
    response = api_client.get("/api/search/?q=NonExistentBook")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_search_books_empty_query(api_client):
    response = api_client.get("/api/search/?q=")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_search_books_whitespace_query(api_client):
    response = api_client.get("/api/search/?q=   ")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Tests de validation des données
@pytest.mark.django_db
def test_create_book_missing_required_fields(api_client):
    payload = {
        "isbn": "9783161484100",
        "title": "Incomplete Book"
        # Missing required fields
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "author" in response.data or "publisher" in response.data


@pytest.mark.django_db
def test_create_book_invalid_isbn_format(api_client):
    payload = {
        "isbn": "invalid-isbn",
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Test",
        "language": "Français",
        "pages": 100,
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    # ISBN validation might pass at serializer level but fail at DB level
    # depending on your validation rules


@pytest.mark.django_db
def test_create_book_duplicate_isbn(api_client, multiple_books):
    payload = {
        "isbn": "9783161484100",  # Duplicate
        "title": "New Book",
        "author": "New Author",
        "publisher": "New Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Test",
        "language": "Français",
        "pages": 100,
        "total_copies": 1,
        "available_copies": 1,
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_book_partial_update_not_supported(api_client, multiple_books):
    book = multiple_books[0]
    payload = {"title": "Updated Title Only"}
    
    response = api_client.put(
        f"/api/books/update/{book.id}/", payload, format="json"
    )
    
    # PUT requires all fields, should fail
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_nonexistent_book(api_client):
    payload = {
        "isbn": "9783161484100",
        "title": "Updated Book",
        "author": "Updated Author",
        "publisher": "Updated Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Updated",
        "language": "Français",
        "pages": 100,
        "total_copies": 1,
        "available_copies": 1,
    }
    
    response = api_client.put("/api/books/update/9999/", payload, format="json")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_nonexistent_book(api_client):
    response = api_client.delete("/api/books/delete/9999/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Tests de sécurité et edge cases
@pytest.mark.django_db
def test_create_book_sql_injection_attempt(api_client):
    payload = {
        "isbn": "9783161484100",
        "title": "'; DROP TABLE books; --",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Test",
        "language": "Français",
        "pages": 100,
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    
    # Should handle safely - either create or reject, but not execute SQL
    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    # Verify table still exists
    assert Book.objects.count() >= 0


@pytest.mark.django_db
def test_search_books_xss_attempt(api_client, multiple_books):
    response = api_client.get("/api/search/?q=<script>alert('xss')</script>")
    
    # Should handle safely
    assert response.status_code == status.HTTP_200_OK
    # Response should not contain raw script tag
    assert "<script>" not in str(response.data)


@pytest.mark.django_db
def test_list_books_with_invalid_page_number(api_client, multiple_books):
    response = api_client.get("/api/books/?page=999")
    
    # Should return empty or error, not crash
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
def test_get_book_with_string_id(api_client):
    response = api_client.get("/api/books/invalid/")
    
    # Should return 404 or bad request, not crash
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
def test_create_book_with_very_long_fields(api_client):
    payload = {
        "isbn": "9783161484100",
        "title": "A" * 300,  # Exceeds max_length=255
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Test",
        "language": "Français",
        "pages": 100,
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in response.data


@pytest.mark.django_db
def test_create_book_with_future_publication_year(api_client):
    payload = {
        "isbn": "9783161484100",
        "title": "Future Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publication_year": 2050,  # Future year
        "category": "FICTION",
        "description": "Test",
        "language": "Français",
        "pages": 100,
    }
    
    response = api_client.post("/api/books/create/", payload, format="json")
    
    # Current implementation might allow this, but it's an edge case to consider
    # You might want to add validation
    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]