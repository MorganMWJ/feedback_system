# Generated by Django 2.1.5 on 2019-04-02 15:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_auto_20190402_1247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={},
        ),
        migrations.AlterModelOptions(
            name='time',
            options={'ordering': ('start', 'end')},
        ),
        migrations.RemoveField(
            model_name='time',
            name='runtime',
        ),
    ]
