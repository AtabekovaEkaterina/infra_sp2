from django.core.validators import RegexValidator
from rest_framework import serializers

from api.validators import validate_year
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                "Поле name не может быть больше 256 символов"
            )
        return value

    def validate_slug(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                "Поле slug не может быть больше 50 символов"
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class ReadTitleSerializer(TitleSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
            "rating",
        )


class WriteTitleSerializer(TitleSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    def validate(self, data):
        request = self.context["request"]
        author_id = request.user
        title_id = self.context["view"].kwargs.get("title_id")
        if (
            request.method == "POST"
            and Review.objects.filter(
                author=author_id, title=title_id
            ).exists()
        ):
            raise serializers.ValidationError(
                "Можно оставить только один отзыв на произведение"
            )
        return data

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError("username 'me' - не допустимо")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Недопустимые символы",
            )
        ],
    )
    confirmation_code = serializers.CharField(required=True)
