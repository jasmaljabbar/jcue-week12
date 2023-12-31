# Generated by Django 4.2.4 on 2023-11-21 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_sid', '0005_brand_image_category_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_name', models.CharField(blank=True, max_length=20, null=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')], default='fixed', max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('expire_date', models.DateTimeField()),
                ('coupon_type', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='private', max_length=10)),
                ('min_purchase_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
            options={
                'verbose_name': 'Coupon',
                'verbose_name_plural': 'Coupons',
            },
        ),
    ]
