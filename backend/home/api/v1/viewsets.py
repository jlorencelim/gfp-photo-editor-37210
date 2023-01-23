import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from home.api.v1.serializers import (
    SignupSerializer,
    UserSerializer, ChangePasswordSerializer, PhotosModelSerializer, FileListSerializer,
)
from home.api.v1.utils import email_users
from home.models import Photos
from home.permissions import OwnerPermission

User = get_user_model()


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    http_method_names = ["post", 'patch']
    queryset = User.objects.all()


class LoginViewSet(ViewSet):
    """Based on rest_framework.authtoken.views.ObtainAuthToken"""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({"token": token.key, "user": user_serializer.data})


class ResetPasswordViewSet(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            try:
                user = User.objects.get(email=request.data["email"])
            except User.DoesNotExist:
                return Response(
                    {"error": 'Please enter a registered email address'}, status=status.HTTP_400_BAD_REQUEST
                )

            token_generator = PasswordResetTokenGenerator()
            temp_key = token_generator.make_token(user)
            url = "{frontend_url}/auth/reset/?token={temp_key}&uid={uid}".format(
                frontend_url=settings.FRONTEND_URL,
                uid=urlsafe_base64_encode(force_bytes(user.pk)),
                temp_key=temp_key,
            )

            template = """<html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">
                    <title>Document</title>
                    <style>
                    .confirmation-button {confirmation_button}
                    .confirmation-link  {confirmation_link}
                    .domain-color{domain_color}
                    </style>
                </head>
                <body style="color: black;">
                    <div>
                    <b>Hi {username},</b>
                    <br>
                    <p>We've received your request to reset your GFP Photo Editor Password.</p>
                    <a href="{domain}" class="confirmation-link"><button class="confirmation-button" class="btn-btn-primary">RESET YOUR PASSWORD</button></a>
                    <br/><br/>
                    <span> Alternately, please copy/paste this link in your browser: </span><br/>
                    <span class="domain-color">{domain}</span>
                    <p>If you didn't make this request, please ignore this email.</b><br/><br/>
                     <b>Best Regards,</b><br/>
                     <b>GFP Photo Editor Support Team</b>
                    </div>
                    </body>

                </html>""".format(confirmation_button="""{
                background-color: #c7d104;
                width: 20em;
                height: 3em;
                border-radius: 9px;
                border: 2px solid;
                box-shadow: 5px 7px;
                }""", confirmation_link="""{
                text-decoration: None;
                color: black !important;}""",
                                  domain_color="{color: #15c;}",
                                  username=user.username, domain=url)

            email_users(
                user,
                "[GFP Photo Editor] Create New Password",
                template,
            )
            return Response(
                {"success": "Password reset e-mail has been sent."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": e.args[0]}, status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordViewSet(ViewSet):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, OwnerPermission, ]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()

            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotosViewSet(ModelViewSet):
    """
    An endpoint for changing password.
    """
    serializer_class = FileListSerializer
    permission_classes = [IsAuthenticated, OwnerPermission, ]
    queryset = Photos.objects.all()

    def get_queryset(self):
        photo_type = self.request.query_params.get('photo_type', None)
        photos = Photos.objects.all()
        if photo_type == 'original':
            photos = photos.filter(photo_type='original')
        elif photo_type == 'edit':
            photos = photos.filter(photo_type='edit')
        elif photo_type == 'collage':
            photos = photos.filter(photo_type='collage')

        return photos

    def get_serializer_class(self):
        if self.action in ['list', 'partial_update', 'retrieve']:
            return PhotosModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        photos = serializer.validated_data['photo']
        for img in photos:
            Photos.objects.create(photo=img, user=request.user, photo_type=serializer.validated_data.get('photo_type', 'original'))

        return Response(status=200)


class LogoutViewSet(ViewSet):
    def list(self, request):
        user = request.user
        user.is_login = False
        user.last_login = datetime.datetime.now()
        user.save()
        user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
