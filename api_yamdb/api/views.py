from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL_HOST_USER
from api.filters import TitleFilter
from api.permissions import (
    IsAuthorAdminModeratorOrReadOnly,
    IsAdminOrSuperuser,
    IsAdminOrReadOnlyPermission,
)
from api.serializers import (
    CategorySerializer,
    CodeSerializer,
    CommentSerializer,
    GenreSerializer,
    MeSerializer,
    ReadTitleSerializer,
    ReviewSerializer,
    TokenSerializer,
    UserSerializer,
    WriteTitleSerializer,
)
from reviews.models import Category, Genre, Title
from users.models import User


class ListCreateDeleteViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all()
        .order_by("-id")
        .annotate(rating=Avg("reviews__score"))
    )
    serializer_class = ReadTitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnlyPermission,)

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return ReadTitleSerializer
        return WriteTitleSerializer


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnlyPermission,)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
    permission_classes = (IsAdminOrReadOnlyPermission,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorAdminModeratorOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthorAdminModeratorOrReadOnly,
        IsAuthenticatedOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        review = get_object_or_404(
            title.reviews, id=self.kwargs.get("review_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        review = get_object_or_404(
            title.reviews, id=self.kwargs.get("review_id")
        )
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrSuperuser)
    lookup_field = "username"
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        methods=["get", "patch"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = User.objects.get(username=request.user.username)
        if request.method == "PATCH":
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = MeSerializer(user)
        return Response(serializer.data)


@api_view(["POST"])
def send_code(request):
    username = request.data.get("username")
    email = request.data.get("email")
    serializer = CodeSerializer(data=request.data)

    if User.objects.filter(username=username, email=email).exists():
        return Response(serializer.initial_data, status=status.HTTP_200_OK)

    serializer.is_valid(raise_exception=True)
    serializer.save()
    email = serializer.data.get("email", False)
    username = serializer.data.get("username", False)
    user = User.objects.get(username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        "Confirmation code",
        f"Your confirmation code: {confirmation_code}",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_gwt(request):
    username = request.data.get("username")
    confirmation_code = request.data.get("confirmation_code")
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
