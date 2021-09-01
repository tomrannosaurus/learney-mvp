import uuid

from django.db import models


class KnowledgeMapModel(models.Model):
    unique_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, help_text="Unique identifier for each knowledge map"
    )
    version = models.IntegerField(help_text="Version number of the map", default=0)

    author_user_id = models.TextField(help_text="User ID of user who created this map")
    url_extension = models.TextField(unique=True, help_text="URL extension of the map")

    s3_bucket_name = models.TextField(
        help_text="Name of the S3 bucket that the knowledge map json is stored in"
    )
    s3_key = models.TextField(help_text="Key of the knowledge map json in S3")

    last_updated = models.DateTimeField(auto_now=True)
