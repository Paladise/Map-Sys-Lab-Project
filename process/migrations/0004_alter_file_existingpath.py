# Generated by Django 4.1.1 on 2022-12-17 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('process', '0003_alter_mapimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='existingPath',
            field=models.CharField(max_length=100),
        ),
    ]