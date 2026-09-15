from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []
