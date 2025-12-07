import pytest

from books.models import Book


@pytest.fixture
def sample_book(db):
    return Book.objects.create(
        isbn="9783161484100",
        title="Pytest Django Sample",
        author="Test Author",
        publisher="Test Publisher",
        publication_year=2024,
        category="FICTION",
        description="Livre utilisé pour valider les méthodes utilitaires du modèle Book.",
        cover_image_url="https://example.com/cover.png",
        language="Français",
        pages=230,
        total_copies=3,
        available_copies=3,
    )


@pytest.mark.django_db
def test_check_availability_reflects_stock(sample_book):
    assert sample_book.check_availability()
    sample_book.available_copies = 0
    sample_book.save()
    assert not sample_book.check_availability()


@pytest.mark.django_db
def test_decrement_copies_reduces_stock(sample_book):
    sample_book.available_copies = 2
    sample_book.total_copies = 2
    sample_book.times_borrowed = 0
    sample_book.save()

    assert sample_book.decrement_copies()
    sample_book.refresh_from_db()

    assert sample_book.available_copies == 1
    assert sample_book.times_borrowed == 1
    assert sample_book.is_available


@pytest.mark.django_db
def test_decrement_copies_fails_when_none_available(sample_book):
    sample_book.available_copies = 0
    sample_book.times_borrowed = 0
    sample_book.save()

    assert not sample_book.decrement_copies()
    sample_book.refresh_from_db()

    assert sample_book.times_borrowed == 0
    assert sample_book.available_copies == 0


@pytest.mark.django_db
def test_return_copy_increases_available(sample_book):
    sample_book.available_copies = 1
    sample_book.total_copies = 3
    sample_book.save()

    assert sample_book.return_copy()
    sample_book.refresh_from_db()

    assert sample_book.available_copies == 2
    assert sample_book.is_available


@pytest.mark.django_db
def test_return_copy_at_capacity(sample_book):
    sample_book.available_copies = sample_book.total_copies
    sample_book.save()

    assert not sample_book.return_copy()
    sample_book.refresh_from_db()

    assert sample_book.available_copies == sample_book.total_copies


@pytest.mark.django_db
@pytest.mark.parametrize(
    "available,expected_prefix",
    [
        (0, "Non disponible"),
        (2, "Peu disponible"),
        (5, "Disponible"),
    ],
)
def test_get_availability_status_matches_message(sample_book, available, expected_prefix):
    sample_book.available_copies = available
    sample_book.save()

    assert sample_book.get_availability_status().startswith(expected_prefix)

