# Generated by Django 5.1 on 2024-09-17 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0016_ordering_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_description',
            field=models.TextField(max_length=255),
        ),
    ]
