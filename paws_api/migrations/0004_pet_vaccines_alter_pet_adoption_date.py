# Generated by Django 5.1.7 on 2025-04-03 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paws_api', '0003_family_codefam'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='vaccines',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='pet',
            name='adoption_date',
            field=models.DateField(null=True),
        ),
    ]
