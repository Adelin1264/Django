# Generated by Django 5.1.1 on 2025-01-15 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplicatie', '0008_bluray_imagine_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bluray',
            name='imagine_url',
        ),
        migrations.AddField(
            model_name='bluray',
            name='imagine',
            field=models.ImageField(blank=True, null=True, upload_to='blurays/'),
        ),
    ]
