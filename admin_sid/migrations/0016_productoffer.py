# Generated by Django 4.2.4 on 2023-12-02 07:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('admin_sid', '0015_remove_product_variants_delete_variant'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')], default='fixed', max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('expire_date', models.DateTimeField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_sid.category')),
            ],
            options={
                'verbose_name': 'Product Offer',
                'verbose_name_plural': 'Product Offers',
            },
        ),
    ]
