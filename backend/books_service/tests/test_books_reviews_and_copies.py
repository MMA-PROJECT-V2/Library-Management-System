import pytest
from rest_framework.test import APIClient
from rest_framework import status
from books.models import Book, BookReview


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_borrow_book_not_found(api_client):
    resp = api_client.post('/api/books/9999/borrow/')
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_borrow_book_no_copies(api_client):
    b = Book.objects.create(
        isbn='9780000000001', title='No Copies', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=1, available_copies=0
    )

    resp = api_client.post(f'/api/books/{b.id}/borrow/')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Aucun exemplaire disponible' in str(resp.data)


@pytest.mark.django_db
def test_borrow_book_success(api_client):
    b = Book.objects.create(
        isbn='9780000000002', title='One Copy', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=1, available_copies=1
    )

    resp = api_client.post(f'/api/books/{b.id}/borrow/')
    assert resp.status_code == status.HTTP_200_OK
    b.refresh_from_db()
    assert resp.data['available_copies'] == b.available_copies


@pytest.mark.django_db
def test_return_book_not_found(api_client):
    resp = api_client.post('/api/books/9999/return/')
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_return_book_at_capacity(api_client):
    b = Book.objects.create(
        isbn='9780000000003', title='Full', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2
    )

    resp = api_client.post(f'/api/books/{b.id}/return/')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_return_book_success(api_client):
    b = Book.objects.create(
        isbn='9780000000004', title='Returnable', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=3, available_copies=1
    )

    resp = api_client.post(f'/api/books/{b.id}/return/')
    assert resp.status_code == status.HTTP_200_OK
    b.refresh_from_db()
    assert resp.data['available_copies'] == b.available_copies


@pytest.mark.django_db
def test_create_and_get_reviews(api_client):
    b = Book.objects.create(
        isbn='9780000000005', title='ReviewMe', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2
    )

    payload = {'user_id': 1, 'rating': 5, 'comment': 'Great'}
    resp = api_client.post(f'/api/books/{b.id}/reviews/create/', payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED

    get_resp = api_client.get(f'/api/books/{b.id}/reviews/')
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.data['count'] == 1


@pytest.mark.django_db
def test_create_review_invalid_rating(api_client):
    b = Book.objects.create(
        isbn='9780000000006', title='BadRating', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2
    )

    payload = {'user_id': 1, 'rating': 10}
    resp = api_client.post(f'/api/books/{b.id}/reviews/create/', payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_search_min_rating_invalid(api_client):
    resp = api_client.get('/api/search/?q=book&min_rating=notanumber')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_search_min_rating_filters(api_client):
    b1 = Book.objects.create(
        isbn='9780000000007', title='HighRated', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2, average_rating=4.5
    )
    b2 = Book.objects.create(
        isbn='9780000000008', title='LowRated', author='B', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2, average_rating=2.0
    )

    resp = api_client.get('/api/search/?q=Rated&min_rating=4')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 1


@pytest.mark.django_db
def test_partial_update_book_success(api_client):
    b = Book.objects.create(
        isbn='9780000000009', title='Partial', author='A', publisher='P',
        publication_year=2020, category='FICTION', description='', language='Français',
        pages=10, total_copies=2, available_copies=2
    )

    resp = api_client.patch(f'/api/books/partial-update/{b.id}/', {'title': 'Partially Updated'}, format='json')
    assert resp.status_code == status.HTTP_200_OK
    b.refresh_from_db()
    assert b.title == 'Partially Updated'
