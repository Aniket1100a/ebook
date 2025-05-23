# Generated by Django 5.1.4 on 2025-01-11 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_alter_cartorderitem_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AboutSection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="about_images/"),
                ),
            ],
        ),
    ]
