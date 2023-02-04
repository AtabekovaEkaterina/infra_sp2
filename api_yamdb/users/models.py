from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизируем модель User."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    ROLES = (
        (USER, "Пользователь"),
        (MODERATOR, "Модератор"),
        (ADMIN, "Администратор"),
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name="Электронная почта",
    )

    bio = models.TextField(
        verbose_name="Биография",
        blank=True,
    )

    role = models.CharField(
        max_length=16,
        blank=True,
        choices=ROLES,
        default=USER,
        verbose_name="Роль",
    )

    password = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Пароль",
    )

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN
