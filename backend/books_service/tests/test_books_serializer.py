import pytest

from books.models import Book
from books.serializers import BookSerializer


@pytest.fixture
def book_payload():
    return {
        "isbn": "9780306406157",
        "title": "Serializer under test",
        "author": "Data Builder",
        "publisher": "Pytest Press",
        "publication_year": 2021,
        "category": "SCIENCE",
        "description": "Payload verifying serializer behavior.",
        "language": "Français",
        "pages": 120,
        "total_copies": 4,
        "available_copies": 4,
        "times_borrowed": 0,
        "average_rating": "0.00",
        "is_available": True,
    }


@pytest.mark.django_db
def test_book_serializer_outputs_all_fields(book_payload):
    Book.objects.create(**book_payload)
    instance = Book.objects.first()

    data = BookSerializer(instance).data

    for field in book_payload:
        assert data[field] == book_payload[field]


@pytest.mark.django_db
def test_book_serializer_requires_fields(book_payload):
    incomplete_payload = {key: book_payload[key] for key in ("isbn", "title")}

    serializer = BookSerializer(data=incomplete_payload)

    assert not serializer.is_valid()
    assert "author" in serializer.errors
    assert "pages" in serializer.errors

