# Generated by Django 4.0.6 on 2022-10-20 22:16

from django.db import migrations, models
import process.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapImage',
            fields=[
                ('id', models.CharField(max_length=11, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=20)),
                ('image', models.ImageField(upload_to=process.models.user_directory_path)),
            ],
        ),
    ]
