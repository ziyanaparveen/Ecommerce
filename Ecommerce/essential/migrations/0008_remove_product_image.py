# Generated by Django 4.2.6 on 2023-10-27 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('essential', '0007_product_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
    ]
