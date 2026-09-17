"""Authentication service layer, kept separate from views so it's testable without HTTP."""

from django.contrib.auth import authenticate

from accounts.models import User


def authenticate_user(email: str, password: str) -> User | None:
    return authenticate(email=email, password=password)
