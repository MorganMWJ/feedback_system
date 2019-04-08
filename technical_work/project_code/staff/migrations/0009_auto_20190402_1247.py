# Generated by Django 2.1.5 on 2019-04-02 11:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20190402_1217'),
    ]

    operations = [
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(null=True)),
                ('runtime', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('start',),
            },
        ),
        migrations.RemoveField(
            model_name='endtime',
            name='session',
        ),
        migrations.RemoveField(
            model_name='starttime',
            name='session',
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'ordering': ('time__start',)},
        ),
        migrations.DeleteModel(
            name='EndTime',
        ),
        migrations.DeleteModel(
            name='StartTime',
        ),
        migrations.AddField(
            model_name='time',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.Session'),
        ),
    ]