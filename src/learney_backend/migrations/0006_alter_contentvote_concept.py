# Generated by Django 3.2.2 on 2021-06-02 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learney_backend", "0005_contentvote_user_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contentvote",
            name="concept",
            field=models.TextField(),
        ),
    ]
