from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    get_gwt,
    ReviewViewSet,
    send_code,
    TitleViewSet,
    UserViewSet,
)

app_name = "api"

v1_router = DefaultRouter()
v1_router.register("categories", CategoryViewSet, basename="categories")
v1_router.register("genres", GenreViewSet, basename="genres")
v1_router.register("titles", TitleViewSet, basename="titles")
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)
v1_router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/signup/", send_code),
    path("v1/auth/token/", get_gwt),
]
