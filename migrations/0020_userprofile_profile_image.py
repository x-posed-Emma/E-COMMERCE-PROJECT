# Generated by Django 5.1 on 2024-09-24 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0019_remove_userprofile_favorites_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='user_profile/'),
        ),
    ]
