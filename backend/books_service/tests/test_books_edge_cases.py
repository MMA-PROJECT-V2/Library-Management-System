import pytest
from decimal import Decimal
from books.models import Book, BookReview
from books.serializers import BookSerializer, BookReviewSerializer


@pytest.fixture
def book_data():
    return {
        "isbn": "9781234567890",
        "title": "Edge Case Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "publication_year": 2024,
        "category": "FICTION",
        "description": "Test book for edge cases",
        "language": "Français",
        "pages": 100,
        "total_copies": 5,
        "available_copies": 5,
    }


# Tests pour BookReview model
@pytest.mark.django_db
def test_book_review_creation():
    review = BookReview.objects.create(
        book_id=1,
        user_id=1,
        rating=5,
        comment="Excellent livre!"
    )
    assert review.rating == 5
    assert review.comment == "Excellent livre!"
    assert str(review) == "Avis 5/5 sur livre 1"


@pytest.mark.django_db
def test_book_review_unique_constraint():
    BookReview.objects.create(book_id=1, user_id=1, rating=4)
    
    with pytest.raises(Exception):  # IntegrityError
        BookReview.objects.create(book_id=1, user_id=1, rating=5)


@pytest.mark.django_db
def test_book_review_rating_validation():
    serializer = BookReviewSerializer(data={
        "book_id": 1,
        "user_id": 1,
        "rating": 6,  # Invalid: max is 5
        "comment": "Test"
    })
    assert not serializer.is_valid()
    assert "rating" in serializer.errors


@pytest.mark.django_db
def test_book_review_rating_minimum_validation():
    serializer = BookReviewSerializer(data={
        "book_id": 1,
        "user_id": 1,
        "rating": 0,  # Invalid: min is 1
        "comment": "Test"
    })
    assert not serializer.is_valid()
    assert "rating" in serializer.errors


# Tests pour Book model - edge cases
@pytest.mark.django_db
def test_book_isbn_uniqueness(book_data):
    Book.objects.create(**book_data)
    
    with pytest.raises(Exception):  # IntegrityError
        Book.objects.create(**book_data)


@pytest.mark.django_db
def test_increment_copies_multiple_times(book_data):
    book = Book.objects.create(**book_data)
    initial_total = book.total_copies
    initial_available = book.available_copies
    
    book.increment_copies(3)
    book.refresh_from_db()
    
    assert book.total_copies == initial_total + 3
    assert book.available_copies == initial_available + 3
    assert book.is_available is True


@pytest.mark.django_db
def test_book_with_zero_pages_validation(book_data):
    book_data["pages"] = 0
    serializer = BookSerializer(data=book_data)
    
    assert not serializer.is_valid()
    assert "pages" in serializer.errors


@pytest.mark.django_db
def test_book_with_negative_copies_validation(book_data):
    book_data["total_copies"] = -1
    serializer = BookSerializer(data=book_data)
    
    assert not serializer.is_valid()
    assert "total_copies" in serializer.errors


@pytest.mark.django_db
def test_book_str_method(book_data):
    book = Book.objects.create(**book_data)
    expected = f"{book_data['title']} par {book_data['author']}"
    assert str(book) == expected


@pytest.mark.django_db
def test_book_ordering(book_data):
    # Create books with different timestamps
    book1 = Book.objects.create(**book_data)
    book_data["isbn"] = "9781234567891"
    book2 = Book.objects.create(**book_data)
    
    books = Book.objects.all()
    # Should be ordered by -created_at (most recent first)
    assert books[0].id == book2.id
    assert books[1].id == book1.id


@pytest.mark.django_db
def test_return_copy_beyond_total_copies(book_data):
    book = Book.objects.create(**book_data)
    book.available_copies = book.total_copies
    book.save()
    
    # Try to return when already at capacity
    result = book.return_copy()
    book.refresh_from_db()
    
    assert result is False
    assert book.available_copies == book.total_copies


@pytest.mark.django_db
def test_decrement_copies_updates_is_available_flag(book_data):
    book = Book.objects.create(**book_data)
    book.available_copies = 1
    book.save()
    
    book.decrement_copies()
    book.refresh_from_db()
    
    assert book.available_copies == 0
    assert book.is_available is False


@pytest.mark.django_db
def test_book_with_empty_cover_url(book_data):
    book_data["cover_image_url"] = ""
    book = Book.objects.create(**book_data)
    assert book.cover_image_url == ""


@pytest.mark.django_db
def test_book_with_blank_description(book_data):
    book_data["description"] = ""
    serializer = BookSerializer(data=book_data)
    # Description can be blank
    assert serializer.is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize("category", [
    "FICTION", "NON_FICTION", "SCIENCE", "TECHNOLOGY",
    "HISTORY", "BIOGRAPHY", "CHILDREN", "EDUCATION",
    "POETRY", "OTHER"
])
def test_valid_book_categories(book_data, category):
    book_data["category"] = category
    serializer = BookSerializer(data=book_data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_book_category(book_data):
    book_data["category"] = "INVALID_CATEGORY"
    serializer = BookSerializer(data=book_data)
    assert not serializer.is_valid()
    assert "category" in serializer.errors


@pytest.mark.django_db
def test_book_average_rating_precision(book_data):
    book = Book.objects.create(**book_data)
    book.average_rating = Decimal("4.75")
    book.save()
    book.refresh_from_db()
    assert book.average_rating == Decimal("4.75")


@pytest.mark.django_db
def test_book_long_isbn(book_data):
    book_data["isbn"] = "12345678901234"  # 14 chars, max is 13
    serializer = BookSerializer(data=book_data)
    assert not serializer.is_valid()
    assert "isbn" in serializer.errors


@pytest.mark.django_db
def test_availability_status_boundary_conditions(book_data):
    book = Book.objects.create(**book_data)
    
    # Test boundary at 3 copies
    book.available_copies = 3
    book.save()
    status = book.get_availability_status()
    assert status.startswith("Disponible")
    
    # Test boundary at 2 copies
    book.available_copies = 2
    book.save()
    status = book.get_availability_status()
    assert status.startswith("Peu disponible")