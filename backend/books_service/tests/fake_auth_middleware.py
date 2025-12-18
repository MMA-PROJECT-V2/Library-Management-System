# tests/fake_auth_middleware.py
import pytest

class DummyUser:
    is_authenticated = True
    id = 1
    role = "ADMIN"
    permissions = ["*"]

    def has_permission(self, perm):
        return True

    def has_any_permission(self, perms):
        return True

    def has_all_permissions(self, perms):
        return True


class DummyAuth:
    def authenticate(self, request):
        return (DummyUser(), None)


@pytest.fixture(autouse=True)
def patch_jwt_auth(monkeypatch):
    """
    Automatically patch JWTAuthentication for all tests.
    """
    monkeypatch.setattr("books.authentication.JWTAuthentication", DummyAuth)
