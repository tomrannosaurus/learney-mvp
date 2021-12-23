# Generated by Django 3.2.2 on 2021-12-22 17:33

import django.db.models.deletion
from django.db import migrations, models


def populate_content_link_field(apps, schema_editor):
    ContentLinkPreview = apps.get_model("learney_backend", "ContentLinkPreview")
    LinkClickModel = apps.get_model("link_clicks", "LinkClickModel")
    for link_click_entry in LinkClickModel.objects.all():
        if link_click_entry.content_link_preview_id is not None:
            link_click_entry.content_link_preview_foreign_key = ContentLinkPreview.objects.get(
                id=link_click_entry.content_link_preview_id
            )
            link_click_entry.save()


def populate_content_link_id_field(apps, schema_editor):
    LinkClickModel = apps.get_model("link_clicks", "LinkClickModel")
    for link_click_entry in LinkClickModel.objects.all():
        link_click_entry.content_link_preview_id = (
            link_click_entry.content_link_preview_foreign_key.id
        )
        link_click_entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ("link_clicks", "0007_ids_to_foreign_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="linkclickmodel",
            name="content_link_preview_foreign_key",
            field=models.ForeignKey(
                help_text="The ContentLinkPreview that was clicked",
                on_delete=django.db.models.deletion.CASCADE,
                to="learney_backend.contentlinkpreview",
                related_name="link_clicks",
                null=True,
            ),
        ),
        migrations.RunPython(
            populate_content_link_field, reverse_code=populate_content_link_id_field
        ),
        migrations.RemoveField(
            model_name="linkclickmodel",
            name="content_link_preview_id",
        ),
        migrations.RenameField(
            model_name="linkclickmodel",
            old_name="content_link_preview_foreign_key",
            new_name="content_link_preview",
        ),
    ]
