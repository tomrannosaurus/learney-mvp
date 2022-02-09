# Generated by Django 3.2.2 on 2022-01-27 12:12
import json

from django.db import migrations


def add_concepts_from_questions_map(apps, schema_editor):
    Concept = apps.get_model("knowledge_maps", "Concept")
    KnowledgeMapModel = apps.get_model("knowledge_maps", "KnowledgeMapModel")
    map_json = json.loads(
        KnowledgeMapModel.objects.get(url_extension="questionsmap").retrieve_map()
    )

    # Add all the concepts
    for node in map_json["nodes"]:
        node_data = node["data"]
        if node_data["nodetype"] == "concept":
            Concept.objects.create(
                name=node_data["name"],
                cytoscape_id=node_data["id"],
            )

    # Add all the edges
    for edge in map_json["edges"]:
        edge_data = edge["data"]
        source_concept = Concept.objects.get(cytoscape_id=edge_data["source"])
        target_concept = Concept.objects.get(cytoscape_id=edge_data["target"])
        target_concept.direct_prerequisites.add(source_concept)


def delete_all_concepts(apps, schema_editor):
    Concept = apps.get_model("knowledge_maps", "Concept")
    for concept in Concept.objects.all():
        concept.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("knowledge_maps", "0006_concept"),
    ]

    operations = [
        migrations.RunPython(add_concepts_from_questions_map, reverse_code=delete_all_concepts)
    ]
