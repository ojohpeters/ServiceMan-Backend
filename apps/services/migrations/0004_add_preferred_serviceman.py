# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0003_add_new_service_request_statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicerequest',
            name='preferred_serviceman',
            field=models.ForeignKey(
                blank=True,
                help_text="Client's preferred serviceman (optional)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='preferred_requests',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

