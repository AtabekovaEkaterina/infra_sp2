from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_year
from users.models import User


class Category(models.Model):
    name = models.TextField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField(validators=[validate_year])
    description = models.TextField(null=True, blank=True)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категории",
    )


class Review(models.Model):
    text = models.TextField()
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            )
        ]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    pub_date = models.DateTimeField(
        "Дата добавления", auto_now_add=True, db_index=True
    )
