# Generated by Django 4.2.3 on 2023-08-05 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="user_info",
            fields=[
                (
                    "handle",
                    models.CharField(max_length=30, primary_key=True, serialize=False),
                ),
                ("rating", models.IntegerField(blank=True, null=True)),
                ("rank", models.CharField(blank=True, max_length=30, null=True)),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "db_table": "user_info",
            },
        ),
        migrations.CreateModel(
            name="user_rating",
            fields=[
                ("user_rating_id", models.AutoField(primary_key=True, serialize=False)),
                ("contest_id", models.IntegerField()),
                ("contest_name", models.CharField(max_length=255)),
                ("rank", models.IntegerField()),
                ("old_rating", models.IntegerField()),
                ("new_rating", models.IntegerField()),
                ("rating_updated_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
                (
                    "handle",
                    models.ForeignKey(
                        db_column="handle",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="query.user_info",
                    ),
                ),
            ],
            options={
                "db_table": "user_rating",
            },
        ),
    ]