# Generated by Django 2.1.5 on 2019-03-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='notes',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='is_running',
            field=models.BooleanField(default=False),
        ),
    ]
