# Generated by Django 3.2.2 on 2021-10-02 08:35

import uuid

from django.db import migrations, models

import learney_web


def fill_link_click_uuids(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    LinkClickModel = apps.get_model("link_clicks", "LinkClickModel")
    for obj in LinkClickModel.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("link_clicks", "0003_rename_click_time_linkclickmodel_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="linkclickmodel",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(fill_link_click_uuids, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="linkclickmodel",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, serialize=False, editable=False, unique=True
            ),
        ),
        migrations.RemoveField("LinkClickModel", "id"),
        migrations.RenameField(model_name="linkclickmodel", old_name="uuid", new_name="id"),
        migrations.AlterField(
            model_name="linkclickmodel",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text="Unique ID for this link click",
                primary_key=True,
                serialize=False,
            ),
        ),
        migrations.AlterField(
            model_name="linkclickmodel",
            name="map_uuid",
            field=models.UUIDField(help_text="UUID of the map this link click corresponds to"),
        ),
        migrations.AddField(
            model_name="linkclickmodel",
            name="concept_id",
            field=models.CharField(
                help_text="ID of the concept clicked",
                max_length=8,
                null=True,
                validators=[learney_web.validators.validate_numeric],
            ),
        ),
        migrations.AddField(
            model_name="linkclickmodel",
            name="content_link_preview_id",
            field=models.IntegerField(
                help_text="Primary key of the ContentLinkPreview that was clicked", null=True
            ),
        ),
        migrations.AlterField(
            model_name="linkclickmodel",
            name="user_id",
            field=models.TextField(help_text="User ID of the user who clicked the link"),
        ),
        migrations.AlterField(
            model_name="linkclickmodel",
            name="session_id",
            field=models.TextField(
                blank=True, help_text="session_key of the session the link was clicked in"
            ),
        ),
    ]
