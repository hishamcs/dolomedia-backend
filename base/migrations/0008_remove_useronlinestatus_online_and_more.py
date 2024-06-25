# Generated by Django 4.2.9 on 2024-05-03 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_useronlinestatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useronlinestatus',
            name='online',
        ),
        migrations.AddField(
            model_name='useronlinestatus',
            name='is_online',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='useronlinestatus',
            name='connections',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
