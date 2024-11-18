# Generated by Django 5.1.1 on 2024-11-17 15:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0004_childactivity"),
    ]

    operations = [
        migrations.RenameField(
            model_name="childactivity",
            old_name="correct_answers",
            new_name="total_right_answers",
        ),
        migrations.RenameField(
            model_name="childactivity",
            old_name="incorrect_answers",
            new_name="total_wrong_answers",
        ),
        migrations.RemoveField(
            model_name="childactivity",
            name="average_time",
        ),
        migrations.AddField(
            model_name="childactivity",
            name="start_activity",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="childactivity",
            name="stop_activity",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="FindImageStats",
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
                (
                    "image_type",
                    models.CharField(
                        choices=[
                            ("vegetable", "Vegetable"),
                            ("fruit", "Fruit"),
                            ("animal", "Animal"),
                        ],
                        max_length=20,
                    ),
                ),
                ("right_answers", models.IntegerField(default=0)),
                ("wrong_answers", models.IntegerField(default=0)),
                (
                    "child_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.childactivity",
                    ),
                ),
            ],
            options={
                "unique_together": {("child_activity", "image_type")},
            },
        ),
        migrations.CreateModel(
            name="FindNumberStats",
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
                ("number", models.IntegerField()),
                ("right_answers", models.IntegerField(default=0)),
                ("wrong_answers", models.IntegerField(default=0)),
                (
                    "child_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.childactivity",
                    ),
                ),
            ],
            options={
                "unique_together": {("child_activity", "number")},
            },
        ),
        migrations.CreateModel(
            name="LearnWithButtonsStats",
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
                (
                    "button",
                    models.CharField(
                        choices=[("horse", "Horse"), ("cat", "Cat"), ("dog", "Dog")],
                        max_length=20,
                    ),
                ),
                ("right_answers", models.IntegerField(default=0)),
                ("wrong_answers", models.IntegerField(default=0)),
                (
                    "child_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.childactivity",
                    ),
                ),
            ],
            options={
                "unique_together": {("child_activity", "button")},
            },
        ),
        migrations.CreateModel(
            name="MatchColorStats",
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
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("red", "Red"),
                            ("yellow", "Yellow"),
                            ("green", "Green"),
                            ("blue", "Blue"),
                        ],
                        max_length=20,
                    ),
                ),
                ("right_answers", models.IntegerField(default=0)),
                ("wrong_answers", models.IntegerField(default=0)),
                (
                    "child_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.childactivity",
                    ),
                ),
            ],
            options={
                "unique_together": {("child_activity", "color")},
            },
        ),
        migrations.CreateModel(
            name="TouchBodyPartStats",
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
                (
                    "body_part",
                    models.CharField(
                        choices=[
                            ("left_hand", "Left Hand"),
                            ("right_hand", "Right Hand"),
                            ("left_bumper", "Left Bumper"),
                            ("right_bumper", "Right Bumper"),
                        ],
                        max_length=20,
                    ),
                ),
                ("right_answers", models.IntegerField(default=0)),
                ("wrong_answers", models.IntegerField(default=0)),
                (
                    "child_activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="activities.childactivity",
                    ),
                ),
            ],
            options={
                "unique_together": {("child_activity", "body_part")},
            },
        ),
    ]
