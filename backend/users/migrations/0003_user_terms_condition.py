# Generated by Django 2.2.26 on 2023-01-23 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20221230_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='terms_condition',
            field=models.BooleanField(default=False),
        ),
    ]