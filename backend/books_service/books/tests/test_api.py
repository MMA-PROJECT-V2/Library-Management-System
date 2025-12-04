import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from books.models import Book

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_list_books(api_client):
    Book.objects.create(title="A", author="A1", isbn="1", available=True)
    Book.objects.create(title="B", author="B1", isbn="2", available=False)

    # adjust URL name/path if your routes differ (e.g. 'books-list' or '/api/books/')
    url = reverse('book-list') if 'book-list' in [u.name for u in api_client.handler._urls.urlpatterns] else '/api/books/'
    resp = api_client.get(url)
    assert resp.status_code in (status.HTTP_200_OK, status.HTTP_302_FOUND)

@pytest.mark.django_db
def test_create_book(api_client):
    url = reverse('book-list') if 'book-list' in [u.name for u in api_client.handler._urls.urlpatterns] else '/api/books/'
    payload = {"title": "New", "author": "X", "isbn": "999", "available": True}
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

@pytest.mark.django_db
def test_retrieve_update_delete_book(api_client):
    book = Book.objects.create(title="C", author="C1", isbn="3", available=True)
    # adjust URL name/path as necessary
    detail_url = reverse('book-detail', args=[book.pk]) if 'book-detail' in [u.name for u in api_client.handler._urls.urlpatterns] else f'/api/books/{book.pk}/'
    r = api_client.get(detail_url)
    assert r.status_code in (status.HTTP_200_OK,)

    update_resp = api_client.patch(detail_url, {"title": "C Updated"}, format='json')
    assert update_resp.status_code in (status.HTTP_200_OK,)

    delete_resp = api_client.delete(detail_url)
    assert delete_resp.status_code in (status.HTTP_204_NO_CONTENT, status.HTTP_200_OK)