from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('application', 'Application'), ('status', 'Status'), ('message', 'Message'), ('job', 'Job'), ('interview', 'Interview'), ('system', 'System')], default='system', max_length=20)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserNotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('application_updates', models.BooleanField(default=True)),
                ('job_alerts', models.BooleanField(default=True)),
                ('message_notifications', models.BooleanField(default=True)),
                ('marketing_emails', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Notification Settings',
                'verbose_name_plural': 'User Notification Settings',
            },
        ),
    ]
