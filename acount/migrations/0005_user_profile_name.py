# Generated by Django 4.2.4 on 2023-12-04 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acount', '0004_wallet_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_profile',
            name='name',
            field=models.CharField(default='user', max_length=50),
            preserve_default=False,
        ),
    ]
