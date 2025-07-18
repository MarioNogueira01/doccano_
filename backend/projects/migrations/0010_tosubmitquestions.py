# Generated by Django 4.2.15 on 2025-04-25 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0009_perspective_perspectivegroup_perspectiveanswer_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ToSubmitQuestions",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(default="toSubmit", max_length=20)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="discrepancies", to="projects.project"
                    ),
                ),
            ],
        ),
    ]
