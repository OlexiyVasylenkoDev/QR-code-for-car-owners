# Generated by Django 4.1.4 on 2022-12-16 18:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_qrcode_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_login',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
