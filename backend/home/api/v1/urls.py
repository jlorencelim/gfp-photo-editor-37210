from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

from home.api.v1.viewsets import (
    SignupViewSet,
    LoginViewSet, ResetPasswordViewSet,
    ChangePasswordViewSet, PhotosViewSet, LogoutViewSet
)

router = DefaultRouter()
router.register("signup", SignupViewSet, basename="signup")
router.register("login", LoginViewSet, basename="login")
router.register(
    "reset/password", ResetPasswordViewSet, basename="reset-password"
)
router.register("change_password", ChangePasswordViewSet, basename="change_password")
router.register("photos", PhotosViewSet, basename="photos")
router.register("logout", LogoutViewSet, basename="logout")

urlpatterns = [
    path("", include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
