# Generated by Django 4.2.11 on 2024-03-17 15:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CityModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_fias', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='ClubModel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clubs.citymodel')),
            ],
        ),
        migrations.CreateModel(
            name='GenresModel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='MeetingModel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('location', models.CharField(max_length=150)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.clubmodel')),
            ],
        ),
        migrations.AddField(
            model_name='clubmodel',
            name='interests',
            field=models.ManyToManyField(to='clubs.genresmodel'),
        ),
    ]
