import pytest
from django.utils import timezone
from books.models import Book

@pytest.mark.django_db
def test_book_creation():
    b = Book.objects.create(
        title="Test Book",
        author="Author Name",
        isbn="ISBN123456",
        available=True,
        created_at=timezone.now() if hasattr(Book, 'created_at') else None
    )
    assert Book.objects.count() == 1
    assert b.title == "Test Book"
    assert b.available is True