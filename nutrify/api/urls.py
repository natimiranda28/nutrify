from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CategoryViewSet,
    CurrentProfileView,
    CurrentUserView,
    DietaryRestrictionViewSet,
    EstablishmentViewSet,
    FavoriteViewSet,
    RegisterView,
)

router = DefaultRouter()
router.register("restrictions", DietaryRestrictionViewSet, basename="restriction")
router.register("categories", CategoryViewSet, basename="category")
router.register("establishments", EstablishmentViewSet, basename="establishment")
router.register("favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="current_user"),
    path("profile/", CurrentProfileView.as_view(), name="profile"),
    path("", include(router.urls)),
]

