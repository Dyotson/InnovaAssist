# Generated by Django 5.0.6 on 2024-07-10 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_alumno_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumno',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
