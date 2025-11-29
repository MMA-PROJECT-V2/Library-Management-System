from django.urls import resolve

from books import views


def test_api_books_list_url_resolves():
    match = resolve("/api/books/")

    assert match.func == views.list_books


def test_api_books_detail_url_resolves():
    match = resolve("/api/books/5/")

    assert match.func == views.get_book
    assert match.kwargs["id"] == 5


def test_api_books_create_url_resolves():
    match = resolve("/api/books/create/")

    assert match.func == views.create_book


def test_api_books_update_url_resolves():
    match = resolve("/api/books/update/9/")

    assert match.func == views.update_book
    assert match.kwargs["id"] == 9


def test_api_books_delete_url_resolves():
    match = resolve("/api/books/delete/11/")

    assert match.func == views.delete_book
    assert match.kwargs["id"] == 11


def test_api_search_url_resolves():
    match = resolve("/api/search/")

    assert match.func == views.search_books

