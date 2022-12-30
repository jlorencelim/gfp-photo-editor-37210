from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Photos(models.Model):
    PHOTOS_TYPE = (
        ('original', 'original'),
        ('edit', 'edit'),
        ('collage', 'collage'),
    )
    photo = models.FileField(upload_to='photos/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    photo_type = models.CharField(max_length=16, choices=PHOTOS_TYPE, default='original')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

