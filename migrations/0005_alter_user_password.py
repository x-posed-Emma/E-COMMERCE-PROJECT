# Generated by Django 5.1 on 2024-09-05 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_product_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=50),
        ),
    ]