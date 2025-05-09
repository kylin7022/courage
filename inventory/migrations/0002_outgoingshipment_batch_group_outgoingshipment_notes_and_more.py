# Generated by Django 5.1.7 on 2025-04-19 12:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="outgoingshipment",
            name="batch_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="inventory.batchgroup",
                verbose_name="批次组",
            ),
        ),
        migrations.AddField(
            model_name="outgoingshipment",
            name="notes",
            field=models.TextField(blank=True, verbose_name="备注"),
        ),
        migrations.AddField(
            model_name="outgoingshipment",
            name="pin_pitch",
            field=models.CharField(blank=True, max_length=50, verbose_name="脚距"),
        ),
        migrations.AddField(
            model_name="outgoingshipment",
            name="unit_weight",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="单重(g)",
            ),
        ),
    ]
