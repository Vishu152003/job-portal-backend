# Generated migration for chat app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        # Add interview status fields
        migrations.AddField(
            model_name='conversation',
            name='interview_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pending', 'Pending'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                    ('reschedule_requested', 'Reschedule Requested'),
                    ('completed', 'Completed'),
                ],
                default='pending',
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='conversation',
            name='interview_response_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='reschedule_reason',
            field=models.TextField(blank=True, null=True),
        ),
        # Add final selection fields
        migrations.AddField(
            model_name='conversation',
            name='final_selection_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pending', 'Pending'),
                    ('selected', 'Selected'),
                    ('rejected', 'Rejected'),
                ],
                default='pending',
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='conversation',
            name='selection_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='selection_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
