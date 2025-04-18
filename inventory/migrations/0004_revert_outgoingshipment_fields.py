# Generated manually to revert migration 0003

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_outgoingshipment_batch_group_outgoingshipment_notes_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingshipment',
            name='batch_group',
        ),
        migrations.RemoveField(
            model_name='outgoingshipment',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='outgoingshipment',
            name='shipping_date',
        ),
    ] 