# Generated by Django 4.2.4 on 2023-12-05 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_sid', '0017_product_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_offer',
            field=models.BooleanField(default=False),
        ),
    ]
